import cv2


def get_video_metadata(video_path: str) -> dict:
    """
    Opens a local video file and extracts basic metadata.

    Args:
        video_path (str): Local path to the video file.

    Returns:
        dict: Basic video metadata including fps, frame count, and duration.
    """

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise RuntimeError(f"Failed to open video file: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps <= 0:
        capture.release()
        raise RuntimeError(f"Invalid FPS value for video: {video_path}")

    duration_sec = frame_count / fps

    capture.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration_sec": duration_sec,
    }
