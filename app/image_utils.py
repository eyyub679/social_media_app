from imagekitio import ImageKit
from dotenv import load_dotenv
import os

load_dotenv()

ik = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)
