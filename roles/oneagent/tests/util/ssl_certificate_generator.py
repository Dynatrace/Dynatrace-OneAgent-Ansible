import ipaddress
import logging
import uuid
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class SSLCertificateGenerator:
    def __init__(self, country_name, state_name, locality_name, organization_name, common_name, validity_days=365):
        self.country_name = country_name
        self.state_name = state_name
        self.locality_name = locality_name
        self.organization_name = organization_name
        self.common_name = common_name
        self.validity_days = validity_days

    def _generate_key_pair(self) -> (rsa.RSAPrivateKey, rsa.RSAPublicKey):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        return private_key, private_key.public_key()

    def _generate_certificate(self, private_key, public_key) -> x509.Certificate:
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, self.country_name),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state_name),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality_name),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization_name),
                    x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
                ]
            )
        )
        builder = builder.issuer_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, self.country_name),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state_name),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality_name),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization_name),
                    x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
                ]
            )
        )
        builder = builder.not_valid_before(datetime.utcnow())
        builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=self.validity_days))
        builder = builder.serial_number(int(uuid.uuid4()))
        builder = builder.public_key(public_key)

        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(self.common_name))]),
            critical=False,
        )
        return builder.sign(
            private_key=private_key,
            algorithm=hashes.SHA256(),
        )

    def _save_private_key(self, filename, private_key) -> None:
        with open(filename, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

    def _save_certificate(self, filename, certificate) -> None:
        with open(filename, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

    def generate_and_save(self, private_key_path, certificate_path) -> None:
        private_key, public_key = self._generate_key_pair()
        self._save_private_key(private_key_path, private_key)
        self._save_certificate(certificate_path, self._generate_certificate(private_key, public_key))
        logging.info("Self-signed certificate generated and saved successfully")
