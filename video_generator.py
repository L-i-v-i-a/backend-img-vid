from moviepy.editor import (
    ImageClip,
    CompositeVideoClip
)

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

    # =========================================
    # UNIQUE FILES
    # =========================================

    timestamp = int(time.time() * 1000)

    temp_image = f"outputs/temp_{timestamp}.jpg"

    final_output = f"outputs/video_{timestamp}.mp4"

    # =========================================
    # LOAD IMAGE
    # =========================================

    try:
        image = Image.open(image_path).convert("RGB")

    except Exception as e:
        raise Exception(f"Failed to load image: {e}")

    # =========================================
    # RESIZE IMAGE
    # =========================================

    image = image.resize((900, 900))

    image.save(temp_image)

    # =========================================
    # VIDEO SETTINGS
    # =========================================

    duration = 4

    canvas_w = 720
    canvas_h = 720

    # =========================================
    # BASE IMAGE CLIP
    # =========================================

    clip = ImageClip(temp_image).set_duration(duration)

    # =========================================
    # MOTIONS
    # =========================================

    # ZOOM IN
    if motion == "zoom":

        animated = clip.resize(
            lambda t: 1 + (0.08 * t)
        ).set_position("center")

    # ZOOM OUT
    elif motion == "zoom_out":

        animated = clip.resize(
            lambda t: 1.3 - (0.08 * t)
        ).set_position("center")

    # PAN LEFT
    elif motion == "pan_left":

        animated = clip.set_position(
            lambda t: (-120 * t, "center")
        )

    # PAN RIGHT
    elif motion == "pan_right":

        animated = clip.set_position(
            lambda t: (120 * t, "center")
        )

    # PAN UP
    elif motion == "pan_up":

        animated = clip.set_position(
            lambda t: ("center", -120 * t)
        )

    # PAN DOWN
    elif motion == "pan_down":

        animated = clip.set_position(
            lambda t: ("center", 120 * t)
        )

    # DIAGONAL
    elif motion == "pan_diagonal":

        animated = clip.set_position(
            lambda t: (80 * t, 80 * t)
        )

    # ROTATE
    elif motion == "rotate":

        animated = clip.rotate(
            lambda t: t * 4
        ).set_position("center")

    # SHAKE
    elif motion == "shake":

        animated = clip.set_position(
            lambda t: (
                10 if int(t * 10) % 2 == 0 else -10,
                10 if int(t * 10) % 2 == 0 else -10
            )
        )

    # PULSE
    elif motion == "pulse":

        animated = clip.resize(
            lambda t: 1 + (0.05 * abs((t * 2) % 2 - 1))
        ).set_position("center")

    # FALLBACK
    else:

        animated = clip.set_position("center")

    # =========================================
    # IMPORTANT FIX:
    # COMPOSITE VIDEO CLIP
    # =========================================

    final = CompositeVideoClip(
        [animated],
        size=(canvas_w, canvas_h)
    )

    # =========================================
    # EXPORT
    # =========================================

    try:

        final.write_videofile(
            final_output,
            fps=12,
            codec="libx264",
            audio=False,
            logger=None
        )

    except Exception as e:

        raise Exception(f"Video export failed: {e}")

    # =========================================
    # CLEAN TEMP IMAGE
    # =========================================

    try:
        os.remove(temp_image)
    except:
        pass

    return final_output