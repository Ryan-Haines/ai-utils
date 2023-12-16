import os
import shutil
import argparse

def handle_files(path, maskpath, moveoutpath, unmaskedpath, delete_flag):
    # Create directories if they do not exist
    if moveoutpath and not os.path.exists(moveoutpath):
        os.mkdir(moveoutpath)
    if unmaskedpath and not os.path.exists(unmaskedpath):
        os.mkdir(unmaskedpath)

    # List of image files in maskpath
    masked_files = set(os.listdir(maskpath))
    
    for filename in os.listdir(path):
        original_file = os.path.join(path, filename)

        # File exists in both path and maskpath
        if filename in masked_files:
            if moveoutpath:
                shutil.move(original_file, os.path.join(moveoutpath, filename))

        # File does not exist in maskpath
        else:
            if delete_flag:
                os.remove(original_file)
                print(f"Deleted image without matching mask: {filename}")
            elif unmaskedpath:
                shutil.move(original_file, os.path.join(unmaskedpath, filename))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True, help='Path to the source directory of images.')
    parser.add_argument('--moveout', action='store_true' help='Move images to path_moveout, if they have a matching mask.')
    parser.add_argument('--maskpath', help='Path to the directory of masked images.')
    parser.add_argument('--delete', action='store_true', help='Delete flag for destructive action.')

    args = parser.parse_args()

    # Update moveoutpath, unmaskedpath, and maskpath based on path
    moveoutpath = args.moveoutpath if args.moveoutpath else args.path + '_moveout'
    unmaskedpath = args.path.rstrip('/') + '_unmasked'
    maskpath = args.maskpath if args.maskpath else args.path + '_masked'

    if args.delete:
        user_input = input("WARNING! This is a destructive action, and will delete training images without a matching image mask. Are you sure you wish to continue? Type YES in all caps to continue: ")
        if user_input != "YES":
            print("Aborting.")
            exit()

    handle_files(args.path, maskpath, moveoutpath, unmaskedpath, args.delete)
