import os
import re
import shutil
import sys
from pathlib import Path

image_files = list()
video_files = list()
document_files = list()
music_files = list()
archives = list()
folders = list()
others = list()
unknown = set()
extensions = set()

registered_extensions = {
    'JPEG': image_files,
    'PNG': image_files,
    'JPG': image_files,
    'SVG': image_files,
    'AVI': video_files,
    'MP4': video_files,
    'MOV': video_files,
    'MKV': video_files,
    'DOC': document_files,
    'DOCX': document_files,
    'TXT': document_files,
    'PDF': document_files,
    'XLS': document_files,
    'XLSX': document_files,
    'PPTX': document_files,
    'MP3': music_files,
    'OGG': music_files,
    'WAW': music_files,
    'AMR': music_files,
    'ZIP': archives,
    'GZ': archives,
    'TAR': archives
}


UKRAINIAN_SYMBOLS = 'абвгдеєжзиіїйклмнопрстуфхцчшщьюя'
ENGLISH_SYMBOLS = ("a", "b", "v", "g", "d", "e", "je", "zh", "z", "y", "i", "ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "ju", "ja")

TRANS = {}
for key, value in zip(UKRAINIAN_SYMBOLS, ENGLISH_SYMBOLS):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()

def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}" if extension else new_name

def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()


def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('images', 'video', 'audio', 'documents', 'archives', 'other'):
                folders.append(item)
                scan(item)
            continue
        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            try:
                container = registered_extensions[extension]
                extensions.add(extension)
                container.append(new_name)
            except KeyError:
                unknown.add(extension)
                others.append(new_name)


def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize.normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)
    new_name = path.name
    for i in ['.zip', '.tar.gz', '.tar']:
        new_name = normalize.normalize(new_name.replace(i, ''))
    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)
    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        os.remove(str(path.resolve()))
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()

def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass

def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    scan(folder_path)
    items = {'images': scan.image_files,
             'video': scan.video_files,
             'audio': scan.music_files,
             'documents': scan.document_files,
             'other': scan.others}
    for key, val in items.items():
        for file in items[key]:
            handle_file(file, folder_path, key)
    for file in scan.archives:
        handle_archive(file, folder_path, "archives")
    remove_empty_folders(folder_path)

def print_result(folder):
    for item in folder.iterdir():
        print(item.name)
        if item.is_dir():
            print_result(item)
        continue

if __name__ == '__main__':
    main()
