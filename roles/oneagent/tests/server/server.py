import argparse
import logging
from http import HTTPStatus
from typing import Any

from flask import Blueprint, Flask, request, send_file
from util.common_utils import get_installers
from util.constants.common_constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    INSTALLERS_DIRECTORY,
    SERVER_CERTIFICATE_FILE_NAME,
    SERVER_DIRECTORY,
    SERVER_PRIVATE_KEY_FILE_NAME,
)
from util.ssl_certificate_generator import SSLCertificateGenerator

app = Flask(__name__)
installer_bp = Blueprint("installer", __name__)
certificate_bp = Blueprint("certificate", __name__)

TransferResult = Any | tuple[str, HTTPStatus]


def get_installer(system: str, arch: str, version: str) -> TransferResult:
    logging.info("Getting installer for system %s_%s in %s version", system, arch, version)

    installers = get_installers(system, arch, version, True)

    if len(installers) > 0:
        logging.info("Serving installer %s", installers[-1])
        return send_file(installers[-1])

    msg = f"Installer for system {system} in {version} version was not found"
    logging.warning(msg)
    return msg, HTTPStatus.NOT_FOUND


@certificate_bp.route(f"/{INSTALLER_CERTIFICATE_FILE_NAME}")
def get_ca_certificate() -> TransferResult:
    cert_file = INSTALLERS_DIRECTORY / INSTALLER_CERTIFICATE_FILE_NAME
    if not cert_file.exists():
        logging.warning("%s not found", cert_file)
        return f"{cert_file} not found", HTTPStatus.NOT_FOUND
    return send_file(cert_file)


@installer_bp.route("/<system>/default/latest")
def get_latest_agent(system) -> TransferResult:
    return get_installer(system, request.args["arch"], "latest")


@installer_bp.route("/<system>/default/version/<version>")
def get_agent_in_version(system, version) -> TransferResult:
    return get_installer(system, request.args["arch"], version)


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s [server] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(description="Run Flask server.")
    parser.add_argument(
        "--ip-address",
        type=str,
        dest="ip_address",
        help="IP address of the host to run the server on",
    )
    parser.add_argument("--port", type=int, help="Port to run the server on")
    args = parser.parse_args()

    generator = SSLCertificateGenerator(
        country_name="US",
        state_name="California",
        locality_name="San Francisco",
        organization_name="Dynatrace",
        common_name=args.ip_address,
    )
    generator.generate_and_save(
        f"{SERVER_DIRECTORY /SERVER_PRIVATE_KEY_FILE_NAME}",
        f"{SERVER_DIRECTORY / SERVER_CERTIFICATE_FILE_NAME}",
    )

    context = (
        f"{SERVER_DIRECTORY / SERVER_CERTIFICATE_FILE_NAME}",
        f"{SERVER_DIRECTORY / SERVER_PRIVATE_KEY_FILE_NAME}",
    )
    app.register_blueprint(installer_bp, url_prefix="/api/v1/deployment/installer/agent")
    app.register_blueprint(certificate_bp)
    app.run(host="0.0.0.0", debug=True, ssl_context=context, port=args.port)
