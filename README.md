# pythonbird

A lightweight, zero-dependency Python library for interacting with local Mozilla Thunderbird profiles, mailboxes, and configurations on Linux.

## Features

- **Profile Auto-Detection:** Automatically spots standard and Snap-based Thunderbird installations.
- **Preference Parsing:** Extracts configured accounts and data from prefs.js.
- **Local Mail Reader:** Reads, locks, and extracts emails securely from local Mbox structures (e.g., Inbox).
- **Address Book Access:** Fetches contacts directly from native SQLite databases (abook.sqlite).
- **Natively Controlled:** Launches native Thunderbird compose windows pre-filled with custom text or attachments via CLI.

## Documentation

For a comprehensive breakdown of every class, method, argument, and advanced error handling practice, please refer to the full [Developer Guide and API Reference](GUIDE.md).

## Installation

This library requires Python 3.8+ and is built specifically for Linux environments.

### Using Poetry (Recommended)

```bash
poetry add pythonbird
```

### Using pip

```bash
pip install pythonbird
```

## Quick Start

Here is how you can use pythonbird in your project:

```python
from pythonbird import ThunderbirdLinux, ThunderbirdMail, ThunderbirdContacts

# 1. Initialize and connect to the active profile
tb = ThunderbirdLinux()
print(f"Active Profile Folder: {tb.profile_dir.name}")
print(f"Configured Accounts: {tb.get_mail_accounts()}")

# 2. Read local emails from the Inbox folder
mail_manager = ThunderbirdMail(tb)
emails = mail_manager.get_local_inbox_messages()
print(f"Total local emails found: {len(emails)}")

for msg in emails[:3]:  # Print headers of the first 3 emails
    print(f"From: {msg['from']} | Subject: {msg['subject']}")

# 3. Extract your address book contacts
contact_manager = ThunderbirdContacts(tb)
contacts = contact_manager.get_all_contacts()
print(f"Total contacts stored: {len(contacts)}")

# 4. Trigger Thunderbird UI to draft a new email
tb.open_compose_window(
    to="developer@example.com",
    subject="Automated Draft via Python",
    body="Hello! This message window was triggered programmatically."
)
```

## Running Tests

We use pytest for automated test suites. The tests run inside an isolated mock environment, ensuring that your local personal emails and settings remain completely untouched.

To install development dependencies and run the tests:

```bash
poetry install
poetry run pytest
```

## Project Architecture

```text
pythonbird/
├── pythonbird/
│   ├── __init__.py      # Clean top-level package imports
│   ├── core.py          # Profile auto-detection, preference extraction & CLI control
│   ├── mail.py          # Reads local storage folders (Mbox structure)
│   └── contacts.py      # SQLite reader for abook.sqlite (Address Book)
├── tests/
│   └── test_core.py     # Automated mock environment tests
├── README.md            # Library documentation
└── pyproject.toml       # Build system definition & project metadata
```

## Safety and Concurrency

When Thunderbird is active, it locks database and mail storage files to prevent edits. To protect your files, pythonbird performs read-only interactions and applies standard file locking mechanisms (mailbox.mbox().lock()) during file execution. This ensures zero risk of database or mail folder corruption.

## License

This project is licensed under the [MIT License](LICENSE).
