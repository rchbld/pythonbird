import configparser
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Sequence, Union


class ThunderbirdLinux:
    def __init__(
        self,
        profile_dir: Optional[Union[str, Path]] = None,
        command: Optional[Sequence[str]] = None,
    ):
        """
        Creates a Thunderbird client instance.

        Args:
            profile_dir:
                Explicit path to a Thunderbird profile. If omitted,
                the default profile is detected automatically.

            command:
                Explicit Thunderbird launch command, for example:
                ["thunderbird"]
                or
                ["flatpak", "run", "org.mozilla.Thunderbird"].
        """
        if profile_dir is None:
            self.base_dir = self._find_thunderbird_dir()
            self.profile_dir = self._get_active_profile_dir()
        else:
            self.profile_dir = Path(profile_dir).expanduser().resolve()
            self.base_dir = self.profile_dir.parent

            if not self.profile_dir.is_dir():
                raise FileNotFoundError(
                    f"Thunderbird profile directory does not exist: "
                    f"{self.profile_dir}"
                )

        self.prefs = self._parse_prefs()
        self.cmd = (
            list(command) if command is not None else self._detect_system_command()
        )

    def _find_thunderbird_dir(self) -> Path:
        """Locates the root Thunderbird directory on Linux."""
        candidate_paths = [
            Path.home() / ".thunderbird",
            Path.home() / "snap" / "thunderbird" / "common" / ".thunderbird",
            Path.home() / ".var" / "app" / "org.mozilla.Thunderbird" / ".thunderbird",
        ]

        for candidate in candidate_paths:
            if candidate.is_dir():
                return candidate

        checked_paths = "\n".join(f"- {path}" for path in candidate_paths)

        raise FileNotFoundError(
            "Thunderbird profile directory was not found.\n"
            f"Checked paths:\n{checked_paths}"
        )

    def _get_active_profile_dir(self) -> Path:
        """Determines the active/default profile directory using profiles.ini."""
        ini_path = self.base_dir / "profiles.ini"

        if not ini_path.is_file():
            raise FileNotFoundError(
                f"Thunderbird profiles.ini file is missing: {ini_path}"
            )

        config = configparser.ConfigParser()
        config.read(ini_path, encoding="utf-8")

        profile_path = self._find_profile_from_install_section(config)

        if profile_path is None:
            profile_path = self._find_default_profile_section(config)

        if profile_path is None:
            profile_path = self._find_profile_directory_fallback()

        if profile_path is None:
            raise FileNotFoundError(
                "Could not determine the active Thunderbird profile."
            )

        profile_path = profile_path.expanduser().resolve()

        if not profile_path.is_dir():
            raise FileNotFoundError(
                f"Thunderbird profile directory does not exist: {profile_path}"
            )

        return profile_path

    def _find_profile_from_install_section(
        self, config: configparser.ConfigParser
    ) -> Optional[Path]:
        """
        Looks for a default profile specified in an Install section.

        Modern versions of Thunderbird can store the active profile there.
        """
        for section in config.sections():
            if not section.startswith("Install"):
                continue

            path_value = config.get(section, "Default", fallback=None)

            if path_value:
                return self.base_dir / path_value

        return None

    def _find_default_profile_section(
        self, config: configparser.ConfigParser
    ) -> Optional[Path]:
        """Looks for a Profile section marked as default."""
        for section in config.sections():
            if not section.startswith("Profile"):
                continue

            if config.get(section, "Default", fallback="0") != "1":
                continue

            path_value = config.get(section, "Path", fallback=None)

            if not path_value:
                continue

            is_relative = config.getboolean(
                section,
                "IsRelative",
                fallback=True,
            )

            if is_relative:
                return self.base_dir / path_value

            return Path(path_value)

        return None

    def _find_profile_directory_fallback(self) -> Optional[Path]:
        """Tries to locate a profile directory when profiles.ini is incomplete."""
        suffixes = (
            ".default-release",
            ".default",
        )

        for item in self.base_dir.iterdir():
            if item.is_dir() and item.name.endswith(suffixes):
                return item

        return None

    def _parse_prefs(self) -> dict:
        """Parses values from the Thunderbird prefs.js file."""
        prefs_path = self.profile_dir / "prefs.js"

        if not prefs_path.is_file():
            return {}

        prefs = {}

        pattern = re.compile(
            r"^\s*user_pref\(\s*"
            r'("(?:\\.|[^"\\])*")'
            r"\s*,\s*"
            r"(.+)"
            r"\s*\);\s*$"
        )

        with prefs_path.open(
            "r",
            encoding="utf-8",
            errors="replace",
        ) as prefs_file:
            for line in prefs_file:
                match = pattern.match(line)

                if match is None:
                    continue

                raw_key, raw_value = match.groups()

                try:
                    key = json.loads(raw_key)
                    value = self._parse_pref_value(raw_value)
                except (json.JSONDecodeError, ValueError):
                    continue

                prefs[key] = value

        return prefs

    @staticmethod
    def _parse_pref_value(raw_value: str):
        """Converts a prefs.js value into an appropriate Python value."""
        raw_value = raw_value.strip()

        if raw_value.startswith('"'):
            return json.loads(raw_value)

        if raw_value == "true":
            return True

        if raw_value == "false":
            return False

        if raw_value == "null":
            return None

        try:
            return int(raw_value)
        except ValueError:
            pass

        try:
            return float(raw_value)
        except ValueError:
            return raw_value

    def _detect_system_command(self) -> list[str]:
        """Detects how Thunderbird is installed."""
        if shutil.which("thunderbird"):
            return ["thunderbird"]

        if shutil.which("flatpak"):
            result = subprocess.run(
                ["flatpak", "info", "org.mozilla.Thunderbird"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            if result.returncode == 0:
                return ["flatpak", "run", "org.mozilla.Thunderbird"]

        raise FileNotFoundError(
            "Thunderbird executable was not found. "
            "Install Thunderbird or pass command explicitly."
        )

    def get_mail_accounts(self) -> list[str]:
        """Returns a list of configured email addresses."""
        accounts = []

        for key, value in self.prefs.items():
            if (
                key.startswith("mail.identity.")
                and key.endswith(".useremail")
                and isinstance(value, str)
                and value
            ):
                accounts.append(value)

        return list(dict.fromkeys(accounts))

    def open_compose_window(
        self,
        to: str,
        subject: str,
        body: str,
        attachment_path: Optional[Union[str, Path]] = None,
    ) -> subprocess.Popen:
        """Opens a Thunderbird composition window with pre-filled fields."""
        compose_parts = [
            f"to='{self._escape_compose_value(to)}'",
            f"subject='{self._escape_compose_value(subject)}'",
            f"body='{self._escape_compose_value(body)}'",
        ]

        if attachment_path is not None:
            attachment = Path(attachment_path).expanduser().resolve()

            if not attachment.is_file():
                raise FileNotFoundError(f"Attachment file does not exist: {attachment}")

            attachment_uri = attachment.as_uri()

            compose_parts.append(
                f"attachment='{self._escape_compose_value(attachment_uri)}'"
            )

        compose_args = ",".join(compose_parts)

        return subprocess.Popen(
            [*self.cmd, "-compose", compose_args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @staticmethod
    def _escape_compose_value(value: str) -> str:
        """
        Escapes characters that can break a Thunderbird compose argument.

        Shell escaping is not needed because the command is launched
        without shell=True.
        """
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\r\n", "\\n")
            .replace("\r", "\\n")
            .replace("\n", "\\n")
        )
