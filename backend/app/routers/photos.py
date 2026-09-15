from datetime import datetime
from hashlib import sha256
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import get_current_user, write_audit
from ..auth.scope import require_work_scope
from ..models.photo import PhotoVerification
from ..models.user import User, UserRole
from ..models.work import Work
from ..services.photo_verification import verify_photo

router = APIRouter(prefix="/photos", tags=["Photo Verification"])

OFFICIAL_ROLES = {
    UserRole.ADMIN, UserRole.MINISTRY, UserRole.STATE_OFFICIAL,
    UserRole.DISTRICT_OFFICIAL, UserRole.MP,
}


@router.get("/{work_id}")
async def list_photos(
	work_id: str,
	request: Request,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	work = db.query(Work).filter(Work.work_id == work_id).first()
	if not work:
		raise HTTPException(status_code=404, detail="Work not found")
	require_work_scope(work, current_user)

	photos = db.query(PhotoVerification).filter(PhotoVerification.work_id == work_id).order_by(PhotoVerification.upload_date.desc()).all()
	write_audit(db, current_user, "PHOTOS_LIST_VIEWED", request, resource_type="work", resource_id=work_id)
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
	request: Request,
	work_id: str = Form(...),
	capture_date: datetime | None = Form(None),
	photo: UploadFile = File(...),
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
):
	"""Hash and record a progress photo, rejecting exact duplicates."""
	if current_user.role not in OFFICIAL_ROLES:
		raise HTTPException(status_code=403, detail="Only officials may submit photo verifications")

	work = db.query(Work).filter(Work.work_id == work_id).first()
	if not work:
		raise HTTPException(status_code=404, detail="Work not found")
	require_work_scope(work, current_user)

	content = await photo.read()
	if not content:
		raise HTTPException(status_code=400, detail="Photo is empty")

	photo_hash = sha256(content).hexdigest()
	duplicate = db.query(PhotoVerification).filter(PhotoVerification.photo_hash == photo_hash).first()
	if duplicate:
		write_audit(
			db, current_user, "PHOTO_VERIFY_DUPLICATE", request,
			resource_type="work", resource_id=work_id, status_value="FAILURE",
		)
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

	write_audit(
		db, current_user, "PHOTO_VERIFIED", request,
		resource_type="work", resource_id=work_id,
	)

	return {"photo_id": str(record.id), "work_id": work_id, "status": record.is_verified, "verification_score": record.verification_score}