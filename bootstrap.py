import hashlib
import ntpath
import os
from typing import Iterator, Tuple, AnyStr, List, Optional

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


def path(rel):
    return os.path.join(ROOT_PATH, rel.lstrip('/'))


def walk_on_path(path) -> Iterator[Tuple[AnyStr, List[AnyStr], List[AnyStr]]]:
    return os.walk(path)


def get_file_dir_and_filename(path_to_file):
    return ntpath.dirname(path_to_file), ntpath.basename(path_to_file)


def hash_file(filename) -> Optional[str]:
    """"This function returns the SHA-1 hash
        of the file passed into it"""

    # make a hash object
    h = hashlib.sha1()

    if not os.path.exists(filename):
        return None

    # open file for reading in binary mode
    with open(filename, 'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

        file.close()

    # return the hex representation of digest
    return h.hexdigest()
