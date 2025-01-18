import re

from httpx import Client, Response

from core.constants import STATIC_PATH

client = Client()


CONTENT_DISPOSITION_FILENAME_REGEX = re.compile(r'filename="(.+)"')


def get_filename_from_content_disposition(response: Response) -> str | None:
    """
    Extract filename from Content-Disposition header.
    """
    content_disposition = response.headers.get("Content-Disposition")
    match = CONTENT_DISPOSITION_FILENAME_REGEX.search(content_disposition)
    if match:
        return match.group(1)
    return None


def guess_file_extension(response: Response) -> str | None:
    """
    Guess the file extension from the response content type.
    """
    content_type = response.headers.get("Content-Type")
    if content_type:
        return content_type.split("/")[-1]

    if filename := get_filename_from_content_disposition(response):
        return filename.split(".")[-1]

    return None


def download_media(
    url: str,
    name: str,
    subdirectory: str | None = None,
    default_extension: str = ".webp",
) -> str:
    """
    Download media from URL.
    """
    root_path = STATIC_PATH / (subdirectory or "")

    response = client.get(url)
    file_name = f"{name}.{guess_file_extension(response) or default_extension}"
    with open(root_path / file_name, "wb") as file:
        file.write(response.content)

    return file_name
