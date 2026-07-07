"""Environment sanity checks: confirms the CI/dev runtime is Linux, Ubuntu,
and the expected Python version, plus a few pytest-marker demonstrations."""
import platform
import sys
import pytest


def test_os_is_linux():
    """Confirm the runtime OS is Linux."""
    assert platform.system() == "Linux"


def test_distro_is_ubuntu():
    """Confirm the runtime distro is Ubuntu."""
    with open("/etc/os-release", encoding="utf-8") as f:
        assert "ubuntu" in f.read().lower()


def test_python_version():
    """Confirm the runtime Python version is 3.14."""
    assert sys.version_info[:2] == (3, 14)


@pytest.mark.xfail(reason="demonstrating an expected failure")
def test_expected_failure():
    """Deliberately-failing test demonstrating xfail behavior."""
    assert 1 == 2  # pylint: disable=comparison-of-constants


@pytest.mark.skip(reason="feature not built yet")
def test_skipped_feature():
    """Deliberately-skipped test demonstrating skip behavior."""
    assert True is False  # pylint: disable=comparison-of-constants


@pytest.mark.parametrize("n,squared", [(2, 4), (3, 9), (4, 16)])
def test_squares(n, squared):
    """Demonstrate parametrize behavior across multiple input signatures."""
    assert n * n == squared
