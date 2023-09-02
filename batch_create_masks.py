import os
import argparse
from PIL import Image, ImageDraw
import easyocr
from tqdm import tqdm 

def is_touching_edges(x1, y1, x2, y2, img_width, img_height, xpad, ypad):
    return x1 <= xpad or y1 <= ypad or x2 >= img_width - xpad or y2 >= img_height - ypad

def is_touching_corners(x1, y1, x2, y2, img_width, img_height, xpad, ypad):
    corners = [(xpad, ypad), (img_width - xpad, ypad), (xpad, img_height - ypad), (img_width - xpad, img_height - ypad)]
    for cx, cy in corners:
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return True
    return False


def process_image(image_path, out_folder, include_textfile, xpad_detect, ypad_detect, xpad_box, ypad_box, corners=False, edges=False, only_largest=False, overwrite=False):
    mask_filename = os.path.join(out_folder, os.path.basename(image_path))
    if os.path.exists(mask_filename) and not overwrite:
        print(f"Mask already exists for {os.path.basename(image_path)}, skipping.")
        return
    
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    
    image = Image.open(image_path)
    width, height = image.size
    mask = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(mask)

    if xpad_detect is None:
        xpad_detect = int(width * 0.05)
    if ypad_detect is None:
        ypad_detect = int(height * 0.05)
    
    mask_created = False
    max_area = 0
    largest_detection = None
    
    for detection in result:
        top_left, top_right, bottom_right, bottom_left = detection[0]
        x1, y1 = top_left
        x2, y2 = bottom_right
        area = (x2 - x1) * (y2 - y1)

        should_draw = True
        
        if edges:
            should_draw = is_touching_edges(x1, y1, x2, y2, width, height, xpad_detect, ypad_detect)
        elif corners:
            should_draw = is_touching_corners(x1, y1, x2, y2, width, height, xpad_detect, ypad_detect)

        if should_draw:
            if only_largest:
                if area > max_area:
                    max_area = area
                    largest_detection = detection
            else:
                draw.rectangle([x1 - xpad_box, y1 - ypad_box, x2 + xpad_box, y2 + ypad_box], fill="black")
                mask_created = True
    
    if only_largest and largest_detection:
        x1, y1 = largest_detection[0][0]
        x2, y2 = largest_detection[0][2]
        draw.rectangle([x1 - xpad_box, y1 - ypad_box, x2 + xpad_box, y2 + ypad_box], fill="black")
        mask_created = True

    if mask_created:
        mask.save(mask_filename)
        
        if include_textfile:
            txt_filename = mask_filename.rsplit('.', 1)[0] + '.txt'
            with open(txt_filename, 'w', encoding='utf-8') as f:
                for detection in result:
                    f.write(detection[1] + '\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='Path to the source directory of images.')
    parser.add_argument('--out', required=True, help='Output directory for masks.')
    parser.add_argument('--include-textfile', action='store_true', help='Include text file.')
    parser.add_argument('--corners', action='store_true', help='Include only masks touching corners.')
    parser.add_argument('--edges', action='store_true', help='Include masks touching edges.')
    parser.add_argument('--only-largest', action='store_true', help='Only keep the largest detected mask.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing mask files.')
    parser.add_argument('--xpad-detect', type=int, default=None, help='Horizontal padding for detection.')
    parser.add_argument('--ypad-detect', type=int, default=None, help='Vertical padding for detection.')
    parser.add_argument('--xpad-box', type=int, default=0, help='Horizontal padding for bounding box.')
    parser.add_argument('--ypad-box', type=int, default=0, help='Vertical padding for bounding box.')
    args = parser.parse_args()
    
    if not os.path.exists(args.out):
        os.mkdir(args.out)

    image_files = [f for f in os.listdir(args.path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]
    
    tqdm.write(f"Total images to process: {len(image_files)}")

    for filename in tqdm(image_files, desc="Processing images"):
        full_path = os.path.join(args.path, filename)
        process_image(full_path, args.out, args.include_textfile, args.xpad_detect, args.ypad_detect, args.xpad_box, args.ypad_box, args.corners, args.edges, args.only_largest, args.overwrite)

if __name__ == "__main__":
    main()
