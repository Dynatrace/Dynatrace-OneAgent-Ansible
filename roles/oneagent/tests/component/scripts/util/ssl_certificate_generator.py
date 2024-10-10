from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
import uuid
import logging

class SSLCertificateGenerator:
    def __init__(self, country_name, state_name, locality_name, organization_name, common_name, validity_days=365):
        self.country_name = country_name
        self.state_name = state_name
        self.locality_name = locality_name
        self.organization_name = organization_name
        self.common_name = common_name
        self.validity_days = validity_days

    def _generate_private_key(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        return self.private_key

    def _generate_public_key(self):
        self.public_key = self.private_key.public_key()
        return self.public_key

    def _generate_certificate(self):
        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
        ]))
        builder = builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, self.country_name),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, self.state_name),
            x509.NameAttribute(NameOID.LOCALITY_NAME, self.locality_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, self.organization_name),
            x509.NameAttribute(NameOID.COMMON_NAME, self.common_name),
        ]))
        builder = builder.not_valid_before(datetime.utcnow())
        builder = builder.not_valid_after(datetime.utcnow() + timedelta(days=self.validity_days))
        builder = builder.serial_number(int(uuid.uuid4()))
        builder = builder.public_key(self.public_key)
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        )
        self.certificate = builder.sign(
            private_key=self.private_key,
            algorithm=hashes.SHA256(),
        )
        return self.certificate

    def _save_private_key(self, filename):
        with open(filename, "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

    def _save_certificate(self, filename):
        with open(filename, "wb") as f:
            f.write(self.certificate.public_bytes(serialization.Encoding.PEM))

    def generate_and_save(self, private_key_path, certificate_path):
        self._generate_private_key()
        self._generate_public_key()
        self._generate_certificate()
        self._save_private_key(private_key_path)
        self._save_certificate(certificate_path)
        logging.info("Self-signed certificate generated and saved successfully")
