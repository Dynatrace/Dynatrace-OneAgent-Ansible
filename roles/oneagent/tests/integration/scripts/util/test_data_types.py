from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class TechType(Enum):
    ANSIBLE = "Ansible"

    def __str__(self) -> str:
        return str(self.name)

    @staticmethod
    def from_str(param: str) -> type:
        try:
            return TechType[param]
        except KeyError:
            raise ValueError(f"Invalid option passed: {param}") from KeyError


class DeploymentPlatform(Enum):
    AIX_PPC = "aix_ppc"
    LINUX_ARM = "linux_arm"
    LINUX_PPCLE = "linux_ppcle"
    LINUX_S390 = "linux_s390"
    LINUX_X86 = "linux_x86"
    WINDOWS_X86 = "windows_x86"

    def __str__(self) -> str:
        return str(self.name)

    def family(self) -> str:
        return "windows" if self == DeploymentPlatform.WINDOWS_X86 else "unix"

    def arch(self) -> str:
        return str(self.value).split("_")[1]

    def system(self) -> str:
        return str(self.value).split("_")[0]

    @staticmethod
    def from_str(param: str):
        try:
            return DeploymentPlatform[param.upper()]
        except KeyError:
            raise ValueError(f"Invalid option passed: {param}") from KeyError

    @staticmethod
    def from_system_and_arch(system: str, arch: str):
        return DeploymentPlatform.from_str(f"{system}_{arch}")


DeploymentResult = List[CommandResult]
PlatformCollection = Dict[DeploymentPlatform, List[str]]
