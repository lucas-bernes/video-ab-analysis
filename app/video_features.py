import cv2
import numpy as np


def extract_video_features(video_path: str, sample_interval_sec: float = 0.5) -> dict:
    """
    Opens a local video file, samples frames at a fixed time interval,
    and extracts lightweight visual features.

    Args:
        video_path (str): Local path to the video file.
        sample_interval_sec (float): Time interval between sampled frames in seconds.

    Returns:
        dict: Video metadata and visual features.
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

    frame_step = max(1, int(fps * sample_interval_sec))

    brightness_values = []
    saturation_values = []

    frame_index = 0

    while True:
        success, frame = capture.read()

        if not success:
            break

        if frame_index % frame_step == 0:
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            brightness = hsv_frame[:, :, 2].mean()
            saturation = hsv_frame[:, :, 1].mean()

            brightness_values.append(brightness)
            saturation_values.append(saturation)

        frame_index += 1

    capture.release()

    avg_brightness = float(np.mean(brightness_values)
                           ) if brightness_values else 0.0
    avg_saturation = float(np.mean(saturation_values)
                           ) if saturation_values else 0.0

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration_sec": duration_sec,
        "avg_brightness": avg_brightness,
        "avg_saturation": avg_saturation,
    }
