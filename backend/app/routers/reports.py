from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth.dependencies import get_current_user, write_audit
from ..database import get_db
from ..models.user import User, UserRole
from ..models.report_signature import ReportSignature
from ..signing.digital_signature import DigitalSignature
from ..config import settings


router = APIRouter(prefix="/reports", tags=["Reports & Signatures"])


class ReportPayload(BaseModel):
    report_id: str = Field(min_length=1, max_length=100)
    report: dict


class VerifyPayload(BaseModel):
    report_id: str
    report: dict


def signing_keys():
    return DigitalSignature.load_or_create_keys(
        settings.report_private_key_path,
        settings.report_public_key_path,
    )


@router.post("/sign")
async def sign_report(
    payload: ReportPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {
        UserRole.ADMIN, UserRole.MINISTRY, UserRole.STATE,
        UserRole.DISTRICT, UserRole.MP,
    }:
        raise HTTPException(status_code=403, detail="Only officials may sign reports")

    existing = db.query(ReportSignature).filter(
        ReportSignature.report_id == payload.report_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Report is already signed")

    private_key, _ = signing_keys()
    report_hash = DigitalSignature.sha256(payload.report)
    signature = DigitalSignature.sign_report(payload.report, private_key)

    record = ReportSignature(
        report_id=payload.report_id,
        report_hash=report_hash,
        signature=signature,
        algorithm=DigitalSignature.ALGORITHM,
        signed_by=str(current_user.id),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    write_audit(db, current_user, "REPORT_SIGNED", request,
                resource_type="report", resource_id=payload.report_id)

    return {
        "report_id": payload.report_id,
        "report_hash": report_hash,
        "signature": signature,
        "algorithm": record.algorithm,
        "signed_by": str(current_user.id),
        "signed_at": record.signed_at,
    }


@router.post("/verify")
async def verify_report(
    payload: VerifyPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(ReportSignature).filter(
        ReportSignature.report_id == payload.report_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="No signature found for report")

    _, public_key = signing_keys()
    current_hash = DigitalSignature.sha256(payload.report)
    signature_valid = DigitalSignature.verify_signature(
        payload.report, record.signature, public_key
    )
    hash_valid = current_hash == record.report_hash
    valid = signature_valid and hash_valid

    write_audit(
        db, current_user,
        "REPORT_SIGNATURE_VERIFIED" if valid else "REPORT_SIGNATURE_VERIFICATION_FAILED",
        request,
        resource_type="report",
        resource_id=payload.report_id,
        status_value="SUCCESS" if valid else "FAILURE",
        details={"hash_valid": hash_valid, "signature_valid": signature_valid},
    )

    return {
        "report_id": payload.report_id,
        "valid": valid,
        "hash_valid": hash_valid,
        "signature_valid": signature_valid,
        "algorithm": record.algorithm,
        "signed_by": record.signed_by,
        "signed_at": record.signed_at,
    }
