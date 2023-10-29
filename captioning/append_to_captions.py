import argparse
import os

def append_text_to_files(path: str, append_text: str):
    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            with open(os.path.join(path, filename), "a") as f:
                f.write(append_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Directory path to process text files.")
    parser.add_argument("--append", required=True, help="Text to append to each file.")
    
    args = parser.parse_args()
    append_text_to_files(args.path, args.append)






