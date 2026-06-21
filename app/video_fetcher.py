import hashlib
import requests
from pathlib import Path


CACHE_DIR = Path("videos_cache")
CACHE_DIR.mkdir(exist_ok=True)


def _generate_filename(url: str) -> str:
    """
    Generates a unique filename for the video based on its URL.
    """
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"{url_hash}.mp4"


def fetch_video(url: str, force_download: bool = False) -> str:
    """
    Downloads a video from a URL and saves it locally in a cache directory.

    Args:
        url (str): The video URL.
        force_download (bool): If True, downloads again even if cache exists.

    Returns:
        str: The local file path of the video.
    """

    filename = _generate_filename(url)
    file_path = CACHE_DIR / filename

    # Cache hit
    if file_path.exists() and not force_download:
        return str(file_path)

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        return str(file_path)

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch video from {url}: {e}")
