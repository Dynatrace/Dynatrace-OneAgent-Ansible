from dataclasses import dataclass
from enum import Enum


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


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
        return str(self.value).split("_", maxsplit=1)[0]

    @staticmethod
    def from_str(param: str) -> "DeploymentPlatform":
        try:
            return DeploymentPlatform[param.upper()]
        except KeyError:
            raise ValueError(f"Invalid option passed: {param}") from KeyError

    @staticmethod
    def from_system_and_arch(system: str, arch: str) -> "DeploymentPlatform":
        return DeploymentPlatform.from_str(f"{system}_{arch}")


DeploymentResult = list[CommandResult]
PlatformCollection = dict[DeploymentPlatform, list[str]]
