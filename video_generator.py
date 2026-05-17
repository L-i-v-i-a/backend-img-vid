from moviepy.editor import ImageClip
from PIL import Image
import os


def generate_video(
    image_path: str,
    motion: str = "zoom",
    frames: int = 8,
    output_path: str = "outputs/generated.mp4"
):

    os.makedirs("outputs", exist_ok=True)

    # =========================
    # LOAD IMAGE
    # =========================
    image = Image.open(image_path).convert("RGB")

    # Resize for speed
    image = image.resize((720, 720))

    temp_image = "outputs/temp_image.jpg"
    image.save(temp_image)

    duration = 4

    # =========================
    # CREATE CLIP
    # =========================
    clip = ImageClip(temp_image).set_duration(duration)

    # =========================
    # MOTION EFFECTS
    # =========================
    if motion == "zoom":

        clip = clip.resize(
            lambda t: 1 + (0.08 * t)
        )

    elif motion == "zoom_out":

        clip = clip.resize(
            lambda t: 1.2 - (0.05 * t)
        )

    elif motion == "pan_left":

        clip = clip.set_position(
            lambda t: (-50 * t, "center")
        )

    elif motion == "pan_right":

        clip = clip.set_position(
            lambda t: (50 * t, "center")
        )

    elif motion == "rotate":

        clip = clip.rotate(
            lambda t: t * 3
        )

    # =========================
    # EXPORT VIDEO
    # =========================
    clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False
    )

    return output_path