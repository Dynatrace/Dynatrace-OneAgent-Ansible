import ipaddress
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


@dataclass
class SSLCertificateInfo:
    country_name: str
    state_name: str
    locality_name: str
    organization_name: str
    common_name: str


class SSLCertificateGenerator:
    def __init__(self, cert_info: SSLCertificateInfo, validity_days: int = 365):
        self.cert_info: SSLCertificateInfo = cert_info
        self.validity_days: int = validity_days

    def _generate_key_pair(self) -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        return private_key, private_key.public_key()

    def _generate_certificate(self, private_key: rsa.RSAPrivateKey, public_key: rsa.RSAPublicKey) -> x509.Certificate:
        x509_name = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, self.cert_info.country_name),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.cert_info.state_name),
                x509.NameAttribute(NameOID.LOCALITY_NAME, self.cert_info.locality_name),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.cert_info.organization_name),
                x509.NameAttribute(NameOID.COMMON_NAME, self.cert_info.common_name),
            ]
        )

        builder = (
            x509.CertificateBuilder()
            .subject_name(x509_name)
            .issuer_name(x509_name)
            .not_valid_before(datetime.now(timezone.utc))
            .not_valid_after(datetime.now(timezone.utc) + timedelta(days=self.validity_days))
            .serial_number(int(uuid.uuid4()))
            .public_key(public_key)
            .add_extension(
                x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(self.cert_info.common_name))]),
                critical=False,
            )
        )

        return builder.sign(
            private_key=private_key,
            algorithm=hashes.SHA256(),
        )

    def _save_private_key(self, filename: Path, private_key: rsa.RSAPrivateKey) -> None:
        with open(filename, "wb") as f:
            _unused = f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

    def _save_certificate(self, filename: Path, certificate: x509.Certificate) -> None:
        with open(filename, "wb") as f:
            _unused = f.write(certificate.public_bytes(serialization.Encoding.PEM))

    def generate_and_save(self, private_key_path: Path, certificate_path: Path) -> None:
        logging.info("Generating self-signed certificate and key pair")
        private_key, public_key = self._generate_key_pair()
        self._save_private_key(private_key_path, private_key)
        self._save_certificate(certificate_path, self._generate_certificate(private_key, public_key))
