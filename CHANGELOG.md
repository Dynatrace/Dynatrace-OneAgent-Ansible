## **1.3.0**&emsp;<sub><sup>2026-08-20 (cea983df0453dc5ea7e672542ffa0db3219828c2...d4352e4738187f7737f6b216ed3f40116ed2c428)</sup></sub>

### Bug Fixes

- Fix ansible\-linter error: variables names from within roles should use oneagent\_ as a prefix\. \(register: installer\_stat\) \(\#119\) (cea983df0453dc5ea7e672542ffa0db3219828c2)
- Removed redundant files from the collection \(\#120\) (b42de0aabc22612e35029174770b4fdf735616f7)
- Fix pylint error: logging\-too\-few\-args: Not enough arguments for… \(\#121\) (17c3e5d05a6af8639763f48fb5ddb3932f6ab499)
- place installer in root\-owned private tmp directory\. The installer is now placed inside a randomly named root\-owned 0700 subdirectory, making the path unpredictable (f376165411ad71d98076d7c27012e4453e64fd76)

<br>

## **1.2.5**&emsp;<sub><sup>2025-11-21 (f903c8f0f8156ebfeb82a7c1638e5d94d085e47b...ab81691af95dae02a1f7cfbf644404b40edcaac6)</sup></sub>

### Features

- add retry mechanism for OneAgent installer download (79658309a21dff5f54d3758131643485a0623ac6)
- Remove unintended config feature from the collection (5cb5d4e8f19b78ac717485b0a708e6d1b9b2bb56)
- Add check for latest OneAgent version before download (3c7670931c7d274f365e16f1ee837acaea324009)

### Bug Fixes

- fix broken conditionals \(\#105\) (7cd6ee37f063e34740678455a8fcadee9cf16f54)

<br>

## **1.2.4**&emsp;<sub><sup>2025-04-30 (47a986a76f99ea3ffd5290c5d51585660050157f..2056802937c9096f48fe3a15ac31874bd7b97ffa)</sup></sub>

### Features

- Added parameter `oneagent_no_log` controlling Ansible no_log attribute

<br>

## **1.2.3**&emsp;<sub><sup>2025-02-03 (08bc7b499a6c74e1d5eca815eaa47e380de6ba57..08bc7b499a6c74e1d5eca815eaa47e380de6ba57)</sup></sub>

### Bug Fixes

- Fixed issue with skipping CA certificate transfer task

<br>

## **1.2.2**&emsp;<sub><sup>2025-10-1 (2effbf1975f46a4669c246722069a827ad0ffec3..1f71c5b165a870b0f11ccc51e06c5e1ddc2fe84f)</sup></sub>

### Bug Fixes

- Fixed linters issues

<br>

## **1.2.1**&emsp;<sub><sup>2024-12-19 (a412454a7c1356a53b07c56d6f14b412684b1d79..df9f55f7ac08d58741eb87ae4b2ecba55bc23fad)</sup></sub>

### Bug Fixes

- Fixed problem with installer signature verification on AIX

<br>

## **1.2.0**&emsp;<sub><sup>2024-11-29 (6f16a253a8ec3630817a2facfb590fbb0b3a473f..7f3bc5f0cc799a88c48d078f23deb2adfd6f3fc9)</sup></sub>

### Features

- Added parameter `--restart-service` parameter, once OneAgent configuration is performed
- Added parameter `oneagent_verify_signature` controlling signature verification step
- Removed `oneagent_validate_certs` parameter
- Added ability for downloading installer's certificate if the certificate is not embedded in the collection

### Bug Fixes

- Fixed problem with `Invalid version string` during collection install
- Fixed problem with `dt-root.cert.pem` not being copied to the target host

<br>