import os
import argparse
import cv2
from PIL import Image, ImageDraw
import easyocr
from tqdm import tqdm
import numpy as np
import itertools
import math

KEEP_BOXES = 1 #todo: make this a flag

def is_touching_edges(x1, y1, x2, y2, img_width, img_height, xpad, ypad):
    return x1 <= xpad or y1 <= ypad or x2 >= img_width - xpad or y2 >= img_height - ypad

def is_touching_corners(x1, y1, x2, y2, img_width, img_height, xpad, ypad):
    corners = [(xpad, ypad), (img_width - xpad, ypad), (xpad, img_height - ypad), (img_width - xpad, img_height - ypad)]
    for cx, cy in corners:
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return True
    return False

def nCr(n, r):
    return math.comb(n, r)

def read_image(image_path, use_color, use_cache, cache_folder, use_binary):
    reader = easyocr.Reader(['en'])
    
    if use_color:
        image = Image.open(image_path)
        result = reader.readtext(image_path)
    else:
        image = read_grayscale_image(image_path, use_cache, cache_folder, use_binary)
        gray_np = np.array(image)
        result = reader.readtext(gray_np)

    return image, result


def read_grayscale_image(image_path, use_cache, cache_folder, use_binary):
    if use_cache:
        cached_filename = os.path.join(cache_folder, os.path.basename(image_path))
        if os.path.exists(cached_filename):
            return Image.open(cached_filename)
        
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    if use_binary:
        _, gray = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    
    if use_cache:
        cv2.imwrite(cached_filename, gray)
    
    return Image.fromarray(gray)


def prepare_boxes(image, **kwargs):
    width, height = image.size
    total_area = width * height
    # If xpad_detect is None or not found, set it to 5% of the width
    xpad_detect = kwargs.get('xpad_detect')
    if xpad_detect is None:
        xpad_detect = int(width * 0.05)

    # If ypad_detect is None or not found, set it to 5% of the height
    ypad_detect = kwargs.get('ypad_detect')
    if ypad_detect is None:
        ypad_detect = int(height * 0.05)

    return {
        'total_area': total_area,
        'width': width,
        'height': height,
        'xpad_detect': xpad_detect,
        'ypad_detect': ypad_detect,
    }


