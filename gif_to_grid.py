import argparse
import io
import os
from typing import Optional, Tuple

import requests
from PIL import Image, ImageSequence


def load_gif(gif_path: str) -> Image.Image:
    """
    Load a GIF from a local path or a URL.

    :param gif_path: Local file path or HTTP/HTTPS URL to a GIF.
    :return: PIL Image object.
    :raises RuntimeError: If the GIF cannot be loaded.
    """
    try:
        if gif_path.startswith(("http://", "https://")):
            response = requests.get(gif_path, timeout=10)
            response.raise_for_status()
            image_bytes = io.BytesIO(response.content)
            img = Image.open(image_bytes)
        else:
            if not os.path.exists(gif_path):
                raise FileNotFoundError(f"File not found: {gif_path}")
            img = Image.open(gif_path)

        return img

    except Exception as e:
        raise RuntimeError(f"Failed to load GIF: {e}") from e


def gif_to_png_grid(
    gif_path: str,
    output_path: Optional[str] = None,
    grid_size: Tuple[int, int] = (4, 6),
) -> Image.Image:
    """
    Convert a GIF into a single PNG image arranged in a grid.

    :param gif_path: Path or URL to the input GIF.
    :param output_path: Path to save the output PNG (optional).
    :param grid_size: (rows, cols) of the output grid.
    :return: The combined grid image.
    """
    rows, cols = grid_size
    gif = load_gif(gif_path)

    frames = [
        frame.convert("RGB")
        for frame in ImageSequence.Iterator(gif)
    ]

    expected_frames = rows * cols
    if len(frames) != expected_frames:
        raise ValueError(
            f"Frame count mismatch: expected {expected_frames}, "
            f"but got {len(frames)}"
        )

    frame_width, frame_height = frames[0].size
    grid_image = Image.new(
        "RGB",
        (frame_width * cols, frame_height * rows)
    )

    for idx, frame in enumerate(frames):
        row = idx // cols
        col = idx % cols
        x_offset = col * frame_width
        y_offset = row * frame_height
        grid_image.paste(frame, (x_offset, y_offset))

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        grid_image.save(output_path)
        print(f"Saved grid image to: {output_path}")

    return grid_image


def main():
    parser = argparse.ArgumentParser(
        description="Convert a GIF into a grid PNG image."
    )
    parser.add_argument(
        "--gif_path",
        type=str,
        help="Path or URL to the input GIF",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=4,
        help="Number of rows in the grid (default: 4)",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=6,
        help="Number of columns in the grid (default: 6)",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="output.png",
        help="Output PNG file path (default: gif_grid.png)",
    )

    args = parser.parse_args()

    gif_to_png_grid(
        gif_path=args.gif_path,
        output_path=args.output_path,
        grid_size=(args.rows, args.cols),
    )


if __name__ == "__main__":
    main()
