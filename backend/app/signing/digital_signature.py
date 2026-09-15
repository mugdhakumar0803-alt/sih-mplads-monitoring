import base64
import hashlib
import json
from pathlib import Path
from datetime import datetime
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class DigitalSignature:
    ALGORITHM = "RSA-3072-PSS-SHA256"

    @staticmethod
    def canonical_bytes(report_data: dict) -> bytes:
        return json.dumps(report_data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")

    @staticmethod
    def sha256(report_data: dict) -> str:
        return hashlib.sha256(DigitalSignature.canonical_bytes(report_data)).hexdigest()

    @staticmethod
    def generate_key_pair():
        return rsa.generate_private_key(public_exponent=65537, key_size=3072)

    @staticmethod
    def sign_report(report_data: dict, private_key) -> str:
        signature = private_key.sign(
            DigitalSignature.canonical_bytes(report_data),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("ascii")

    @staticmethod
    def verify_signature(report_data: dict, signature: str, public_key) -> bool:
        try:
            public_key.verify(
                base64.b64decode(signature, validate=True),
                DigitalSignature.canonical_bytes(report_data),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False

    @staticmethod
    def load_or_create_keys(private_path: str, public_path: str):
        private_file, public_file = Path(private_path), Path(public_path)
        private_file.parent.mkdir(parents=True, exist_ok=True)
        public_file.parent.mkdir(parents=True, exist_ok=True)

        if private_file.exists() and public_file.exists():
            return (
                serialization.load_pem_private_key(private_file.read_bytes(), password=None),
                serialization.load_pem_public_key(public_file.read_bytes()),
            )

        private_key = DigitalSignature.generate_key_pair()
        public_key = private_key.public_key()
        private_file.write_bytes(private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        ))
        public_file.write_bytes(public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        return private_key, public_key

    @staticmethod
    def create_signed_report(report_data: dict, private_key) -> dict:
        return {
            "report": report_data,
            "report_hash": DigitalSignature.sha256(report_data),
            "signature": DigitalSignature.sign_report(report_data, private_key),
            "signed_at": datetime.utcnow().isoformat(),
            "algorithm": DigitalSignature.ALGORITHM,
        }
