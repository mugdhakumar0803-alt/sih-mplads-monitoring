# Digital signature utilities
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import json
from datetime import datetime


class DigitalSignature:
    """Digital signature utilities for report signing and verification."""
    
    @staticmethod
    def generate_key_pair():
        """Generate RSA key pair for signing."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        return private_key
    
    @staticmethod
    def sign_report(
        report_data: dict,
        private_key: rsa.RSAPrivateKey,
    ) -> str:
        """Sign a report with digital signature."""
        # Convert report data to JSON string
        report_json = json.dumps(report_data, sort_keys=True, default=str)
        
        # Sign the data
        signature = private_key.sign(
            report_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode()
    
    @staticmethod
    def verify_signature(
        report_data: dict,
        signature: str,
        public_key: rsa.RSAPublicKey,
    ) -> bool:
        """Verify a report signature."""
        try:
            # Convert report data to JSON string
            report_json = json.dumps(report_data, sort_keys=True, default=str)
            
            # Decode signature from base64
            signature_bytes = base64.b64decode(signature)
            
            # Verify the signature
            public_key.verify(
                signature_bytes,
                report_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def create_signed_report(
        report_data: dict,
        private_key: rsa.RSAPrivateKey,
    ) -> dict:
        """Create a report with embedded signature."""
        signature = DigitalSignature.sign_report(report_data, private_key)
        
        return {
            "report": report_data,
            "signature": signature,
            "signed_at": datetime.utcnow().isoformat(),
            "algorithm": "RSA-2048-SHA256",
        }
    
    @staticmethod
    def export_public_key(private_key: rsa.RSAPrivateKey) -> str:
        """Export public key in PEM format."""
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode()
    
    @staticmethod
    def import_public_key(pem_str: str) -> rsa.RSAPublicKey:
        """Import public key from PEM format."""
        pem_bytes = pem_str.encode()
        return serialization.load_pem_public_key(
            pem_bytes,
            backend=default_backend()
        )
