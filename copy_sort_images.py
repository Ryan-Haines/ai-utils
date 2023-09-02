import os
import shutil
from PIL import Image
import argparse
import random

def copy_images(base_folder, out_folder, min_width, min_height):
    # Check if output directories exist; if not, create them
    landscape_dir = os.path.join(out_folder, 'landscape')
    portrait_dir = os.path.join(out_folder, 'portrait')

    if not os.path.exists(landscape_dir):
        os.makedirs(landscape_dir)
    if not os.path.exists(portrait_dir):
        os.makedirs(portrait_dir)

    current_seed = None

    # Walk through the base directory
    for dirpath, dirnames, filenames in os.walk(base_folder):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
                full_path = os.path.join(dirpath, filename)

                # Check image dimensions using PIL
                with Image.open(full_path) as img:
                    width, height = img.size

                    # Check if the image dimensions are above the minimum dimensions
                    if width > min_width and height > min_height:
                        destination_dir = landscape_dir if width > height else portrait_dir
                        destination_path = os.path.join(destination_dir, filename)

                        # Roll a new seed if needed
                        if os.path.exists(destination_path):
                            current_seed = random.randint(1000, 1001000)
                        
                        new_filename = f"{current_seed}_{filename}" if current_seed and os.path.exists(destination_path) else filename
                        destination_path = os.path.join(destination_dir, new_filename)

                        shutil.copy2(full_path, destination_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sort images into portrait and landscape folders.')
    parser.add_argument('--folder', required=True, help='Base folder containing images.')
    parser.add_argument('--out', required=True, help='Output directory where images should be copied.')
    parser.add_argument('--minWidth', type=int, default=0, help='Minimum width of images to be copied.')
    parser.add_argument('--minHeight', type=int, default=0, help='Minimum height of images to be copied.')

    args = parser.parse_args()

    copy_images(args.folder, args.out, args.minWidth, args.minHeight)
