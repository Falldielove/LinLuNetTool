import os

def save_last_path(path):
    with open('last_path.txt', 'w') as f:
        f.write(path)

def get_last_path():
    if os.path.exists('last_path.txt'):
        with open('last_path.txt', 'r') as f:
            return f.read().strip()
    return None
