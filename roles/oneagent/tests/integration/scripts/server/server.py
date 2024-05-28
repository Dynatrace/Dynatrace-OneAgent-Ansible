import logging
from http import HTTPStatus
from pathlib import Path
from typing import Any, Tuple, Union

from flask import Blueprint, Flask, request, send_file

from util.common_utils import get_installers
from util.constants.common_constants import HOST_SERVER_PORT

APPLICATION_ROOT = "/api/v1/deployment/installer/agent"

app = Flask(__name__)
bp = Blueprint("server", __name__)

TransferResult = Union[Any, Tuple[str, HTTPStatus]]


def get_installer(system: str, arch: str, version: str) -> TransferResult:
    logging.info(f"Getting installer for system {system}_{arch} in {version} version")

    installers = get_installers(system, arch, version, True)

    if len(installers) > 0:
        logging.info("Serving installer %s", installers[-1])
        return send_file(installers[-1])

    msg = f"Installer for system {system} in {version} version was not found"
    logging.warning(msg)
    return msg, HTTPStatus.NOT_FOUND


@bp.route("/<system>/default/latest")
def get_latest_agent(system):
    return get_installer(system, request.args["arch"], "latest")


@bp.route("/<system>/default/version/<version>")
def get_agent_in_version(system, version):
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
