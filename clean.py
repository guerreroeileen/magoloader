import os
import shutil

def clean():
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                print(f"Removed {os.path.join(root, d)}")
        for f in files:
            if f.endswith(".pyc"):
                os.remove(os.path.join(root, f))
                print(f"Removed {os.path.join(root, f)}")

if __name__ == "__main__":
    clean()
