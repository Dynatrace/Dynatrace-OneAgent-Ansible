import logging
import threading
from collections.abc import Generator
from http import HTTPStatus

from flask import Blueprint, Flask, Response, request, send_file
from tests.constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    SERVER_CERTIFICATE_FILE_NAME,
    SERVER_PRIVATE_KEY_FILE_NAME,
    WORK_INSTALLERS_DIR_PATH,
    WORK_SERVER_DIR_PATH,
)
from tests.deployment.deployment_operations import get_installers
from tests.deployment.ssl_certificate_generator import (
    SSLCertificateGenerator,
    SSLCertificateInfo,
)
from werkzeug.serving import make_server

app = Flask(__name__)
installer_bp = Blueprint("installer", __name__)
certificate_bp = Blueprint("certificate", __name__)

TransferResult = tuple[str, HTTPStatus] | Response


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
    cert_file = WORK_INSTALLERS_DIR_PATH / INSTALLER_CERTIFICATE_FILE_NAME
    if not cert_file.exists():
        logging.warning("%s not found", cert_file)
        return f"{cert_file} not found", HTTPStatus.NOT_FOUND
    return send_file(cert_file)


@installer_bp.route("/<system>/default/latest")
def get_latest_agent(system: str) -> TransferResult:
    return get_installer(system, request.args["arch"], "latest")


@installer_bp.route("/<system>/default/version/<version>")
def get_agent_in_version(system: str, version: str) -> TransferResult:
    return get_installer(system, request.args["arch"], version)


def run_server(ip_address: str, port: int) -> Generator[None, None, None]:
    logging.info("Starting server on %s:%d", ip_address, port)

    ssl_info = SSLCertificateInfo(
        country_name="US",
        state_name="California",
        locality_name="San Francisco",
        organization_name="Dynatrace",
        common_name=ip_address,
    )
    ssl_generator = SSLCertificateGenerator(ssl_info, validity_days=365)
    ssl_generator.generate_and_save(
        WORK_SERVER_DIR_PATH / SERVER_PRIVATE_KEY_FILE_NAME,
        WORK_SERVER_DIR_PATH / SERVER_CERTIFICATE_FILE_NAME,
    )

    ssl_context = (
        f"{WORK_SERVER_DIR_PATH / SERVER_CERTIFICATE_FILE_NAME}",
        f"{WORK_SERVER_DIR_PATH / SERVER_PRIVATE_KEY_FILE_NAME}",
    )
    app.register_blueprint(installer_bp, url_prefix="/api/v1/deployment/installer/agent")
    app.register_blueprint(certificate_bp)

    server = make_server(ip_address, port, app, ssl_context=ssl_context)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    logging.info("Server thread started on %s:%d", ip_address, port)

    yield

    logging.info("Shutting down the server")
    server.shutdown()
    server_thread.join()
