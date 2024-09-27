import logging
from http import HTTPStatus
from pathlib import Path
from typing import Any

from flask import Blueprint, Flask, request, send_file

from util.common_utils import get_installers
from util.constants.common_constants import HOST_SERVER_PORT, INSTALLERS_DIRECTORY, SIGNATURE_FILE_NAME

APPLICATION_ROOT = "/api/v1/deployment/installer/agent"

app = Flask(__name__)
bp = Blueprint("server", __name__)

TransferResult = Any | tuple[str, HTTPStatus]


def get_installer(system: str, arch: str, version: str) -> TransferResult:
    logging.info(f"Getting installer for system {system}_{arch} in {version} version")

    installers = get_installers(system, arch, version, True)

    if len(installers) > 0:
        logging.info("Serving installer %s", installers[-1])
        return send_file(installers[-1])

    msg = f"Installer for system {system} in {version} version was not found"
    logging.warning(msg)
    return msg, HTTPStatus.NOT_FOUND


@bp.route(f"/{SIGNATURE_FILE_NAME}")
def get_ca_certificate() -> TransferResult:
    cert_file = INSTALLERS_DIRECTORY / SIGNATURE_FILE_NAME
    if not cert_file.exists():
        return f"{cert_file} not found", HTTPStatus.NOT_FOUND
    return send_file(cert_file)


@bp.route("/<system>/default/latest")
def get_latest_agent(system) -> TransferResult:
    return get_installer(system, request.args["arch"], "latest")


@bp.route("/<system>/default/version/<version>")
def get_agent_in_version(system, version) -> TransferResult:
    return get_installer(system, request.args["arch"], version)


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s [server] %(levelname)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO
    )
    server_path = Path("scripts") / "server"
    context = (f"{server_path / 'server.pem'}", f"{server_path / 'server.key'}")
    app.register_blueprint(bp, url_prefix=APPLICATION_ROOT)
    app.run(host="0.0.0.0", debug=True, ssl_context=context, port=HOST_SERVER_PORT)


if __name__ == "__main__":
    main()
