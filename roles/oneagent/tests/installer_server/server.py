import logging
from http import HTTPStatus
import threading
from typing import Any
from threading import Event

from constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    SERVER_CERTIFICATE_FILE_NAME,
    SERVER_PRIVATE_KEY_FILE_NAME,
    WORK_INSTALLERS_DIR_PATH,
    WORK_SERVER_DIR_PATH,
)
from deployment.deployment_operations import get_installers
from deployment.ssl_certificate_generator import SSLCertificateGenerator
from flask import Blueprint, Flask, request, send_file
from werkzeug.serving import make_server

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
    cert_file = WORK_INSTALLERS_DIR_PATH / INSTALLER_CERTIFICATE_FILE_NAME
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


def run_server(ip_address: str, port: int, log_file_path: str, stop_event: Event) -> None:
    logging.basicConfig(
        format=f"%(asctime)s [{__name__}] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
        handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
    )

    logging.info("Starting server on %s:%d", ip_address, port)

    generator = SSLCertificateGenerator(
        country_name="US",
        state_name="California",
        locality_name="San Francisco",
        organization_name="Dynatrace",
        common_name=ip_address,
    )
    generator.generate_and_save(
        f"{WORK_SERVER_DIR_PATH / SERVER_PRIVATE_KEY_FILE_NAME}",
        f"{WORK_SERVER_DIR_PATH / SERVER_CERTIFICATE_FILE_NAME}",
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

    stop_event.wait()

    logging.info("Received stop event, shutting down the server")
    server.shutdown()
    server_thread.join()
