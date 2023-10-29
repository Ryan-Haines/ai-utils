import argparse
import os
from PIL import Image

def sort_images_by_orientation(path: str) -> None:
    portrait_path = os.path.join(path, 'portrait')
    landscape_path = os.path.join(path, 'landscape')

    os.makedirs(portrait_path, exist_ok=True)
    os.makedirs(landscape_path, exist_ok=True)

    for filename in os.listdir(path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(path, filename)
            with Image.open(filepath) as img:
                width, height = img.size
            if width > height:
                os.rename(filepath, os.path.join(landscape_path, filename))
            else:
                os.rename(filepath, os.path.join(portrait_path, filename))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, type=str, help='Directory containing images to sort.')
    args = parser.parse_args()

    sort_images_by_orientation(args.path)

