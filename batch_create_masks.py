import os
import argparse
from PIL import Image, ImageDraw
import easyocr
from tqdm import tqdm 
import shutil

def is_touching_edges(x1, y1, x2, y2, img_width, img_height):
    return x1 <= 0 or y1 <= 0 or x2 >= img_width or y2 >= img_height

def is_touching_corners(x1, y1, x2, y2, img_width, img_height):
    corners = [(0, 0), (img_width, 0), (0, img_height), (img_width, img_height)]
    for cx, cy in corners:
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return True
    return False

def process_image(image_path, out_folder, include_textfile, xpad=24, ypad=24, corners=False, edges=False):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    
    image = Image.open(image_path)
    width, height = image.size
    mask = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(mask)
    
    mask_created = False  # Flag to check if any mask is created

    for detection in result:
        top_left, top_right, bottom_right, bottom_left = detection[0]
        x1, y1 = top_left
        x2, y2 = bottom_right
        x3, y3 = top_right
        x4, y4 = bottom_left

        within_xpad = lambda x: x <= xpad or x >= width - xpad
        within_ypad = lambda y: y <= ypad or y >= height - ypad

        touches_corner = any(within_xpad(x) and within_ypad(y) for x, y in [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
        touches_edge = any(within_xpad(x) or within_ypad(y) for x, y in [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
        
        if corners and not touches_corner:
            continue
        if edges and not touches_edge:
            continue

        draw.rectangle([x1 - xpad, y1 - ypad, x2 + xpad, y2 + ypad], fill="black")
        mask_created = True
    
    if mask_created:
        mask_filename = os.path.join(out_folder, os.path.basename(image_path))
        mask.save(mask_filename)
        
        if include_textfile:
            txt_filename = mask_filename.rsplit('.', 1)[0] + '.txt'
            with open(txt_filename, 'w', encoding='utf-8') as f:
                for detection in result:
                    f.write(detection[1] + '\n')
    else:
        print(f"no mask created for {os.path.basename(image_path)}, moving to undetected folder")
        undetected_folder = os.path.join(os.path.dirname(image_path), "_undetected")
        if not os.path.exists(undetected_folder):
            os.mkdir(undetected_folder)
        shutil.move(image_path, os.path.join(undetected_folder, os.path.basename(image_path)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='Path to the source directory of images.')
    parser.add_argument('--out', required=True, help='Output directory for masks.')
    parser.add_argument('--include-textfile', action='store_true', help='Include text file.')
    parser.add_argument('--corners', action='store_true', help='Include only masks touching corners.')
    parser.add_argument('--edges', action='store_true', help='Include masks touching edges.')
    parser.add_argument('--xpad', type=int, default=24, help='Horizontal padding.')
    parser.add_argument('--ypad', type=int, default=24, help='Vertical padding.')
    args = parser.parse_args()

    if args.corners and args.edges:
        print("Warning: Using both --corners and --edges is redundant; --edges will take precedence.")

    if not os.path.exists(args.out):
        os.mkdir(args.out)

    total_files = len([name for name in os.listdir(args.path) if name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))])
    processed_files = 0

    for filename in os.listdir(args.path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            full_path = os.path.join(args.path, filename)
            process_image(full_path, args.out, args.include_textfile, args.xpad, args.ypad, args.corners, args.edges)
            processed_files += 1
            print(f"Progress: {processed_files}/{total_files}")

if __name__ == "__main__":
    main()