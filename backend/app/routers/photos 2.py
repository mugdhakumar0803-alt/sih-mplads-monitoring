from datetime import datetime
from hashlib import sha256
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.photo import PhotoVerification
from ..models.work import Work

router = APIRouter(prefix="/photos", tags=["Photo Verification"])


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
	"""Hash and record a progress photo, rejecting exact duplicates."""
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
	try:
		from PIL import Image, ExifTags
		image = Image.open(BytesIO(content))
		exif = image.getexif()
		metadata["exif"] = {ExifTags.TAGS.get(key, str(key)): value for key, value in exif.items()}
	except Exception:
		metadata["exif"] = {}

	record = PhotoVerification(
		work_id=work_id,
		photo_url=f"upload://{photo_hash}",
		photo_hash=photo_hash,
		capture_date=capture_date or datetime.utcnow(),
		is_verified="verified",
		verification_score=1.0,
		verification_method="hash_and_metadata",
		photo_metadata=metadata,
	)
	db.add(record)
	db.commit()
	db.refresh(record)
	return {"photo_id": str(record.id), "work_id": work_id, "status": record.is_verified, "verification_score": record.verification_score}
