from pythonbird.core import ThunderbirdLinux
from pythonbird.mail import ThunderbirdMail


def test_decodes_mime_subject_and_windows_1251_body(tmp_path):
    profile_dir = tmp_path / "test.default-release"
    local_folders = profile_dir / "Mail" / "Local Folders"
    local_folders.mkdir(parents=True)

    (profile_dir / "prefs.js").write_text("", encoding="utf-8")

    inbox_path = local_folders / "Inbox"

    email_headers = (
        b"From sender@example.com Fri Jul 10 12:00:00 2026\n"
        b"From: =?UTF-8?B?0KLQtdGB0YLQvtCy0YvQuSDCeNGC0L/RgNCw0LLQuNGC0LXQu9GM?="
        b" <sender@example.com>\n"
        b"Subject: =?UTF-8?B?0KLQtdGB0YLQvtCy0LDRjyDRgtC10LzQsA==?=\n"
        b"MIME-Version: 1.0\n"
        b"Content-Type: text/plain; charset=windows-1251\n"
        b"Content-Transfer-Encoding: 8bit\n"
        b"\n"
    )

    body = "Привет из тестового письма!".encode("windows-1251")

    inbox_path.write_bytes(email_headers + body + b"\n\n")

    tb = ThunderbirdLinux(
        profile_dir=profile_dir,
        command=["thunderbird"],
    )

    mail = ThunderbirdMail(tb)
    messages = mail.get_local_inbox_messages()

    assert len(messages) == 1
    assert messages[0]["subject"] == "Тестовая тема"
    assert "Привет из тестового письма!" in messages[0]["body"]
