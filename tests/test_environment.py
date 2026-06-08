import platform
import sys
import pytest


def test_os_is_linux():
    assert platform.system() == "Linux"


def test_distro_is_ubuntu():
    with open("/etc/os-release", encoding="utf-8") as f:
        assert "ubuntu" in f.read().lower()


def test_python_version():
    assert sys.version_info[:2] == (3, 14)


@pytest.mark.xfail(reason="demonstrating an expected failure")
def test_expected_failure():
    assert 1 == 2


@pytest.mark.skip(reason="feature not built yet")
def test_skipped_feature():
    assert True is False


@pytest.mark.parametrize("n,squared", [(2, 4), (3, 9), (4, 16)])
def test_squares(n, squared):
    assert n * n == squared