def draw_boxes(result, draw, **kwargs):
    min_x = 0
    min_y = 0
    max_x = 0
    max_y = 0
    total_masked_area_percent = 0

    min_area = kwargs.get('min_area')  # Default value if not passed
    max_area = kwargs.get('max_area', 10)  # Default value if not passed
    only_largest = kwargs.get('only_largest', False)  # Default value if not passed
    contain_bounding_boxes = kwargs.get('contain_bounding_boxes', False)  # Default value if not passed
    text_direction = kwargs.get('text_direction', 'horizontal')  # Default value if not passed
    xpad_box = kwargs.get('xpad_box', 0)  # Default value if not passed
    ypad_box = kwargs.get('ypad_box', 0)  # Default value if not passed
    corners = kwargs.get('corners', False)  # Default value if not passed
    edges = kwargs.get('edges', False)  # Default value if not passed
    min_total_area = kwargs.get('min_total_area', 0.1)  # Default value if not passed
    xpad_detect = kwargs.get('xpad_detect')  # Assuming this is in box_settings
    ypad_detect = kwargs.get('ypad_detect')  # Assuming this is in box_settings
    width = kwargs.get('width')  # Assuming this is in box_settings
    height = kwargs.get('height')  # Assuming this is in box_settings
    total_area = kwargs.get('total_area')  # Assuming this is in box_settings
    was_mask_created = False
    detected_boxes = []

    for detection in result:
        top_left, top_right, bottom_right, bottom_left = detection[0]
        x1, y1 = top_left
        x2, y2 = bottom_right
        if (min_x == 0 and min_y == 0 and max_x == 0 and max_y == 0):
            min_x = x1
            min_y = y1
            max_x = x2
            max_y = y2

        box_width = x2 - x1  # Dimensions of the bounding box, renamed to avoid conflict
        box_height = y2 - y1  # Dimensions of the bounding box, renamed to avoid conflict
        is_horizontally_longer = box_width > box_height  # Use 'box_width' and 'box_height' here

        if text_direction == 'horizontal' and not is_horizontally_longer and not box_width == box_height:
            continue
        if text_direction == 'vertical' and is_horizontally_longer and not box_width == box_height:
            continue

        area = (x2 - x1) * (y2 - y1)
        area_percent = (area / total_area) * 100
        if area_percent < min_area or area_percent > max_area:
            print(f"\nArea percentage {area_percent} is not within the range of {min_area} and {max_area}.")
            continue

        should_draw = False
        if edges:
            should_draw = is_touching_edges(x1, y1, x2, y2, width, height, xpad_detect, ypad_detect)
            if should_draw:
                x1_draw, y1_draw, x2_draw, y2_draw = x1, y1, x2, y2
                if x1 <= xpad_detect:
                    x1_draw = 0
                if y1 <= ypad_detect:
                    y1_draw = 0
                if x2 >= (width - xpad_detect):
                    x2_draw = width
                if y2 >= (height - ypad_detect):
                    y2_draw = height
                draw.rectangle([x1_draw, y1_draw, x2_draw, y2_draw], fill="black")
                was_mask_created = True
                total_masked_area_percent += area_percent
        elif corners:
            should_draw = is_touching_corners(x1, y1, x2, y2, width, height, xpad_detect, ypad_detect)
        else:
            should_draw = True

        if should_draw and not edges:
            detected_boxes.append((x1, y1, x2, y2))
            min_x = min(min_x, x1)
            min_y = min(min_y, y1)
            max_x = max(max_x, x2)
            max_y = max(max_y, y2)

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
                was_mask_created = True
                total_masked_area_percent += area_percent

    if only_largest and largest_detection:
        x1, y1 = largest_detection[0][0]
        x2, y2 = largest_detection[0][2]
        x1_draw = max(x1 - xpad_box, 0)
        y1_draw = max(y1 - ypad_box, 0)
        x2_draw = min(x2 + xpad_box, width)
        y2_draw = min(y2 + ypad_box, height)
        draw.rectangle([x1_draw, y1_draw, x2_draw, y2_draw], fill="black")
        was_mask_created = True
        # print(f"\nDrawing bounding box for largest detection {detection[1]}")
        total_masked_area_percent += area_percent

    largest_valid_combination = None
    largest_valid_area = 0

    if contain_bounding_boxes and len(detected_boxes) > 1:
        # print(f"\nFound {len(detected_boxes)} bounding boxes. Checking if they can be combined.")
        
        largest_valid_combination = None  # Initialize
        largest_valid_area = 0  # Initialize
        combinations_area = []  # List to store all possible combinations and their areas

        combinations_area = []
        for box1, box2 in itertools.combinations(detected_boxes, 2):
            min_x = min(box1[0], box2[0])
            min_y = min(box1[1], box2[1])
            max_x = max(box1[2], box2[2])
            max_y = max(box1[3], box2[3])
            area_comb = (max_x - min_x) * (max_y - min_y)
            combinations_area.append((area_comb, (box1, box2)))

        combinations_area.sort(reverse=True)  # Sort by area, largest to smallest
        largest_valid_combination = None
        largest_valid_area = 0

        for area_comb, boxes in combinations_area:
            area_percent = (area_comb / total_area) * 100
            if area_percent <= max_area:
                largest_valid_combination = (min(boxes[0][0], boxes[1][0]), 
                                            min(boxes[0][1], boxes[1][1]), 
                                            max(boxes[0][2], boxes[1][2]), 
                                            max(boxes[0][3], boxes[1][3]))
                largest_valid_area = area_comb
                contributing_boxes = boxes  # Store the contributing boxes
                break

        if largest_valid_combination:
            print(f"\nThe largest valid bounding box was found. Area percentage: {total_masked_area_percent}")
            min_x, min_y, max_x, max_y = largest_valid_combination
            # White out the areas not covered by the largest bounding box
            draw.rectangle([0, 0, width, min_y], fill="white")
            draw.rectangle([0, max_y, width, height], fill="white")
            draw.rectangle([0, min_y, min_x, max_y], fill="white")
            draw.rectangle([max_x, min_y, width, max_y], fill="white")
            # Finally, draw the largest valid bounding box
            if(kwargs.get('draw_contain', True)):
                # breakpoint()
                print(f"\nmin total area: {kwargs.get('min_total_area', 0.1)}")
                if (kwargs.get('contain_under_min', True) and total_masked_area_percent < kwargs.get('min_total_area', 0.1)) or not kwargs.get('contain_under_min', True):
                    draw.rectangle([largest_valid_combination[0], largest_valid_combination[1], largest_valid_combination[2], largest_valid_combination[3]], fill="black")    
                    was_mask_created = True
        else:
            # print(f"\nNo valid bounding box found. Keeping the closest {KEEP_BOXES} bounding boxes to the corner. modify KEEP_BOXES in batch_create_masks.py to change")
            # Calculate the distance of each bounding box to the top-left corner (0, 0)
            distances_to_corner = [(box[0]**2 + box[1]**2, box) for box in detected_boxes]
            distances_to_corner.sort()
            # Keep only the closest N boxes (todo: determined by --keep-boxes flag)
            keep_boxes = int(KEEP_BOXES)  # Replace with the actual flag value
            boxes_to_keep = [box for _, box in distances_to_corner[:keep_boxes]]
            for box in detected_boxes:
                if box not in boxes_to_keep:
                    draw.rectangle([box[0], box[1], box[2], box[3]], fill="white")


    return was_mask_created, total_masked_area_percent

