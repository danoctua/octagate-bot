import re


URL_PATTERN = re.compile(
    r"(?i)\b((?:https?|ftp):\/\/(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^\s]*)?|t\.me\/\w+)\b"
)
BROAD_URL_PATTERN = re.compile(r"[^\s]+\.[a-zA-Z][a-zA-Z]+\/?[^\s]*")
USERNAME_PATTERN = re.compile(r"@([a-zA-Z0-9_]{5,32})\b")

REPLACE_STRING = "k3w1"


def cleanup_name(name: str) -> str:
    name_cleaned = name
    for pattern in (BROAD_URL_PATTERN, USERNAME_PATTERN):
        name_cleaned = re.sub(pattern, REPLACE_STRING, name_cleaned)

    return name_cleaned
