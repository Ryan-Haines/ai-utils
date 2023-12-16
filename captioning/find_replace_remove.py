# python find_replace_remove.py -c path_to_config.json --path path_to_directory
import os
import json
import argparse
def process_file(file_path, remove_list, replace_list):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    log_info = f"In file {file_path}, "
    removals = []
    replacements = []
    for removal in remove_list:
        if removal in content:
            content = content.replace(removal, '')
            removals.append(removal)
    for find, replace in replace_list:
        if find in content:
            content = content.replace(find, replace)
            replacements.append((find, replace))
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    if removals:
        log_info += f"removed {', '.join(removals)}, "
    if replacements:
        log_info += ', '.join([f"renamed {find} to {replace}" for find, replace in replacements])
    if not removals and not replacements:
        log_info += "no changes made"
    return log_info
def main(config_path, directory_path):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    remove_list = config.get('remove', [])
    replace_list = config.get('replace', [])
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            log_info = process_file(file_path, remove_list, replace_list)
            if 'no changes made' not in log_info:
                print(log_info)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text replacement script.")
    parser.add_argument("-c", "--config", required=True, help="Path to the JSON configuration file.")
    parser.add_argument("--path", required=True, help="Path to the directory containing text files.")
    args = parser.parse_args()
    
    main(args.config, args.path)
