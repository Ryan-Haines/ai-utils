import argparse
import os
import random
from PIL import Image
import shutil

def main(path, outpath, per_set, set_limit, min_width, min_height, ignore_ends, repick, first, last):
    if not os.path.exists(outpath):
        os.makedirs(outpath)

    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    selected_images = []
    
    existing_files = {f for f in os.listdir(outpath) if f.endswith(('jpg', 'png'))}

    for folder in folders:
        folder_path = os.path.join(path, folder)
        image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('jpg', 'png'))])

        if ignore_ends:
            image_files = image_files[1:-1]

        if first:
            image_files = image_files[:per_set]
        elif last:
            image_files = image_files[-per_set:]

        effective_per_set = per_set  # Initialize here for both conditions
        existing_from_this_folder = set()
        
        if repick:
            existing_from_this_folder = existing_files.intersection(set(os.listdir(os.path.join(path, folder))))
            
            if len(existing_from_this_folder) >= effective_per_set:
                continue

            # Remove existing images from this folder from the candidates
            image_files = list(set(image_files) - existing_from_this_folder)

            if not image_files:
                continue

        sampled_images = random.sample(image_files, min(effective_per_set - len(existing_from_this_folder), len(image_files))) if effective_per_set else [random.choice(image_files)]

        for img in sampled_images:
            img_path = os.path.join(folder_path, img)
            img_obj = Image.open(img_path)
            if img_obj.size[0] >= min_width and img_obj.size[1] >= min_height:
                selected_images.append((img_path, img))
                if repick:
                    print(f"Repicked: {img}")
                else:
                    print(f"Picked: {img}")

        if set_limit and len(selected_images) >= set_limit:
            break

    for img_path, img_name in selected_images:
        new_name = img_name
        while os.path.exists(os.path.join(outpath, new_name)):
            new_name = f"{img_name.split('.')[0]}_{random.randint(1, 1000)}.{img_name.split('.')[1]}"

        shutil.copy(img_path, os.path.join(outpath, new_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True)
    parser.add_argument('--outpath', required=True)
    parser.add_argument('--perSet', type=int, default=None)
    parser.add_argument('--setLimit', type=int, default=None)
    parser.add_argument('--minWidth', type=int, default=0)
    parser.add_argument('--minHeight', type=int, default=0)
    parser.add_argument('--ignore-ends', action='store_true')
    parser.add_argument('--repick', action='store_true')
    parser.add_argument('--first', action='store_true', help='Take from the start of each folder')
    parser.add_argument('--last', action='store_true', help='Take from the end of each folder')
    
    args = parser.parse_args()

    if args.first and args.last:
        parser.error("--first and --last are mutually exclusive. Choose one.")
    
    main(args.path, args.outpath, args.perSet, args.setLimit, args.minWidth, args.minHeight, args.ignore_ends, args.repick, args.first, args.last)
