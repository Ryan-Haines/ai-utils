import argparse
import os
import subprocess
from PIL import Image

def process_svgs(input_path, canvas_width, canvas_height):
    for file in os.listdir(input_path):
        if file.lower().endswith('.svg'):
            svg_path = os.path.join(input_path, file)
            png_path = os.path.join(input_path, os.path.splitext(file)[0] + '.png')

            print('Processing ' + svg_path)
            print('Saving to ' + png_path)

            # Convert SVG to PNG using ImageMagick
            try:
                result = subprocess.run(['magick', svg_path, png_path], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"Error converting file {file}: {e}")
                continue

            # Open the PNG with Pillow
            with Image.open(png_path) as img:
                aspect_ratio = min(canvas_width / img.width, canvas_height / img.height)
                new_size = (int(img.width * aspect_ratio), int(img.height * aspect_ratio))

                # Resize and center the image
                img = img.resize(new_size, Image.ANTIALIAS)
                new_img = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))  # White background
                new_img.paste(img, ((canvas_width - new_size[0]) // 2, (canvas_height - new_size[1]) // 2))

                # Save the centered image
                new_img.save(png_path)

def main():
    parser = argparse.ArgumentParser(description='Process SVG files in a directory.')
    parser.add_argument('--path', type=str, required=True, help='Input folder path')
    parser.add_argument('-w', '--width', type=int, required=True, help='Canvas width')
    parser.add_argument('-ht', '--height', type=int, required=True, help='Canvas height')

    args = parser.parse_args()
    process_svgs(args.path, args.width, args.height)

if __name__ == "__main__":
    main()
