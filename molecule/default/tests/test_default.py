import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_nginx_user(host):

    os = host.system_info.distribution
    if os == 'redhat':
        user = host.user('dtuser')
        assert user.exists
        assert user.shell == '/sbin/nologin'
        assert user.home == '/var/cache/dtuser'
        assert user.group == 'dtuser'


def test_oneagent_running_and_enabled(host):
    oneagent = host.service("oneagent")
    assert oneagent.is_running
    assert oneagent.is_enabled


def test_oneagent_listening_port(host):
    socket = host.socket('tcp://127.0.0.1:50000')

    assert socket.is_listening


@pytest.mark.parametrize('file, content', [
  ("/opt/dynatrace/oneagent/agent/agent.state", "RUNNING")
])
def test_files(host, file, content):
    file = host.file(file)

    assert file.exists
    assert file.contains(content)
