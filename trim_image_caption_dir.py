import os
import argparse
import re
import shutil

def main(path, delete_images, delete_text, move_captions_to, move_images_to, dry_run):
    image_exts = ['png', 'jpg', 'jpeg', 'gif', 'webm']
    text_files = set()
    image_files = set()
    unmatched_images = []
    unmatched_texts = []

    for filename in os.listdir(path):
        name, ext = os.path.splitext(filename)
        ext = ext[1:]

        if ext in image_exts:
            image_files.add(name)
        elif ext == 'txt':
            text_files.add(name)

    def move_file(src, dest, filename):
        if dry_run:
            print(f"Would move: {src} to {dest}")
        else:
            shutil.move(src, dest)
            print(f"Moved: {filename}")

    def handle_files(files, extensions, delete, move_to_path, unmatched_list):
        for file in files:
            unmatched_list.append(file)
            for ext in extensions:
                file_path = os.path.join(path, f"{file}.{ext}")
                if os.path.exists(file_path):
                    if delete:
                        if dry_run:
                            print(f"Would remove: {file_path}")
                        else:
                            os.remove(file_path)
                            break
                    elif move_to_path:
                        dest_path = os.path.join(move_to_path, f"{file}.{ext}")
                        move_file(file_path, dest_path, file_path)
                        break

    handle_files(image_files - text_files, image_exts, delete_images, move_images_to, unmatched_images)
    handle_files(text_files - image_files, ['txt'], delete_text, move_captions_to, unmatched_texts)

    print("----- START Images with no matching text files -----")
    print("\n".join(unmatched_images))
    print("----- END Images with no matching text files -----")
    print("----- START Text files with no matching image files -----")
    print("\n".join(unmatched_texts))
    print("----- END Text files with no matching image files -----")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='Directory path to search')
    parser.add_argument('--delete-images', '-di', action='store_true', help='Delete unmatched images')
    parser.add_argument('--delete-text', '-dt', action='store_true', help='Delete unmatched text files')
    parser.add_argument('--movecaptionsto', '-mvc', type=str, help='Move unmatched captions to this directory')
    parser.add_argument('--moveimagesto', '-mvi', type=str, help='Move unmatched images to this directory')
    parser.add_argument('--dry-run', '-dr', action='store_true', help='Only print what would be done, without making changes')
    args = parser.parse_args()

    if not args.dry_run:
        confirmation_required = args.moveimagesto or args.movecaptionsto
        if confirmation_required:
            user_input = input("Confirm action? [y/N]: ").strip().lower()
            if user_input != 'y':
                print("Action cancelled.")
                exit(1)

    main(args.path, args.delete_images, args.delete_text, args.movecaptionsto, args.moveimagesto, args.dry_run)
