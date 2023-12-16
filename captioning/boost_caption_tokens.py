import argparse
import os
import re

def boost_caption_token(path: str, regex: str):
    pattern = re.compile(regex)
    
    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            filepath = os.path.join(path, filename)
            
            with open(filepath, "r+") as f:
                content = f.read()
                matches = pattern.findall(content)
                
                if matches:
                    content = pattern.sub("", content)
                    new_content = ",".join(matches) + "," + content  # Added comma
                    
                    f.seek(0)
                    f.write(new_content)
                    f.truncate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Directory path to process text files.")
    parser.add_argument("--regex", required=True, help="Regex pattern to match tokens.")
    
    args = parser.parse_args()
    boost_caption_token(args.path, args.regex)
