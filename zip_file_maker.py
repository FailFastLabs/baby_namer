import os
import fnmatch
import zipfile
from gitignore_parser import parse_gitignore

def zipdir(path, ziph, gitignore):
    # ziph is zipfile handle
    whitelist_files = ['./data/STATE.CA.TXT', './data/yob2020.txt']
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                if not gitignore(filepath) and not os.path.islink(filepath) and ".git" not in filepath or filepath in whitelist_files:
                    ziph.write(filepath)
                    print(f"adding {filepath}")  # Add this line
            except ValueError:
                print(f"Skipping symbolic link or outside file: {filepath}")

def main():
    gitignore = parse_gitignore('.gitignore', base_dir='.')
    zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('.', zipf, gitignore)
    zipf.close()

def main():
    gitignore = parse_gitignore('.gitignore', base_dir='.')
    zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('.', zipf, gitignore)
    zipf.close()

if __name__ == '__main__':
    main()
