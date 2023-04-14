from typing import List
from pathlib import Path
from datetime import datetime
import re
import shutil
import argparse
import mimetypes
import uuid
import json
from multiprocessing.pool import ThreadPool
import itertools
import tqdm
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Union, Generator


def find_files_worker(extension: str, path: Path, recursive: bool) -> List[Path]:
    if not extension.startswith("."):
        extension = "." + extension
    if path.is_dir():
        return list(path.rglob(f"*{extension}")) if recursive else list(path.glob(f"*{extension}"))
    else:
        return []


def find_files(extension: str, paths: List[Path], recursive: bool = False, num_threads: int = 4) -> List[Path]:
    """
        Finds files with the specified extension in the specified paths and returns them as  a list.
        :param extension: The extension of the file, starts with a '.' (e.g. '.png')
        :param paths:  A list of Path objects pointing to specific files, or directories to search.
        :param recursive: Flag to indicate if the directory search should be recursive or not.
        :param num_threads: Number of worker threads to complete search.
        :return: A list of valid Path objects.
    """
    if not extension.startswith("."):
        extension = "." + extension
    file_paths = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        tasks = [executor.submit(find_files_worker, extension, path, recursive) for path in paths]
        for task in tasks:
            try:
                result = task.result()
                file_paths.extend(result)
            except Exception as e:
                print(f"An error occurred: {e}")

    return file_paths


def get_extensions_for_type(general_type):
    mimetypes.init()
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext


def parse_args():
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument("-v", "--verbose", action="store_true", help="Print information.")
    subparsers = parent_parser.add_subparsers(dest="command")
    copy_images = subparsers.add_parser("copy_images",
                                        add_help=False,
                                        description="Copy images from directories to a destination.")
    copy_images.add_argument("folders", type=Path, nargs="+", help="Directories to search through, can also be a json file with a dictionary mapping destination keys to source values.")
    copy_images.add_argument("-o", "--output", default=".", type=Path, help="Folder to copy images into. Default current folder.")
    copy_images.add_argument("-i", "--images", type=str, nargs="+", help="File extensions to search for.", default=list(get_extensions_for_type("image")))
    copy_images.add_argument("-u", "--uuid", action="store_true", help="Generate UUIDv4s for files. Ensures all images are copied.")
    copy_images.add_argument("--dry_run", action="store_true", help="Do not copy, just output mappings.")
    args = parent_parser.parse_args()
    return args


def glob_suffix(search_params: dict):
    path = search_params["path"]
    suffix = search_params["suffix"]
    if search_params.get("verbose"):
        print(f"Searching for {suffix} in {path.name}")
    return path.rglob("*" + suffix)


def expand_json_mappings(json_paths: List[Path]):
    mappings = {}
    for path in json_paths:
        with open(path, "r") as f:
            mappings.update(json.load(f))
    return mappings


def search4images(args: argparse.Namespace):
    image_paths = [path for path in args.folders if path.suffix in args.images and path.exists()]
    json_paths = [path for path in args.folders if path.suffix == ".json" and path.exists()]
    json_mappings = expand_json_mappings(json_paths)
    dir_paths = [path for path in args.folders if path.is_dir() and path.exists()]
    combinations = [{"path": p, "suffix": s} for p, s in itertools.product(dir_paths, args.images)]
    with ThreadPool(processes=10) as pool:
        results = pool.map(glob_suffix, combinations)
        output = itertools.chain(json_mappings.items(), *image_paths, *results)
    return output


def copy_worker(args: argparse.Namespace):
    def do_work(mapping):
        if not args.dry_run:
            if Path(mapping[0]).exists():
                if args.verbose:
                    print(f"File exists ", mapping[0])
                    return False
            if args.verbose:
                print(f"copying {mapping[1]} to {mapping[0]}")
            shutil.copy2(mapping[1], mapping[0])
        return True
    return do_work


def copy_images(args: argparse.Namespace):
    # Check the output directory exists
    args.output.mkdir(exist_ok=True, parents=True)
    destination_parent = args.output.resolve()
    # Create iterator for searching source directories for images
    search_results = search4images(args)
    mappings = {}
    # Create mappings from source to destination
    for item in tqdm.tqdm(search_results, desc="Finding images..."):
        if isinstance(item, Path):
            # TODO consider UUIDs to prevent overwriting of images with same filenames.
            if args.uuid:
                destination = destination_parent.joinpath(item.stem + f"_{uuid.uuid4()}" + item.suffix)
            else:
                destination = destination_parent.joinpath(item.name)
            source = item
        elif isinstance(item, tuple):
            destination = item[0]
            source = item[1]
        else:
            raise ValueError("Item is of type: ", type(item), ". Should be either Path or tuple.")
        if str(destination) in mappings:
            if args.verbose:
                print("Already mapped: ", item)
            continue
        mappings.update({str(destination): str(source)})
    with open(args.output.joinpath("image_mappings.json"), "w") as f:
        json.dump(mappings, f)
    with ThreadPool(processes=10) as pool:
        worker = copy_worker(args)
        results = pool.map(worker, mappings.items())
        for res in tqdm.tqdm(results, desc="Copying..."):
            pass
        if args.verbose and args.dry_run:
            print("Dry run complete.")


if __name__ == "__main__":
    args = parse_args()
    if args.command == "copy_images":
        copy_images(args)
