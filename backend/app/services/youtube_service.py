from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    """
    Extract the YouTube video ID from a YouTube URL.
    """

    parsed_url = urlparse(url)

    # Standard URL:
    # https://www.youtube.com/watch?v=i_LwzRVP7bg
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)

        if "v" in query_params:
            return query_params["v"][0]

    # Short URL:
    # https://youtu.be/i_LwzRVP7bg
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    raise ValueError("Invalid YouTube URL")