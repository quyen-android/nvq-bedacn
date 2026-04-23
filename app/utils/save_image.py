import os
import uuid
from io import BytesIO
from PIL import Image
from slugify import slugify


def make_slug(text: str) -> str:
    return slugify(text, separator="_")


async def save_image(file, folder_path: str) -> str:
    contents = await file.read()

    image = Image.open(BytesIO(contents)).convert("RGB")

    filename = f"{uuid.uuid4().hex}.jpg"

    os.makedirs(folder_path, exist_ok=True)

    full_path = os.path.join(folder_path, filename)
    image.save(full_path, "JPEG")

    return filename