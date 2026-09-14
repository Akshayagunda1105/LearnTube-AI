from app.services.youtube_service import extract_video_id


test_urls = [
    "https://www.youtube.com/watch?v=i_LwzRVP7bg&list=PLWKjhJtqVAblStefaz_YOVpDWqcRScc2s",
    "https://youtu.be/i_LwzRVP7bg",
]


for url in test_urls:
    video_id = extract_video_id(url)
    print(f"URL: {url}")
    print(f"Video ID: {video_id}")
    print("-" * 50)