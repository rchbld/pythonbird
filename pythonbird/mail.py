from __future__ import annotations

import mailbox
from email.header import decode_header, make_header
from email.message import Message
from pathlib import Path
from typing import Iterator, Optional, Union

from .core import ThunderbirdLinux


class ThunderbirdMail:
    def __init__(self, tb_instance: ThunderbirdLinux):
        self.profile_dir = tb_instance.profile_dir

    def get_local_inbox_messages(
        self,
        limit: Optional[int] = None,
    ) -> list[dict]:
        return list(self.iter_local_inbox_messages(limit=limit))

    def iter_local_inbox_messages(
        self,
        limit: Optional[int] = None,
    ) -> Iterator[dict]:
        mbox_path = self.profile_dir / "Mail" / "Local Folders" / "Inbox"

        yield from self.iter_mbox_messages(
            mbox_path=mbox_path,
            limit=limit,
        )

    def get_mbox_messages(
        self,
        mbox_path: Union[str, Path],
        limit: Optional[int] = None,
    ) -> list[dict]:
        return list(
            self.iter_mbox_messages(
                mbox_path=mbox_path,
                limit=limit,
            )
        )

    def iter_mbox_messages(
        self,
        mbox_path: Union[str, Path],
        limit: Optional[int] = None,
    ) -> Iterator[dict]:
        mbox_path = Path(mbox_path).expanduser().resolve()

        if not mbox_path.is_file():
            return

        if limit is not None and limit < 0:
            raise ValueError("limit must be greater than or equal to zero.")

        mbox = mailbox.mbox(
            mbox_path,
            create=False,
        )

        try:
            for position, (message_id, message) in enumerate(mbox.iteritems()):
                if limit is not None and position >= limit:
                    break

                yield self._message_to_dict(message_id, message)
        finally:
            mbox.close()

    def _message_to_dict(self, message_id, message: Message) -> dict:
        bodies = self._get_bodies(message)

        return {
            "id": message_id,
            "from": self._decode_header(message.get("from")),
            "to": self._decode_header(message.get("to")),
            "subject": self._decode_header(message.get("subject")),
            "date": self._decode_header(message.get("date")),
            "body": bodies["text"],
            "text_body": bodies["text"],
            "html_body": bodies["html"],
        }

    def _get_body(self, message: Message) -> str:
        bodies = self._get_bodies(message)

        if bodies["text"]:
            return bodies["text"]

        return bodies["html"]

    def _get_bodies(self, message: Message) -> dict[str, str]:
        text_parts = []
        html_parts = []

        if message.is_multipart():
            parts = message.walk()
        else:
            parts = [message]

        for part in parts:
            if part.is_multipart():
                continue

            content_disposition = part.get_content_disposition()

            if content_disposition == "attachment":
                continue

            content_type = part.get_content_type()

            if content_type == "text/plain":
                decoded = self._decode_part(part)

                if decoded:
                    text_parts.append(decoded)

            elif content_type == "text/html":
                decoded = self._decode_part(part)

                if decoded:
                    html_parts.append(decoded)

        return {
            "text": "\n".join(text_parts).strip(),
            "html": "\n".join(html_parts).strip(),
        }

    @staticmethod
    def _decode_part(part: Message) -> str:
        payload = part.get_payload(decode=True)

        if payload is None:
            raw_payload = part.get_payload()

            if isinstance(raw_payload, str):
                return raw_payload

            return ""

        charset = part.get_content_charset() or "utf-8"

        try:
            return payload.decode(charset)
        except (LookupError, UnicodeDecodeError):
            return payload.decode("utf-8", errors="replace")

    @staticmethod
    def _decode_header(value: Optional[str]) -> str:
        if value is None:
            return ""

        try:
            return str(make_header(decode_header(value)))
        except (LookupError, UnicodeDecodeError):
            return value
