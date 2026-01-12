import logging
import subprocess
from pathlib import Path

import requests
from constants import (
    INSTALLER_CERTIFICATE_FILE_NAME,
    INSTALLER_PRIVATE_KEY_FILE_NAME,
    INSTALLERS_DIR_PATH,
    WORK_INSTALLERS_DIR_PATH,
    InstallerVersion,
)
from deployment.deployment_platform import DeploymentPlatform, PlatformCollection
from deployment.ssl_certificate_generator import (
    SSLCertificateGenerator,
    SSLCertificateInfo,
)


def get_file_content(path: Path) -> list[str]:
    with path.open("r") as f:
        return f.readlines()


def replace_tag(source: list[str], old: str, new: str) -> list[str]:
    return [line.replace(old, new) for line in source]


def sign_installer(installer: list[str]) -> list[str]:
    cmd = [
        "openssl",
        "cms",
        "-sign",
        "-signer",
        f"{WORK_INSTALLERS_DIR_PATH / INSTALLER_CERTIFICATE_FILE_NAME}",
        "-inkey",
        f"{WORK_INSTALLERS_DIR_PATH / INSTALLER_PRIVATE_KEY_FILE_NAME}",
    ]

    proc = subprocess.run(
        cmd,
        input=f"{''.join(installer)}",
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode != 0:
        logging.error("Failed to sign installer: %s", proc.stdout)
        return []

    signed_installer = proc.stdout.splitlines()
    delimiter = next(l for l in signed_installer if l.startswith("----"))
    index = signed_installer.index(delimiter)
    signed_installer = signed_installer[index + 1 :]

    custom_delimiter = "----SIGNED-INSTALLER"

    return [
        f"{l}\n" if not l.startswith(delimiter) else f"{l.replace(delimiter, custom_delimiter)}\n"
        for l in signed_installer
    ]


def generate_installers() -> bool:
    uninstall_template = get_file_content(INSTALLERS_DIR_PATH / "uninstall.sh")
    uninstall_code = replace_tag(uninstall_template, "$", r"\$")

    oneagentctl_template = get_file_content(INSTALLERS_DIR_PATH / "oneagentctl.sh")
    oneagentctl_code = replace_tag(oneagentctl_template, "$", r"\$")

    installer_partial_name = "Dynatrace-OneAgent-Linux"
    installer_template = get_file_content(INSTALLERS_DIR_PATH / f"{installer_partial_name}.sh")
    installer_template = replace_tag(installer_template, "##UNINSTALL_CODE##", "".join(uninstall_code))
    installer_template = replace_tag(installer_template, "##ONEAGENTCTL_CODE##", "".join(oneagentctl_code))

    ssl_info = SSLCertificateInfo(
        country_name="US",
        state_name="California",
        locality_name="San Francisco",
        organization_name="Dynatrace",
        common_name="127.0.0.1",
    )
    ssl_generator = SSLCertificateGenerator(ssl_info, validity_days=365)

    ssl_generator.generate_and_save(
        WORK_INSTALLERS_DIR_PATH / INSTALLER_PRIVATE_KEY_FILE_NAME,
        WORK_INSTALLERS_DIR_PATH / INSTALLER_CERTIFICATE_FILE_NAME,
    )

    # REMOVE INSTALLER VERSION
    for version in InstallerVersion:
        installer_code = replace_tag(installer_template, "##VERSION##", version.value)
        installer_code = sign_installer(installer_code)
        if not installer_code:
            return False
        with open(WORK_INSTALLERS_DIR_PATH / f"{installer_partial_name}-{version.value}.sh", "w") as f:
            f.writelines(installer_code)

    return True


def get_installers_versions_from_tenant(tenant: str, tenant_token: str, system_family: str) -> list[str]:
    url = f"{tenant}/api/v1/deployment/installer/agent/versions/{system_family}/default"
    headers = {"accept": "application/json", "Authorization": f"Api-Token {tenant_token}"}

    resp = requests.get(url, headers=headers)

    try:
        versions = resp.json()["availableVersions"]
        if len(versions) < 2:
            logging.error("List of available installers is too short: %s", versions)
        else:
            return [versions[0], versions[-1]]
    except KeyError:
        logging.error("Failed to get list of installer versions: %s", resp.content)
    return []


def download_and_save(path: Path, url: str, headers: dict[str, str]) -> bool:
    resp = requests.get(url, headers=headers)

    if not resp.ok:
        logging.error("Failed to download file %s: %s", path, resp.text)
        return False

    with path.open("wb") as f:
        _unused = f.write(resp.content)
    return True


def download_signature(url: str) -> bool:
    path = WORK_INSTALLERS_DIR_PATH / INSTALLER_CERTIFICATE_FILE_NAME
    return download_and_save(path, url, {})


def download_installer(tenant: str, tenant_token: str, version: str, platform: DeploymentPlatform) -> bool:
    family = platform.family()
    url = f"{tenant}/api/v1/deployment/installer/agent/{family}/default/version/{version}"
    headers = {"accept": "application/octet-stream", "Authorization": f"Api-Token {tenant_token}"}

    ext = "exe" if family == "windows" else "sh"
    path = WORK_INSTALLERS_DIR_PATH / f"Dynatrace-OneAgent-{family}_{platform.arch()}-{version}.{ext}"

    return download_and_save(path, url, headers)


def download_installers(tenant: str, tenant_token: str, platforms: PlatformCollection) -> bool:
    for platform in platforms:
        versions = get_installers_versions_from_tenant(tenant, tenant_token, platform.family())
        if not versions:
            return False
        for version in versions:
            if not download_installer(tenant, tenant_token, version, platform):
                return False
    return True
