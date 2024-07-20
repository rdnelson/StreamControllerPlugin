from typing import Tuple
from PIL import Image
import numpy as np

def color_shift(image: str|Image.Image, color: Tuple[int, int, int, int]) -> Image:
    if isinstance(image, str): 
        image = Image.open(image)

    rgba = image.convert("RGBA")
    data = np.array(rgba)
    red, green, blue, _ = data.T
    white_areas = (red == 0xff) & (blue == 0xff) & (green == 0xff)
    data[..., :-1][white_areas.T] = color[:-1]

    return Image.fromarray(data)