def save_mask(mask, mask_filename, include_textfile, result):
    mask.save(mask_filename)
    
    if include_textfile:
        txt_filename = mask_filename.rsplit('.', 1)[0] + '.txt'
        with open(txt_filename, 'w', encoding='utf-8') as f:
            for detection in result:
                f.write(detection[1] + '\n')

MAX_COMBINATIONS = 2**15

def process_image(**kwargs):
    print(f"\nProcessing {os.path.basename(kwargs['image_path'])}")
    image_path = kwargs['image_path']
    out_folder = kwargs['out_folder']
    overwrite = kwargs.get('overwrite', False)

    mask_filename = os.path.join(out_folder, os.path.basename(image_path))
    if os.path.exists(mask_filename) and not overwrite:
        print(f"\nMask already exists for {os.path.basename(image_path)}, skipping.")
        return
    
    image, result = read_image(
        image_path=image_path,
        use_color=kwargs.get('use_color', True),
        use_cache=kwargs.get('use_cache', False),
        cache_folder=kwargs.get('cache_folder'),
        use_binary=kwargs.get('use_binary', False),
    )

    box_settings = prepare_boxes(image, **kwargs)
    mask = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(mask)


    all_kwargs = box_settings.copy()  # Start with the contents of box_settings

    # Update all_kwargs only for keys that have non-None values in kwargs
    for key, value in kwargs.items():
        if value is not None:
            all_kwargs[key] = value

    mask_created = False

    mask_created, total_masked_area_percent = draw_boxes(
        result=result,
        draw=draw,
        **all_kwargs,
    )

    if mask_created and total_masked_area_percent >= kwargs.get('min_total_area', 0.1):
        save_mask(mask, mask_filename, kwargs.get('include_textfile', True), result)
    else:
        print(f"\nMask was not created for {os.path.basename(image_path)}, total masked area percentage was {total_masked_area_percent} and threshold was {kwargs.get('min_total_area', 0.1)}")

    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='Path to the source directory of images.')
    parser.add_argument('--out', required=True, help='Output directory for masks.')
    parser.add_argument('--include-textfile', action='store_true', help='Include text file.')
    parser.add_argument('--corners', action='store_true', help='Include only masks touching corners.')
    parser.add_argument('--edges', action='store_true', help='Include masks touching edges.')
    parser.add_argument('--only-largest', action='store_true', help='Only keep the largest detected mask.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing mask files.')
    parser.add_argument('--xpad-detect', type=int, default=256, help='Horizontal padding for detection.')
    parser.add_argument('--ypad-detect', type=int, default=256, help='Vertical padding for detection.')
    parser.add_argument('--xpad-box', type=int, default=0, help='Horizontal padding for bounding box.')
    parser.add_argument('--ypad-box', type=int, default=0, help='Vertical padding for bounding box.')
    parser.add_argument('--min-area', type=float, default=0.1, help='Minimum area as a percentage to include bounding box. Default is 1%.')
    parser.add_argument('--max-area', type=float, default=10, help='Maximum area as a percentage to include bounding box. Default is 10%.')
    parser.add_argument('--use-color', type=bool, default=True, help='Use color images instead of grayscale.')
    parser.add_argument('--use-cache', action='store_true', help='Cache grayscale images to disk.')
    parser.add_argument('--use-binary', action='store_true', help='Use binary black/white instead of grayscale.')
    parser.add_argument('--text-direction', default='horizontal', choices=['horizontal', 'vertical', 'any'], help='Orientation of the bounding box. Choices are horizontal, vertical, or any')
    parser.add_argument('--min-total-area', type=float, default=0.1, help='Minimum total area as a percentage to create masks for the image. Default is 0.1%. Recommended range 10-20%. Useful for images with multiple bounding boxes where sometimes one of the boxes is missing.')
    parser.add_argument('--contain', action='store_true', help='Measure around all bounding boxes to find the largest within the --max-area. Useful for eliminating false positives.')
    parser.add_argument('--draw-contain', action='store_true', help='Use in combination with --contain. Draw a bounding box around all bounding boxes. Useful for images with multiple bounding boxes where sometimes one of the middle boxes is missing.')
    parser.add_argument('--contain-under-min', action='store_true', help='Use in combination with --contain and --draw-contain. Only draws contain if the detected boxes have less than the total area already.')


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
    tqdm.write(f"Measure around all bounding boxes to find the largest within the --max-area: {args.contain}")
    tqdm.write(f"Draw a bounding box around all bounding boxes: {args.draw_contain}")
    tqdm.write(f"Only draws contain if the detected boxes have less than the total area already: {args.contain_under_min}")


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
            'min_total_area': args.min_total_area,
            'contain_bounding_boxes': args.contain,
            'draw_contain': args.draw_contain,
            'contain_under_min': args.contain_under_min,
        }
        process_image(**args_dict)

if __name__ == "__main__":
    main()
