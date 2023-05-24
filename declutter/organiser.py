import itertools
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import Dict, List, Tuple, Union

import regex

from .content_mime import IGNORE, NOT_CATEGORIZED, mimes

absolute_directory_type = namedtuple(
    "absolute_directory_type", ["type_of", "size", "count"]
)


def pluralise(content_name: str):
    _ = content_name.capitalize()

    if _.endswith("s") or _.endswith("x"):
        return _ + "es"

    return _ + "s"


def list_content(dictionary: defaultdict):
    """
    Get all content within the lists of the dictionary.
    """
    for _, __ in dictionary.items():
        if isinstance(__, dict):
            yield from list_content(__)

        if isinstance(__, (list, tuple, set)):
            yield from __


def get_content_type(
    content_extension: str,
    *,
    content_types: dict[str, Union[str, dict]] = mimes,
    ignore=IGNORE
) -> Tuple[str]:

    for type_of, types in content_types.items():
        if type_of == NOT_CATEGORIZED or type_of in ignore:
            return ()

        if isinstance(types, dict):
            if any(
                regex.match(pattern + "$", content_extension, flags=regex.I)
                for pattern in list_content(types)
            ):
                return (
                    type_of,
                    *get_content_type(content_extension, content_types=types),
                )
            continue

        for pattern in types:
            if regex.match(pattern + "$", content_extension, flags=regex.I):
                return (type_of,)

    return ()


def recursive_path_size_and_count(path: Path) -> int:
    """
    Get the size of the path recursively.
    """
    if path.is_dir():
        size = 0
        count = 0

        for content in path.iterdir():
            sub_size, sub_count = recursive_path_size_and_count(content)

            size += sub_size
            count += sub_count

    return path.stat().st_size, 1


def get_directory_type(
    path: Path, *, beacon=None, recurse=False
) -> Dict[Tuple[str], List[Path]]:
    """
    Get the possible types of the content in the directory recursively.
    """
    beacon = beacon or defaultdict(list)

    parent_skip_list = []

    for content in itertools.chain((path,), path.glob("**/*" if recurse else "*")):

        if content.is_dir():
            git_directory = content / ".git"
            build_directory = content / "build"
            src_directory = content / "src"

            if any(
                dev_directory.exists() and dev_directory.is_dir()
                for dev_directory in (git_directory, build_directory, src_directory)
            ):
                parent_skip_list.append(content)
                beacon[("developer",)].append(content)
                continue

            asset_directory = content / "assets"
            cache_directory = content / "cache"
            views_directory = content / "views"
            data_directory = content / "data"

            for directory in (
                asset_directory,
                cache_directory,
                views_directory,
                data_directory,
            ):
                if directory.exists() and directory.is_dir():
                    parent_skip_list.append(directory)
                    beacon[()].append(directory)
                    continue

            continue

        if any(parent in parent_skip_list for parent in content.parents):
            continue

        if not "." in content.name:
            beacon[()].append(content)
            continue

        _, extension = content.name.rsplit(".", 1)
        beacon[get_content_type(extension)].append(content)

    return beacon


def get_absolute_directory_type(path: Path, *, recurse=False):

    directory_beacon = get_directory_type(path, recurse=recurse)

    for type_of, paths in directory_beacon.items():

        sub_size = 0
        sub_count = 0

        for sub_path in paths:
            sub__size, sub__count = recursive_path_size_and_count(sub_path)
            sub_size += sub__size
            sub_count += sub__count

        yield absolute_directory_type(type_of, sub_size, sub_count)


SPECIAL_DIRECTORIES = [pluralise(_) for _ in mimes]


def get_transfer_route(current_path: Path, directory_tuple: Tuple[str]):
    if not directory_tuple:
        return current_path

    raw_copy = current_path

    for directory in directory_tuple:
        raw_copy /= pluralise(directory)
        raw_copy.mkdir(exist_ok=True)

    return raw_copy


def iter_organisation(path: Path, *, recurse=False):
    for content in path.glob("*"):
        if content.is_dir() and not content.name in SPECIAL_DIRECTORIES:
            directory_beacon = get_absolute_directory_type(content, recurse=recurse)

            directory_types = sorted(
                directory_beacon,
                key=lambda absol_dir_type: absol_dir_type.count,
                reverse=True,
            )
            if not directory_types:
                continue

            type_of, *_ = directory_types[0]

            yield content, get_transfer_route(path, type_of)
            continue
        else:
            if "." in content.name:

                _, extension = content.name.rsplit(".", 1)

                yield content, get_transfer_route(path, get_content_type(extension))
