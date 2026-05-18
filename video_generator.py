from moviepy.editor import ImageClip
from PIL import Image
import os
import time


def generate_video(
    image_path: str,
    motion: str = "zoom",
    frames: int = 8,
    output_path: str = "outputs/generated.mp4"
):

    os.makedirs("outputs", exist_ok=True)

    # =========================
    # SAFE UNIQUE FILE NAMES
    # =========================
    timestamp = int(time.time() * 1000)
    temp_image = f"outputs/temp_{timestamp}.jpg"
    final_output = f"outputs/video_{timestamp}.mp4"

    # =========================
    # LOAD IMAGE SAFELY
    # =========================
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise Exception(f"Failed to load image: {e}")

    # Resize for speed (important for Render stability)
    image = image.resize((640, 640))
    image.save(temp_image)

    duration = 4

    # =========================
    # CREATE CLIP
    # =========================
    clip = ImageClip(temp_image).set_duration(duration)

    # =========================
    # MOTION EFFECTS (EXPANDED)
    # =========================

    # 🔵 BASIC ZOOM IN
    if motion == "zoom":
        clip = clip.resize(lambda t: 1 + (0.06 * t))

    # 🔵 ZOOM OUT
    elif motion == "zoom_out":
        clip = clip.resize(lambda t: 1.2 - (0.05 * t))

    # 🔵 PAN LEFT
    elif motion == "pan_left":
        clip = clip.set_position(lambda t: (-60 * t, "center"))

    # 🔵 PAN RIGHT
    elif motion == "pan_right":
        clip = clip.set_position(lambda t: (60 * t, "center"))

    # 🔵 PAN UP
    elif motion == "pan_up":
        clip = clip.set_position(lambda t: ("center", -60 * t))

    # 🔵 PAN DOWN
    elif motion == "pan_down":
        clip = clip.set_position(lambda t: ("center", 60 * t))

    # 🔵 DIAGONAL MOVE
    elif motion == "pan_diagonal":
        clip = clip.set_position(lambda t: (40 * t, 40 * t))

    # 🔵 ROTATE
    elif motion == "rotate":
        clip = clip.rotate(lambda t: t * 2.5)

    # 🔵 SHAKE EFFECT
    elif motion == "shake":
        clip = clip.set_position(
            lambda t: (5 * (t * 10 % 2 - 1), 5 * (t * 10 % 2 - 1))
        )

    # 🔵 PULSE ZOOM (nice cinematic effect)
    elif motion == "pulse":
        clip = clip.resize(lambda t: 1 + 0.03 * abs(t * 3 % 2 - 1))

    # =========================
    # EXPORT VIDEO (STABLE SETTINGS)
    # =========================
    try:
        clip.write_videofile(
            final_output,
            fps=12,              # faster + more stable than 24
            codec="libx264",
            audio=False,
            logger=None
        )
    except Exception as e:
        raise Exception(f"Video export failed: {e}")

    return final_output