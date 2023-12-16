import argparse
import os
from PIL import Image, UnidentifiedImageError
import shutil
import Levenshtein

# def main(image_path, mask_path):
#     image_files = [f for f in os.listdir(image_path) if f.endswith(('jpg', 'png', 'jpeg'))]
#     mask_files = [f for f in os.listdir(mask_path) if f.endswith(('jpg', 'png', 'jpeg'))]
#     mask_dimensions = {}
    
#     for mask in mask_files:
#         try:
#             with Image.open(os.path.join(mask_path, mask)) as img:
#                 dimensions = img.size
#             mask_dimensions[dimensions] = mask
#         except UnidentifiedImageError:
#             continue
    
#     # print mask dimensions
#     print("mask dimensions:")
#     for dim in mask_dimensions:
#         print(dim)

#     for image in image_files:
#         if image not in mask_files:
#             try:
#                 with Image.open(os.path.join(image_path, image)) as img:
#                     dimensions = img.size
#                 if dimensions in mask_dimensions:
#                     source_mask = os.path.join(mask_path, mask_dimensions[dimensions])
#                     target_mask = os.path.join(mask_path, image)
#                     shutil.copy(source_mask, target_mask)
#                     print(f"guessed mask for {image}")
#                 else:
#                     print(f"could not guess mask for {image}")
#                     print(f"dimensions: {dimensions}")
#             except UnidentifiedImageError:
#                 continue

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--path', required=True)
#     parser.add_argument('--out', required=True)
    
#     args = parser.parse_args()
#     main(args.path, args.out)

def main(image_path, mask_path):
    image_files = [f for f in os.listdir(image_path) if f.lower().endswith(('jpg', 'png', 'jpeg'))]
    mask_files = [f for f in os.listdir(mask_path) if f.lower().endswith(('jpg', 'png', 'jpeg'))]
    mask_dimensions = {}
    
    for mask in mask_files:
        try:
            with Image.open(os.path.join(mask_path, mask)) as img:
                dimensions = img.size
            mask_dimensions.setdefault(dimensions, []).append(mask)
        except UnidentifiedImageError:
            continue

    for image in image_files:
        if image not in mask_files:
            try:
                with Image.open(os.path.join(image_path, image)) as img:
                    dimensions = img.size
                if dimensions in mask_dimensions:
                    closest_mask = min(mask_dimensions[dimensions], key=lambda m: Levenshtein.distance(image, m))
                    source_mask = os.path.join(mask_path, closest_mask)

                    # Copy the mask to the mask directory, but rename it according to the original image
                    target_mask = os.path.join(mask_path, image)
                    shutil.copy(source_mask, target_mask)

                    print(f"Guessed mask for {image} was {closest_mask}, saved as {image}")
                else:
                    print(f"Could not guess mask for {image}")
                    print(f"Dimensions: {dimensions}")
            except UnidentifiedImageError:
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mask guessing utility.")
    parser.add_argument('--path', required=True, help="Path to the directory containing the images.")
    parser.add_argument('--out', required=True, help="Path to the directory containing the masks.")

    args = parser.parse_args()
    main(args.path, args.out)