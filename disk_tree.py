#!/usr/bin/env python3
import os
import sys
import argparse
from colorama import init, Fore, Style
import humanize

# Initialize colorama
init(autoreset=True)

# File type color mapping
TYPE_COLORS = {
    'folder': Fore.BLUE,
    'image': Fore.YELLOW,
    'text': Fore.CYAN,
    'audio': Fore.MAGENTA,
    'video': Fore.RED,
    'other': Fore.WHITE,
}

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
TEXT_EXTS  = {'.txt', '.md', '.py', '.java', '.c', '.cpp', '.html', '.css', '.js'}
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.aac'}
VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov'}

# Size-based color thresholds (in bytes)
def size_color(size):
    if size > 10 * 1024**2:      # >10 MB
        return Fore.RED
    if size > 1 * 1024**2:       # >1 MB
        return Fore.YELLOW
    return Fore.GREEN            # <=1 MB

def get_type_color(path, is_dir):
    if is_dir:
        return TYPE_COLORS['folder']
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGE_EXTS: return TYPE_COLORS['image']
    if ext in TEXT_EXTS:  return TYPE_COLORS['text']
    if ext in AUDIO_EXTS: return TYPE_COLORS['audio']
    if ext in VIDEO_EXTS: return TYPE_COLORS['video']
    return TYPE_COLORS['other']

def build_tree(path, prefix=''):
    """
    Recursively yield (path, is_dir, size, display_name, children)
    """
    try:
        entries = sorted(os.scandir(path), key=lambda e: e.stat().st_size, reverse=True)
    except PermissionError:
        return

    for idx, entry in enumerate(entries):
        is_last = idx == len(entries) - 1
        connector = '└── ' if is_last else '├── '
        new_prefix = prefix + ('    ' if is_last else '│   ')
        size = entry.stat().st_size if not entry.is_dir(follow_symlinks=False) else dir_size(entry.path)
        display = humanize.naturalsize(size, binary=True)
        yield entry.path, entry.is_dir(follow_symlinks=False), size, display, prefix, connector
        if entry.is_dir(follow_symlinks=False):
            yield from build_tree(entry.path, new_prefix)

def dir_size(path):
    total = 0
    for root, _, files in os.walk(path, onerror=lambda e: None):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def print_tree(root):
    print(f"{Fore.BLUE}{root}{Style.RESET_ALL}")
    for path, is_dir, size, display, prefix, connector in build_tree(root):
        color = get_type_color(path, is_dir) + size_color(size)
        name = os.path.basename(path) + ('/' if is_dir else '')
        print(f"{prefix}{connector}{color}{name} {Style.DIM}({display}){Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(
        description="Disk usage tree with color coding by file type & size"
    )
    parser.add_argument(
        'path', nargs='?', default='.',
        help="Root folder to scan (default: current directory)"
    )
    args = parser.parse_args()
    print_tree(os.path.abspath(args.path))

if __name__ == '__main__':
    main()
