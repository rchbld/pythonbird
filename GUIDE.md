# Pythonbird: Complete Developer Guide and API Reference

This documentation covers every class, method, configuration detail, and exception handling mechanism available in the `pythonbird` library.

---

## Table of Contents
1. [Core Architecture Overview](#1-core-architecture-overview)
2. [Module: ThunderbirdLinux](#2-module-thunderbirdlinux)
3. [Module: ThunderbirdMail](#3-module-thunderbirdmail)
4. [Module: ThunderbirdContacts](#4-module-thunderbirdcontacts)
5. [Exception and Error Handling](#5-exception-and-error-handling)
6. [Advanced Concurrency and Safety Practices](#6-advanced-concurrency-and-safety-practices)

---

## 1. Core Architecture Overview

The `pythonbird` library interacts natively with Mozilla Thunderbird on Linux systems without relying on heavy external runtime wrappers. It operates via three primary vector approaches:
- **Direct Configuration Parsing:** Reads and decodes JavaScript runtime options (`prefs.js`) and profile trees (`profiles.ini`).
- **Low-Level File I/O Locking:** Securely extracts tabular contact logs from SQLite databases and reads emails from sequential flat-file standard Mbox containers.
- **Process Orchestration:** Forwards mail construction commands via background system subprocess shell pipelines.

---

## 2. Module: ThunderbirdLinux

The foundational controller class. It initializes environmental sweeps, evaluates installation paths, and hosts active configuration states.

### Class: `ThunderbirdLinux()`
No arguments are required for initialization. Upon invocation, it triggers auto-discovery procedures.

#### Properties
- `base_dir` *(pathlib.Path)*: The resolved root directory where Thunderbird stores global configs (`~/.thunderbird` or Snap alternatives).
- `profile_dir` *(pathlib.Path)*: The absolute path pointing directly inside the active, default profile workspace directory.
- `prefs` *(dict)*: Key-value dictionary containing raw parsed settings from the active profile's `prefs.js` file.
- `cmd` *(str)*: System command execution prefix resolved for your active Linux packaging scheme (`thunderbird` or `flatpak run ...`).

#### Methods

##### `get_mail_accounts() -> list[str]`
Scans loaded configuration rules to isolate all actively registered user email accounts.
- **Returns:** A list of strings containing email addresses.
- **Example:**
  ```python
  from pythonbird import ThunderbirdLinux
  tb = ThunderbirdLinux()
  print(tb.get_mail_accounts()) # ['user@example.com', 'work@company.org']
  ```

##### `open_compose_window(to: str, subject: str, body: str, attachment_path: str = None) -> None`
Spawns a native, graphical Thunderbird window pre-loaded with mail data. Does not lock your running Python script thread.
- **Parameters:**
  - `to` *(str)*: Target recipient email address.
  - `subject` *(str)*: Text line for the message header subject.
  - `body` *(str)*: Raw plain text lines for the email body message.
  - `attachment_path` *(str, optional)*: Absolute local system path to a target file file attachment.
- **Example:**
  ```python
  tb.open_compose_window(
      to="friend@mail.com",
      subject="Library Test",
      body="Sent via pythonbird!",
      attachment_path="/home/user/documents/report.pdf"
  )
  ```

---

## 3. Module: ThunderbirdMail

Handles safe reading of local storage structures where emails are physically mirrored on disk.

### Class: `ThunderbirdMail(tb_instance: ThunderbirdLinux)`
- **Parameters:**
  - `tb_instance` *(ThunderbirdLinux)*: An initialized instance of the core connection controller.

#### Methods

##### `get_local_inbox_messages() -> list[dict]`
Extracts all available sequential messages mirrored within local data storage boxes.
- **Returns:** A list of structured dictionaries. Each item contains:
  - `id` *(int)*: Sequential entry index inside the mailbox store.
  - `from` *(str)*: Unparsed message sender identification string header.
  - `subject` *(str)*: Decoded email title header.
  - `date` *(str)*: Original timestamp delivery header.
  - `body` *(str)*: Plain text block body payload.
- **Example:**
  ```python
  from pythonbird import ThunderbirdLinux, ThunderbirdMail
  
  tb = ThunderbirdLinux()
  reader = ThunderbirdMail(tb)
  for email in reader.get_local_inbox_messages():
      print(f"[{email['date']}] {email['subject']} from {email['from']}")
  ```

---

## 4. Module: ThunderbirdContacts

Intersects local address book catalogs without interfering with live database sync procedures.

### Class: `ThunderbirdContacts(tb_instance: ThunderbirdLinux)`
- **Parameters:**
  - `tb_instance` *(ThunderbirdLinux)*: An initialized instance of the core connection controller.

#### Methods

##### `get_all_contacts() -> list[dict]`
Establishes a temporary, isolated, read-only sqlite database connection pool to index contact information.
- **Returns:** A list of dictionaries representing individual contacts:
  - `name` *(str)*: Display name as saved in the Thunderbird interface.
  - `email` *(str)*: Primary target email contact vector.
- **Example:**
  ```python
  from pythonbird import ThunderbirdLinux, ThunderbirdContacts
  
  tb = ThunderbirdLinux()
  address_book = ThunderbirdContacts(tb)
  for contact in address_book.get_all_contacts():
      print(f"Name: {contact['name']} | Email: {contact['email']}")
  ```

---

## 5. Exception and Error Handling

Your application should wrap `pythonbird` invocations in standard `try-except` blocks to handle system-specific edge cases cleanly.

```python
from pythonbird import ThunderbirdLinux

try:
    tb = ThunderbirdLinux()
except FileNotFoundError as e:
    # Triggered if Thunderbird is not installed or profiles are wiped
    print(f"System Discovery Error: {e}")
except PermissionError:
    # Triggered if user lacks read permissions to ~/.thunderbird files
    print("Security block: Access to Thunderbird profiles denied.")
```

### Common Fault Vectors
1. **`FileNotFoundError: Thunderbird directory not found...`**
   - *Cause:* Thunderbird has never been launched by the current Linux user, or it uses an untracked customized flatpak environment.
2. **Empty accounts list returned**
   - *Cause:* Profile paths match correctly, but no email entries have been configured yet inside the setup wizard.

---

## 6. Advanced Concurrency and Safety Practices

### Database Lock Management
Thunderbird creates temporary execution locks (`.parentlock`) when active. 
- `pythonbird` bypasses write conflicts by enforcing a strict **Read-Only Uniform Resource Identifier scheme** (`file:...mode=ro`) when interacting with `abook.sqlite`.
- Mail containers are wrapped in software-level context flags using standard kernel system wrappers (`mailbox.mbox.lock()`) to guarantee that operations will not drop or corrupt mail text tables if the Python runtime executes while Thunderbird is polling background updates.

---

## License

This project is licensed under the [MIT License](LICENSE).
