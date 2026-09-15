import base64
import hashlib
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import (
    padding,
    rsa,
)


class DigitalSignature:

    ALGORITHM = "RSA-3072-PSS-SHA256"

    @staticmethod
    def canonical_bytes(
        report_data: dict,
    ) -> bytes:

        return json.dumps(
            report_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        ).encode("utf-8")

    @staticmethod
    def sha256(report_data: dict) -> str:

        return hashlib.sha256(
            DigitalSignature.canonical_bytes(
                report_data
            )
        ).hexdigest()

    @staticmethod
    def generate_key_pair():

        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=3072,
        )

    @staticmethod
    def sign_report(
        report_data: dict,
        private_key,
    ) -> str:

        signature = private_key.sign(
            DigitalSignature.canonical_bytes(
                report_data
            ),
            padding.PSS(
                mgf=padding.MGF1(
                    hashes.SHA256()
                ),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        return base64.b64encode(
            signature
        ).decode("ascii")

    @staticmethod
    def verify_signature(
        report_data: dict,
        signature: str,
        public_key,
    ) -> bool:

        try:
            public_key.verify(
                base64.b64decode(
                    signature,
                    validate=True,
                ),
                DigitalSignature.canonical_bytes(
                    report_data
                ),
                padding.PSS(
                    mgf=padding.MGF1(
                        hashes.SHA256()
                    ),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            return True

        except (
            InvalidSignature,
            ValueError,
            TypeError,
        ):
            return False

    @staticmethod
    def load_keys(
        private_path: str,
        public_path: str,
    ):

        private_file = Path(private_path)
        public_file = Path(public_path)

        if not private_file.exists():
            raise RuntimeError(
                "Report signing private key is missing"
            )

        if not public_file.exists():
            raise RuntimeError(
                "Report signing public key is missing"
            )

        private_key = (
            serialization
            .load_pem_private_key(
                private_file.read_bytes(),
                password=None,
            )
        )

        public_key = (
            serialization
            .load_pem_public_key(
                public_file.read_bytes()
            )
        )

        return private_key, public_key