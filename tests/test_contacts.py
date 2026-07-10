import sqlite3

from pythonbird.contacts import ThunderbirdContacts
from pythonbird.core import ThunderbirdLinux


def test_reads_contacts(tmp_path):
    profile_dir = tmp_path / "test.default-release"
    profile_dir.mkdir()

    (profile_dir / "prefs.js").write_text("", encoding="utf-8")

    db_path = profile_dir / "abook.sqlite"

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE cards (
                displayName TEXT,
                primaryEmail TEXT
            )
            """
        )

        connection.execute(
            """
            INSERT INTO cards (displayName, primaryEmail)
            VALUES (?, ?)
            """,
            ("Test User", "test@example.com"),
        )

    tb = ThunderbirdLinux(
        profile_dir=profile_dir,
        command=["thunderbird"],
    )

    contacts = ThunderbirdContacts(tb).get_all_contacts()

    assert contacts == [
        {
            "name": "Test User",
            "email": "test@example.com",
        }
    ]
