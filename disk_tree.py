#!/usr/bin/env python3
import os
import sys
import argparse
from colorama import init, Fore, Style
import humanize

# Initialize ANSI color handling
init(autoreset=True)

# Package version
__version__ = '0.2.0'

# File-type color mapping
TYPE_COLORS = {
    'folder': Fore.BLUE,
    'image':  Fore.YELLOW,
    'text':   Fore.CYAN,
    'audio':  Fore.MAGENTA,
    'video':  Fore.RED,
    'other':  Fore.GREEN,
}

# File extension sets for type detection
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
TEXT_EXTS  = {'.txt', '.md', '.py', '.java', '.c', '.cpp', '.html', '.css', '.js'}
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.aac'}
VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.mov'}

# Size-based color thresholds
def size_color(size):
    if size > 10 * 1024**2:
        return Fore.RED
    if size > 1  * 1024**2:
        return Fore.YELLOW
    return Fore.GREEN

# Determine ANSI color based on file type
def get_type_color(path, is_dir):
    if is_dir:
        return TYPE_COLORS['folder']
    ext = os.path.splitext(path)[1].lower()
    if ext in IMAGE_EXTS: return TYPE_COLORS['image']
    if ext in TEXT_EXTS:  return TYPE_COLORS['text']
    if ext in AUDIO_EXTS: return TYPE_COLORS['audio']
    if ext in VIDEO_EXTS: return TYPE_COLORS['video']
    return TYPE_COLORS['other']

# Calculate total size of directory recursively
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

# Build tree structure
def build_tree(path, prefix='', current_depth=1, max_depth=3,
               limit=None, include_hidden=False, sort_by='size'):
    if current_depth > max_depth:
        return

    try:
        entries = list(os.scandir(path))
    except PermissionError:
        return

    # Filter hidden
    if not include_hidden:
        entries = [e for e in entries if not e.name.startswith('.')]

    # Compute sort keys
    entry_info = []
    for entry in entries:
        try:
            if entry.is_dir(follow_symlinks=False):
                size = dir_size(entry.path)
            else:
                size = entry.stat().st_size
        except OSError:
            size = 0
        entry_info.append((entry, size))

    # Sorting
    if sort_by == 'size':
        key_func = lambda es: es[1]
        reverse = True
    elif sort_by == 'name':
        key_func = lambda es: es[0].name.lower()
        reverse = False
    elif sort_by == 'type':
        # Directories first, then by extension, then name
        def type_key(es):
            entry = es[0]
            if entry.is_dir(follow_symlinks=False):
                return (0, '', entry.name.lower())
            ext = os.path.splitext(entry.name)[1].lower()
            return (1, ext, entry.name.lower())
        key_func = type_key
        reverse = False
    else:
        key_func = lambda es: es[1]
        reverse = True

    entry_info.sort(key=key_func, reverse=reverse)

    # Apply limit
    if limit is not None:
        entry_info = entry_info[:limit]

    # Yield entries
    for idx, (entry, size) in enumerate(entry_info):
        is_last   = idx == len(entry_info) - 1
        connector = '└── ' if is_last else '├── '
        new_prefix= prefix + ('    ' if is_last else '│   ')

        human_sz = humanize.naturalsize(size, binary=True)
        is_dir   = entry.is_dir(follow_symlinks=False)

        yield entry.path, is_dir, size, human_sz, prefix, connector

        if is_dir:
            yield from build_tree(
                entry.path,
                new_prefix,
                current_depth + 1,
                max_depth,
                limit,
                include_hidden,
                sort_by
            )

# Print the tree to stdout
def print_tree(root, max_depth, per_dir_limit, include_hidden, sort_by):
    print(f"{Fore.BLUE}{root}{Style.RESET_ALL}")
    for path, is_dir, size, human_sz, prefix, connector in build_tree(
            root, '', 1, max_depth,
            per_dir_limit, include_hidden, sort_by):
        name = os.path.basename(path) + ('/' if is_dir else '')
        # Name uses type color
        name_colored = f"{get_type_color(path, is_dir)}{name}{Style.RESET_ALL}"
        # Size parentheses use size color
        size_colored = f"{size_color(size)}{Style.DIM}({human_sz}){Style.RESET_ALL}"
        print(f"{prefix}{connector}{name_colored} {size_colored}")

# Entry point
def main():
    parser = argparse.ArgumentParser(
        description="Disk-usage tree with color coding by file type & size",
        add_help=True
    )
    parser.add_argument(
        'path', nargs='?', default='.',
        help="Root folder to scan (default: current directory)"
    )
    parser.add_argument(
        '-d', '--depth', type=int, default=3,
        help="Max tree depth (default: 3)"
    )
    parser.add_argument(
        '-l', '--limit', type=int, default=10,
        help="Max entries per directory (default: 10)"
    )
    parser.add_argument(
        '-s', '--sort', choices=['size','name','type'], default='size',
        help="Sort entries by 'size' (default), 'name', or 'type'"
    )
    parser.add_argument(
        '-a', '--all', action='store_true',
        help="Include hidden files and directories"
    )
    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {__version__}'
    )
    # --help is automatically added
    args = parser.parse_args()

    root = os.path.abspath(args.path)
    print_tree(
        root,
        args.depth,
        args.limit,
        args.all,
        args.sort
    )

if __name__ == '__main__':
    main()
