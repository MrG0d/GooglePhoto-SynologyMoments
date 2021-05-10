from datetime import datetime
import json
import os
import re

from bootstrap import get_file_dir_and_filename, hash_file, path
from logger import Logger
from translate.ru import *

hash_processed_photos = {}

logger = Logger('Transform')

PATH_TO_GOOGLE_PHOTO_DIR = path('google_photo')


def get_meta_file(path_to_media_file):
    directory, name = get_file_dir_and_filename(path_to_media_file)
    basic_metafile_name = (name if '-%s.' % NAME_KEY_CHANGED not in name else name.replace('-%s' % NAME_KEY_CHANGED, ''))
    metafile_original_name = '%s.json' % basic_metafile_name
    metafile_path = '%s/%s' % (directory, '.' + metafile_original_name)
    metafile_original_path = '%s/%s' % (directory, metafile_original_name)
    if not os.path.isfile(metafile_path):  # find: .name.ext.json
        if not os.path.isfile(metafile_original_path):  # find: name.ext.json
            # logger.info('Error find metafile for file [%s]: %s' % (path_to_media_file, metafile_original_path))
            metafile_original_path = '%s/%s.json' % (directory, basic_metafile_name[:-1])  # find: nam.ext.json
            if not os.path.isfile(metafile_original_path):
                # logger.info('Error find metafile for file [%s]: %s' % (path_to_media_file, metafile_original_path))
                metafile_original_path = '%s/%s.json' % (directory, os.path.splitext(basic_metafile_name)[0])  # find: name.json
                if not os.path.isfile(metafile_original_path):
                    # logger.info('Error find metafile for file [%s]: %s' % (path_to_media_file, metafile_original_path))
                    metafile_original_path = '%s/%s.json' % (directory, os.path.splitext(basic_metafile_name)[0][:-1])  # find: nam.json
                    if not os.path.isfile(metafile_original_path):
                        # logger.info('Error find metafile for file [%s]: %s' % (path_to_media_file, metafile_original_path))
                        matches = re.search(r"(\(\d+\))\.", path_to_media_file)
                        if matches:
                            metafile_original_path = '%s/%s%s.json' % (directory, basic_metafile_name.replace(matches[1], ''), matches[1])  # find: name(1).mp4 -> name.mp4(1).json
                        if not matches or not os.path.isfile(metafile_original_path):
                            # logger.error('Error find metafile for media [%s]' % (path_to_media_file))
                            return None
        os.rename(metafile_original_path, metafile_path)

    return metafile_path


def get_meta_data(path_to_media_file):
    path_to_metadata = get_meta_file(path_to_media_file)
    if not path_to_metadata:
        return None
    try:
        with open(path_to_metadata) as json_file:
            return json.load(json_file)
    except Exception as e:
        print(e.args)
        logger.error('Error read meta-file for photo [%s]: %s' % (path_to_media_file, path_to_metadata))
        return None


def get_time_from_name(path_to_media_file):
    name = os.path.splitext(path_to_media_file)[0]
    matches = re.search(r'(20[1,2]\d)-?(\d{2})-?(\d{2})[_-](\d{2})-?(\d{2})-?(\d{2})', name)  # for <Year><Month><Day>
    if matches:
        date = datetime(int(matches[1]), int(matches[2]), int(matches[3]), int(matches[4]), int(matches[5]), int(matches[6]))
    else:
        matches = re.search(r'(\d{2})(\d{2})(20[1,2]\d)_(\d{2})(\d{2})(\d{2})', name)  # for <Day><Year><Month>
        if matches:
            date = datetime(int(matches[3]), int(matches[2]), int(matches[1]), int(matches[4]), int(matches[5]), int(matches[6]))
        else:
            return None

    return datetime.timestamp(date)


def processed_files(file_list, ignore_duplicate_message=False):
    for file in file_list:
        directory, name = get_file_dir_and_filename(file)
        if name.startswith('.'):
            continue
        ext = os.path.splitext(file)[1][1:]
        if ext not in ['mp4', 'MP4', 'jpg', 'JPG', '3gp', 'png', 'gif', 'CR2', 'JPEG', 'jpeg', 'MOV', 'mov']:
            if ext not in ['json', 'html']:
                logger.error('Unsupported file: %s' % file)
            continue

        hash = hash_file(file)
        if hash in hash_processed_photos:
            if ignore_duplicate_message is False:
                logger.warning('The file has already been processed: %s %r' % (file, hash_processed_photos[hash]))
            os.rename(file, '%s/.%s' % (directory, name))
            continue
        hash_processed_photos[hash] = {'path': file}

        timestamp = get_time_from_name(file)
        metadata = get_meta_data(file)  # for hide metafiles
        if metadata and not timestamp:
            creation_at = int(metadata['creationTime']['timestamp'])
            taken_at = int(metadata['photoTakenTime']['timestamp'])
            timestamp = taken_at if taken_at < creation_at else creation_at

        if not timestamp:
            logger.error('Failed to get time of create a file: %s' % file)
            continue

        formatted = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print('-- File: %s [%s]' % (file, formatted))
        os.utime(file, (timestamp, timestamp))


def processed(root, dirs, files, ignore_duplicate_message=False):
    files = ['%s/%s' % (root, file) for file in files]
    print('Directory: %s' % root)

    metadata_path = '%s/%s.json' % (root, NAME_KEY_METADATA)
    if os.path.isfile(metadata_path):
        with open(metadata_path) as json_file:
            metadata = json.load(json_file)
            os.utime(root, (int(metadata['albumData']['date']['timestamp']), int(metadata['albumData']['date']['timestamp'])))

    if len(files):
        processed_files(files, ignore_duplicate_message)


def dir_is_album(path_to_dir):
    return not re.match(r'^(Photos from \d{4}|'+NAME_KEY_ARCHIVE+')$', os.path.basename(path_to_dir))


# only album
for root, dirs, files in os.walk(PATH_TO_GOOGLE_PHOTO_DIR):
    if dir_is_album(root):
        processed(root, dirs, files)

# other dirs
for root, dirs, files in os.walk(PATH_TO_GOOGLE_PHOTO_DIR):
    if not dir_is_album(root):
        processed(root, dirs, files, True)


print("Success")
