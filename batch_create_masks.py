import os
import argparse
import cv2
from PIL import Image, ImageDraw
import easyocr
from tqdm import tqdm
import numpy as np

def is_touching_edges(x1, y1, x2, y2, img_width, img_height, xpad, ypad):
    return x1 <= xpad or y1 <= ypad or x2 >= img_width - xpad or y2 >= img_height - ypad

def is_touching_corners(x1, y1, x2, y2, img_width, img_height, xpad, ypad):
    corners = [(xpad, ypad), (img_width - xpad, ypad), (xpad, img_height - ypad), (img_width - xpad, img_height - ypad)]
    for cx, cy in corners:
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return True
    return False


def process_image(**kwargs):
    image_path = kwargs.get('image_path')
    out_folder = kwargs.get('out_folder')
    include_textfile = kwargs.get('include_textfile', True)
    use_color = kwargs.get('use_color', True)
    use_binary = kwargs.get('use_binary', False)
    use_cache = kwargs.get('use_cache', False)
    cache_folder = kwargs.get('cache_folder')
    xpad_detect = kwargs.get('xpad_detect')
    ypad_detect = kwargs.get('ypad_detect')
    xpad_box = kwargs.get('xpad_box', 0)
    ypad_box = kwargs.get('ypad_box', 0)
    corners = kwargs.get('corners', False)
    edges = kwargs.get('edges', False)
    only_largest = kwargs.get('only_largest', False)
    overwrite = kwargs.get('overwrite', False)
    min_area = kwargs.get('min_area', 0.1)
    max_area = kwargs.get('max_area', 10)
    text_direction = kwargs.get('text_direction', 'horizontal')
    minimum_total_area = kwargs.get('minimum_total_area', 0.1)


    mask_filename = os.path.join(out_folder, os.path.basename(image_path))
    if os.path.exists(mask_filename) and not overwrite:
        print(f"\nMask already exists for {os.path.basename(image_path)}, skipping.")
        return

    print(f"\nProcessing {os.path.basename(image_path)}")
    
    if use_color:  # color is default
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_path)
        image = Image.open(image_path)  # Open color image
    else:
        if use_cache:
            cached_filename = os.path.join(cache_folder, os.path.basename(image_path))
            if os.path.exists(cached_filename):
                gray_pil = Image.open(cached_filename)  # Use cached image (No modification)
            else:
                img = cv2.imread(image_path)
                if use_binary:
                    _, binary = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY)
                    cv2.imwrite(cached_filename, binary)
                    gray_pil = Image.fromarray(binary)
                else:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(cached_filename, gray)
                    gray_pil = Image.fromarray(gray)
        else:
            img = cv2.imread(image_path)
            if use_binary:
                _, binary = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 128, 255, cv2.THRESH_BINARY)
                gray_pil = Image.fromarray(binary)
            else:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_pil = Image.fromarray(gray)


        # Convert PIL Image to numpy array before reading
        gray_np = np.array(gray_pil)
        
        reader = easyocr.Reader(['en'])
        result = reader.readtext(gray_np)  # Pass numpy array instead of PIL object
        image = gray_pil  # Use already-loaded grayscale PIL object

    width, height = image.size
    mask = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(mask)

    if xpad_detect is None:
        xpad_detect = int(width * 0.05)
    if ypad_detect is None:
        ypad_detect = int(height * 0.05)
    
    mask_created = False
    largest_detection = None
    
    total_masked_area_percent = 0  
    total_area = width * height 
    print(f"With this many detections: {len(result)}")
    for detection in result:
        top_left, top_right, bottom_right, bottom_left = detection[0]
        x1, y1 = top_left
        x2, y2 = bottom_right
        box_width = x2 - x1  # Dimensions of the bounding box, renamed to avoid conflict
        box_height = y2 - y1  # Dimensions of the bounding box, renamed to avoid conflict

        is_horizontally_longer = box_width > box_height  # Use 'box_width' and 'box_height' here

        if text_direction == 'horizontal' and not is_horizontally_longer and not box_width == box_height:
            print(f"Text direction is horizontal but mask is vertical, skipping.")
            continue
        if text_direction == 'vertical' and is_horizontally_longer and not box_width == box_height:
            print(f"Text direction is vertical but mask is horizontal, skipping.")
            continue
        

        area = (x2 - x1) * (y2 - y1)

        area_percent = (area / total_area) * 100
        if area_percent < min_area or area_percent > max_area:
            print(f"Area percentage {area_percent} is not within the range of {min_area} and {max_area}.")
            continue

        should_draw = False
        if edges:
            should_draw = is_touching_edges(x1, y1, x2, y2, width, height, xpad_detect, ypad_detect)
        elif corners:
            should_draw = is_touching_corners(x1, y1, x2, y2, width, height, xpad_detect, ypad_detect)
        else:
            should_draw = True

        if should_draw:
            if only_largest:
                if area > max_area:
                    max_area = area
                    largest_detection = detection
            else:
                x1_draw = max(x1 - xpad_box, 0)
                y1_draw = max(y1 - ypad_box, 0)
                x2_draw = min(x2 + xpad_box, width)
                y2_draw = min(y2 + ypad_box, height)
                draw.rectangle([x1_draw, y1_draw, x2_draw, y2_draw], fill="black")
                # print(f"\nDrawing bounding box for {detection[1]}")
                total_masked_area_percent += area_percent
                mask_created = True

    if only_largest and largest_detection:
        x1, y1 = largest_detection[0][0]
        x2, y2 = largest_detection[0][2]
        x1_draw = max(x1 - xpad_box, 0)
        y1_draw = max(y1 - ypad_box, 0)
        x2_draw = min(x2 + xpad_box, width)
        y2_draw = min(y2 + ypad_box, height)
        draw.rectangle([x1_draw, y1_draw, x2_draw, y2_draw], fill="black")
        print(f"Drawing bounding box for largest detection {detection[1]}")
        total_masked_area_percent += area_percent
        mask_created = True

    if mask_created and total_masked_area_percent >= minimum_total_area:
        mask.save(mask_filename)
        
        if include_textfile:
            txt_filename = mask_filename.rsplit('.', 1)[0] + '.txt'
            with open(txt_filename, 'w', encoding='utf-8') as f:
                for detection in result:
                    f.write(detection[1] + '\n')
    else:
        print(f"Mask was not created for {os.path.basename(image_path)}, total masked area percentage: {total_masked_area_percent}, minimum save mask threshold: {minimum_total_area}.")

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
    parser.add_argument('--min-area', type=float, default=1, help='Minimum area as a percentage to include bounding box. Default is 1%.')
    parser.add_argument('--max-area', type=float, default=10, help='Maximum area as a percentage to include bounding box. Default is 10%.')
    parser.add_argument('--use-color', action='store_true', default=True, help='Use color images instead of grayscale.')
    parser.add_argument('--use-cache', action='store_true', help='Cache grayscale images to disk.')
    parser.add_argument('--use-binary', action='store_true', help='Use binary black/white instead of grayscale.')
    parser.add_argument('--text-direction', default='horizontal', choices=['horizontal', 'vertical', 'any'], help='Orientation of the bounding box. Choices are horizontal, vertical, or any')
    parser.add_argument('--min-total-area', type=float, default=0.1, help='Minimum total area as a percentage to create masks for the image. Default is 0.1%. Recommended range 10-20%. Useful for images with multiple bounding boxes where sometimes one of the boxes is missing.')


    args = parser.parse_args()
    
    if not os.path.exists(args.out):
        os.mkdir(args.out)

    if args.use_cache:
        cache_folder = args.path + '_grayscale_cache'
        if not os.path.exists(cache_folder):
            os.mkdir(cache_folder)
    else:
        cache_folder = None


    image_files = [f for f in os.listdir(args.path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]
    
    tqdm.write(f"Total images to process: {len(image_files)}")
    tqdm.write(f"Output directory: {args.out}")
    tqdm.write(f"Include text file: {args.include_textfile}")
    tqdm.write(f"Horizontal padding for detection: {args.xpad_detect}")
    tqdm.write(f"Vertical padding for detection: {args.ypad_detect}")
    tqdm.write(f"Horizontal padding for bounding box: {args.xpad_box}")
    tqdm.write(f"Vertical padding for bounding box: {args.ypad_box}")
    tqdm.write(f"Include only masks touching corners: {args.corners}")
    tqdm.write(f"Include only masks touching edges: {args.edges}")
    tqdm.write(f"Only keep the largest detected mask: {args.only_largest}")
    tqdm.write(f"Overwrite existing mask files: {args.overwrite}")
    tqdm.write(f"Minimum area as a percentage to include bounding box: {args.min_area}")
    tqdm.write(f"Maximum area as a percentage to include bounding box: {args.max_area}")
    tqdm.write(f"Use color images instead of grayscale: {args.use_color}")
    tqdm.write(f"Cache grayscale images to disk: {args.use_cache}")
    tqdm.write(f"Use binary black/white instead of grayscale: {args.use_binary}")
    tqdm.write(f"Orientation of the bounding box: {args.text_direction}")
    tqdm.write(f"Minimum total area as a percentage to create masks for the image: {args.min_total_area}")


    for filename in tqdm(image_files, desc="Processing images"):
        full_path = os.path.join(args.path, filename)
        args_dict = {
            'image_path': full_path,
            'out_folder': args.out,
            'include_textfile': args.include_textfile,
            'use_color': args.use_color,
            'use_binary': args.use_binary,
            'use_cache': args.use_cache,
            'cache_folder': cache_folder,
            'xpad_detect': args.xpad_detect,
            'ypad_detect': args.ypad_detect,
            'xpad_box': args.xpad_box,
            'ypad_box': args.ypad_box,
            'corners': args.corners,
            'edges': args.edges,
            'only_largest': args.only_largest,
            'overwrite': args.overwrite,
            'min_area': args.min_area,
            'max_area': args.max_area,
            'text_direction': args.text_direction,
            'minimum_total_area': args.min_total_area,
        }
        process_image(**args_dict)

if __name__ == "__main__":
    main()
