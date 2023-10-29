import argparse
import os
import re
import ast

def process_txt(input_folder, clean, strip_text, strip_regex, replace_tuples):
    image_extensions = ['.jpg', '.png', '.jpeg', '.gif', '.bmp', '.webp']
    image_extensions += [ext.upper() for ext in image_extensions]
    
    for root, _, files in os.walk(input_folder):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            
            if file_extension.lower() in image_extensions:
                txt_file = f"{file_name}.txt"
                txt_path = os.path.join(root, txt_file)
                if os.path.exists(txt_path):
                    
                    if clean:
                        file_name = re.sub(r'\d', '', file_name)
                        file_name = file_name.replace("-", " ").replace("_", " ")
                    
                    if strip_text:
                        file_name = file_name.replace(strip_text, "")
                    
                    if strip_regex:
                        file_name = re.sub(strip_regex, '', file_name)

                    for find_str, replace_str in replace_tuples:
                        file_name = file_name.replace(find_str, replace_str)

                    file_name = re.sub(' +', ' ', file_name)  # Compress multiple spaces to a single space

                    append_text = f", {file_name}"
                    
                    with open(txt_path, 'a') as f:
                        f.write(append_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-folder', required=True, help='Root folder to start the directory walk')
    parser.add_argument('--clean', action='store_true', help='Remove numbers and replace hyphens/underscores with spaces')
    parser.add_argument('--strip', type=str, default=None, help='Text to remove from the file name')
    parser.add_argument('--stripRegex', type=str, default=None, help='Regular expression to remove from the file name')
    parser.add_argument('--replaceTuples', type=ast.literal_eval, default=[], help='Tuples for find/replace operations')
    args = parser.parse_args()

    try:
        if not all(isinstance(t, tuple) and len(t) == 2 for t in args.replaceTuples):
            raise ValueError("Invalid format: --replaceTuples must be a list of 2-element tuples.")
    except (ValueError, SyntaxError):
        print("Error: Invalid format for --replaceTuples. Expected a list of 2-element tuples.")
        exit(1)
    
    process_txt(args.input_folder, args.clean, args.strip, args.stripRegex, args.replaceTuples)
