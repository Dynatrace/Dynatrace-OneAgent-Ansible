import base64
from pathlib import Path

from command.command_result import CommandResult
from command.command_wrapper import CommandWrapper
from command.windows.windows_command_executor import WindowsCommandExecutor
from typing_extensions import override


class WindowsCommandWrapper(CommandWrapper):
    def __init__(self, user: str, password: str):
        self.executor: WindowsCommandExecutor = WindowsCommandExecutor(user, password)

    @override
    def get_file_content(self, address: str, file: Path) -> CommandResult:
        return self.executor.execute(address, "type", str(file))

    def _run_powershell(self, address: str, script: str) -> CommandResult:
        # Encoding the script avoids quoting issues when passing it through cmd
        encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
        return self.executor.execute(
            address, "powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded
        )

    @staticmethod
    def _quote(value: object) -> str:
        return "'" + str(value).replace("'", "''") + "'"

    @override
    def file_exists(self, address: str, file: Path) -> CommandResult:
        # Unlike cmd's "if exist", Test-Path resolves wildcards in any path component
        return self._run_powershell(address, f"if (Test-Path -Path {self._quote(file)}) {{ exit 0 }} else {{ exit 1 }}")

    def remove_items(self, address: str, pattern: Path) -> CommandResult:
        return self._run_powershell(
            address, f"Remove-Item -Path {self._quote(pattern)} -Recurse -Force -ErrorAction SilentlyContinue; exit 0"
        )

    def check_private_directories(self, address: str, pattern: Path) -> CommandResult:
        # Exits with 0 only if at least one directory matches the pattern and, for each of them and everything
        # inside, no principal other than SYSTEM and Administrators is allowed any access and the owner (who can
        # always rewrite the DACL) is trusted. Each violation is reported on a separate stdout line.
        script = f"""
            $ErrorActionPreference = 'Stop'
            $allowedSids = @('S-1-5-18', 'S-1-5-32-544')  # NT AUTHORITY\\SYSTEM, BUILTIN\\Administrators
            $trustedOwners = $allowedSids + [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
            $sidType = [System.Security.Principal.SecurityIdentifier]
            $directories = @(Get-Item -Path {self._quote(pattern)} -Force | Where-Object {{ $_.PSIsContainer }})
            if ($directories.Count -eq 0) {{ Write-Output 'No directory matches {pattern}'; exit 1 }}
            $violations = @()
            foreach ($directory in $directories) {{
                if (-not (Get-Acl -LiteralPath $directory.FullName).AreAccessRulesProtected) {{
                    $violations += "$($directory.FullName): inherits permissions from its parent"
                }}
                foreach ($item in @($directory) + @(Get-ChildItem -LiteralPath $directory.FullName -Recurse -Force)) {{
                    $acl = Get-Acl -LiteralPath $item.FullName
                    $owner = $acl.GetOwner($sidType).Value
                    if ($trustedOwners -notcontains $owner) {{ $violations += "$($item.FullName): owned by $owner" }}
                    foreach ($rule in $acl.GetAccessRules($true, $true, $sidType)) {{
                        $sid = $rule.IdentityReference.Value
                        if ($rule.AccessControlType -eq 'Allow' -and $allowedSids -notcontains $sid) {{
                            $violations += "$($item.FullName): $($rule.FileSystemRights) allowed for $sid"
                        }}
                    }}
                }}
            }}
            if ($violations.Count -gt 0) {{ $violations | Write-Output; exit 1 }}
            exit 0
        """
        return self._run_powershell(address, script)

    def create_lookalike_signed_executable(self, address: str, root_subject: str, signer_subject: str) -> CommandResult:
        # Builds an executable signed with a code signing certificate whose subject matches the genuine publisher,
        # issued by a freshly generated (thus untrusted) root, and prints the signed file in base64.
        # A system binary can't be used: those are catalog-signed, which Authenticode cmdlets report instead.
        # The certificates and their keys are removed from the host before returning.
        script = f"""
            $ErrorActionPreference = 'Stop'
            $store = 'Cert:\\CurrentUser\\My'
            $certificates = @()
            $name = 'lookalike-' + [System.Guid]::NewGuid().ToString('N') + '.exe'
            $path = Join-Path -Path $env:TEMP -ChildPath $name
            try {{
                $root = New-SelfSignedCertificate -CertStoreLocation $store -Subject {self._quote(root_subject)} `
                    -KeyUsage CertSign, CRLSign, DigitalSignature `
                    -TextExtension @('2.5.29.19={{critical}}{{text}}ca=1') `
                    -NotAfter (Get-Date).AddYears(30)
                $certificates += $root
                $signer = New-SelfSignedCertificate -CertStoreLocation $store -Subject {self._quote(signer_subject)} `
                    -Type CodeSigningCert -Signer $root
                $certificates += $signer
                Add-Type -TypeDefinition 'public static class Program {{ public static int Main() {{ return 1; }} }}' `
                    -OutputAssembly $path -OutputType ConsoleApplication
                $result = Set-AuthenticodeSignature -LiteralPath $path -Certificate $signer -HashAlgorithm SHA256
                if ($result.SignerCertificate.Thumbprint -ne $signer.Thumbprint) {{
                    throw "Failed to sign '$path': $($result.StatusMessage)"
                }}
                [System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes($path))
            }} finally {{
                foreach ($certificate in $certificates) {{
                    $item = "$store\\$($certificate.Thumbprint)"
                    Remove-Item -LiteralPath $item -DeleteKey -ErrorAction SilentlyContinue
                }}
                Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
            }}
        """
        return self._run_powershell(address, script)

    @override
    def directory_exists(self, address: str, directory: Path) -> CommandResult:
        return self.executor.execute(address, f'if exist "{directory}\\*" (exit 0) else (exit 1)')

    def _run_directory_creation_command(self, address: str, directory: Path) -> CommandResult:
        result = CommandResult(0, "", "")
        if self.directory_exists(address, directory).returncode == 1:
            result = self.executor.execute(address, "md", str(directory))

        return result

    @override
    def create_directory(self, address: str, directory: Path) -> CommandResult:
        for parent in list(directory.parents)[::-1][1::]:
            result = self._run_directory_creation_command(address, parent)
            if result.returncode != 0:
                return result
        return self._run_directory_creation_command(address, directory)

    @override
    def run_command(self, address: str, command: str, *args: str) -> CommandResult:
        return self.executor.execute(address, f'"{command}"', *args)
