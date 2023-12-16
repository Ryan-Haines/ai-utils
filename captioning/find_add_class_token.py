# python find_add_class_token.py --path "/path/to/directory" --search "foo" "bar" --prepend "Hello"

import argparse
import os

def process_files(path, search_terms, prepend, append):
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            file_path = os.path.join(path, filename)
            with open(file_path, 'r+') as file:
                content = file.read()

                if any(term in content for term in search_terms):
                    print(f"Match found in {filename}")
                else:
                    new_content = f"{prepend}{content}{append}" if prepend else f"{content}{append}"
                    file.seek(0)
                    file.write(new_content)
                    file.truncate()

                    action = "Prepended" if prepend else "Appended"
                    print(f"{action} to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Process .txt files in a directory.")
    parser.add_argument('--path', type=str, required=True, help="Directory path to search for .txt files.")
    parser.add_argument('--search', nargs='+', required=True, help="List of strings to search in the files.")
    parser.add_argument('--prepend', type=str, help="String to prepend to the file content.")
    parser.add_argument('--append', type=str, help="String to append to the file content.")

    args = parser.parse_args()

    if not args.prepend and not args.append:
        raise ValueError("Either --prepend or --append argument is required")

    process_files(args.path, args.search, args.prepend, args.append)

if __name__ == "__main__":
    main()
