#!/bin/sh

readonly TEST_DIR='test_dir'
readonly LOG_DIR="${TEST_DIR}/logs"
readonly SERVER_LOG_FILE="${LOG_DIR}/server.log"

prepareInstallerFiles() {
	local baseName='Dynatrace-OneAgent-Linux'
	local srcInstallerDir="resources/installers"
	local destInstallerDir="${TEST_DIR}/installers"

	printf 'Preparing installer files...\n'
	mkdir -p "${destInstallerDir}"
	cp "${srcInstallerDir}/${baseName}.sh" "${destInstallerDir}/${baseName}-1.0.0.sh"
	sed -i "s/##VERSION##/1.0.0/g" "${destInstallerDir}/${baseName}-1.0.0.sh"
	cp "${srcInstallerDir}/${baseName}.sh" "${destInstallerDir}/${baseName}-2.0.0.sh"
	sed -i "s/##VERSION##/2.0.0/g" "${destInstallerDir}/${baseName}-2.0.0.sh"
}

runServer() {
	local serverScript='scripts/server/server.py'

	printf 'Running server...\n'
	mkdir -p "${LOG_DIR}"
	PYTHONPATH='scripts' python "${serverScript}" >>"${SERVER_LOG_FILE}" 2>&1 &
}

runTests() {
	printf 'Running tests...\n'
}

main() {
	rm -rf "${TEST_DIR}"
	prepareInstallerFiles
	runServer
	runTests
}

##################
## SCRIPT START ##
##################
main "${@}"