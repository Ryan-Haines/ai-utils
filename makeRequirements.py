import ast
import argparse

def get_imports(filepath):
    imports = []
    with open(filepath, "r") as src:
        tree = ast.parse(src.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            for n in node.names:
                imports.append(n.name if node.level == 0 else f"{node.module}.{n.name}")
    return imports

def write_requirements(script_path):
    imports = get_imports(script_path)
    std_libs = set(['os', 'argparse', 'sys', 'math', 're', 'datetime', 'ast'])
    external_libs = [lib for lib in imports if lib.split('.')[0] not in std_libs]

    with open("requirements.txt", "w") as f:
        for lib in external_libs:
            f.write(f"{lib}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--script-path', required=True, help='Path to the Python script.')
    args = parser.parse_args()
    write_requirements(args.script_path)
