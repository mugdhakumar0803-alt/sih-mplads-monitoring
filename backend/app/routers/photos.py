from datetime import datetime
from hashlib import sha256
from io import BytesIO
from math import radians, sin, cos, sqrt, atan2

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.photo import PhotoVerification
from ..models.work import Work

router = APIRouter(prefix="/photos", tags=["Photo Verification"])

MAX_ALLOWED_DISTANCE_METERS = 150  # tune this — GPS on phones isn't perfectly precise


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _extract_gps_from_exif(exif_dict: dict) -> tuple[float, float] | None:
    """
    EXIF GPS data is stored in a nested, awkward format (degrees/minutes/
    seconds as fractions). This converts it to plain decimal lat/lon.
    Returns None if the photo has no GPS data at all — which is common
    for screenshots, downloaded images, or phones with location off.
    """
    gps_info = exif_dict.get("GPSInfo")
    if not gps_info:
        return None

    try:
        def to_decimal(dms, ref):
            degrees, minutes, seconds = dms
            decimal = degrees + minutes / 60 + seconds / 3600
            if ref in ("S", "W"):
                decimal = -decimal
            return decimal

        lat = to_decimal(gps_info[2], gps_info[1])
        lon = to_decimal(gps_info[4], gps_info[3])
        return lat, lon
    except (KeyError, IndexError, TypeError, ZeroDivisionError):
        return None


@router.get("/{work_id}")
async def list_photos(work_id: str, db: Session = Depends(get_db)):
    photos = db.query(PhotoVerification).filter(PhotoVerification.work_id == work_id).order_by(PhotoVerification.upload_date.desc()).all()
    return {
        "photos": [
            {
                "photo_id": str(photo.id),
                "work_id": photo.work_id,
                "status": photo.is_verified,
                "verification_score": photo.verification_score,
                "capture_date": photo.capture_date,
                "photo_url": photo.photo_url,  # frontend needs this to actually SHOW the image
                "rejection_reason": photo.photo_metadata.get("rejection_reason") if photo.photo_metadata else None,
            }
            for photo in photos
        ]
    }


@router.post("/verify")
async def verify_photo(
    work_id: str = Form(...),
    capture_date: datetime | None = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    REAL verification now — a photo only passes if its embedded GPS
    location is genuinely close to the work's registered location.
    No GPS data, or GPS too far away, now correctly REJECTS the photo
    instead of blindly marking it verified.
    """
    work = db.query(Work).filter(Work.work_id == work_id).first()
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    content = await photo.read()
    if not content:
        raise HTTPException(status_code=400, detail="Photo is empty")

    photo_hash = sha256(content).hexdigest()
    duplicate = db.query(PhotoVerification).filter(PhotoVerification.photo_hash == photo_hash).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="Duplicate photo already submitted")

    metadata = {"filename": photo.filename, "content_type": photo.content_type}
    gps_coords = None
    try:
        from PIL import Image, ExifTags
        image = Image.open(BytesIO(content))
        exif = image.getexif()
        exif_dict = {ExifTags.TAGS.get(key, str(key)): value for key, value in exif.items()}

        # GPS data lives in a separate IFD block, not the flat exif dict
        gps_ifd = exif.get_ifd(0x8825) if hasattr(exif, "get_ifd") else {}
        if gps_ifd:
            exif_dict["GPSInfo"] = gps_ifd
        metadata["exif"] = exif_dict
        gps_coords = _extract_gps_from_exif(exif_dict)
    except Exception:
        metadata["exif"] = {}

    # --- THE ACTUAL FIX: check GPS instead of always passing ---
    if gps_coords is None:
        is_verified = "rejected"
        verification_score = 0.0
        metadata["rejection_reason"] = "No GPS location data found in this photo"
    else:
        photo_lat, photo_lon = gps_coords
        work_lat = getattr(work, "latitude", None)
        work_lon = getattr(work, "longitude", None)

        if work_lat is None or work_lon is None:
            # Honest edge case: if the WORK itself has no registered
            # coordinates yet, we can't check distance — flag it clearly
            # rather than pretending we verified something we didn't.
            is_verified = "unverifiable"
            verification_score = 0.0
            metadata["rejection_reason"] = "This work has no registered GPS location to check against"
        else:
            distance_m = _haversine_distance_m(photo_lat, photo_lon, work_lat, work_lon)
            metadata["distance_from_registered_location_m"] = round(distance_m, 1)

            if distance_m <= MAX_ALLOWED_DISTANCE_METERS:
                is_verified = "verified"
                verification_score = round(max(0.0, 1.0 - (distance_m / MAX_ALLOWED_DISTANCE_METERS)), 3)
            else:
                is_verified = "rejected"
                verification_score = 0.0
                metadata["rejection_reason"] = (
                    f"Photo location is {distance_m:.0f}m from the registered work site "
                    f"(max allowed: {MAX_ALLOWED_DISTANCE_METERS}m)"
                )

    record = PhotoVerification(
        work_id=work_id,
        photo_url=f"upload://{photo_hash}",
        photo_hash=photo_hash,
        capture_date=capture_date or datetime.utcnow(),
        is_verified=is_verified,
        verification_score=verification_score,
        verification_method="gps_distance_check",
        photo_metadata=metadata,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "photo_id": str(record.id),
        "work_id": work_id,
        "status": record.is_verified,
        "verification_score": record.verification_score,
        "rejection_reason": metadata.get("rejection_reason"),
    }