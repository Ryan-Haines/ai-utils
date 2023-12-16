# script that takes input folder of images, output folder of images. copies images from input to copydir if they dont already exist in output.

import argparse
import os
import shutil

def collect_unmasked():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask-path", "-i", required=True, help="Path to the input images")
    parser.add_argument("--masked-images-path", "-o", required=True, help="Path to the masked images")
    parser.add_argument("--copyto", "-c", required=True, help="Directory to copy images")
    
    args = parser.parse_args()
    
    mask_path = args.mask_path
    masked_images_path = args.masked_images_path
    copy_to = args.copyto

    mask_files = set(os.path.splitext(f)[0] for f in os.listdir(mask_path) if os.path.isfile(os.path.join(mask_path, f)))
    masked_files = set(os.path.splitext(f)[0] for f in os.listdir(masked_images_path) if os.path.isfile(os.path.join(masked_images_path, f)))

    unmasked_files = mask_files - masked_files
    print(f"Found {len(unmasked_files)} unmasked files")

    possible_extensions = ['jpg', 'jpeg', 'png']

    for file in unmasked_files:
        src_path = None
        for ext in possible_extensions:
            # Check for both lowercase and uppercase extensions
            for case_ext in [ext, ext.upper()]:
                tentative_path = os.path.join(mask_path, f"{file}.{case_ext}")
                if os.path.isfile(tentative_path):
                    src_path = tentative_path
                    break
            if src_path:
                break

        if src_path:
            dest_path = os.path.join(copy_to, f"{file}{os.path.splitext(src_path)[1]}")
            shutil.copy2(src_path, dest_path)
        else:
            print(f"Could not find a matching file for {file}")


if __name__ == "__main__":
    collect_unmasked()

