from unittest.mock import patch

import pytest

from pythonbird.core import ThunderbirdLinux


@pytest.fixture
def profile_dir(tmp_path):
    profile = tmp_path / "test.default-release"
    profile.mkdir()

    prefs_path = profile / "prefs.js"
    prefs_path.write_text("", encoding="utf-8")

    return profile


def test_compose_does_not_use_shell(profile_dir):
    tb = ThunderbirdLinux(
        profile_dir=profile_dir,
        command=["thunderbird"],
    )

    dangerous_subject = 'Test"; touch /tmp/pythonbird-test; echo "'

    with patch("pythonbird.core.subprocess.Popen") as popen_mock:
        tb.open_compose_window(
            to="user@example.com",
            subject=dangerous_subject,
            body="Message body",
        )

    popen_mock.assert_called_once()

    args, kwargs = popen_mock.call_args
    command = args[0]

    assert isinstance(command, list)
    assert command[0] == "thunderbird"
    assert command[1] == "-compose"
    assert dangerous_subject in command[2]

    assert "shell" not in kwargs
