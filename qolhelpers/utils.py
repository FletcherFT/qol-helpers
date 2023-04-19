import multiprocessing
import shutil
import argparse
import mimetypes
import uuid
import json
import tqdm
import concurrent.futures
from pathlib import Path
from typing import Sequence, Tuple, List, Union
import sys
import os
from qolhelpers.images import threshold_and_crop, detect_anomalies
import cv2


def find_files_threaded(path: os.PathLike, extensions: Sequence[str], recursive: bool) -> List[Path]:
    # Make the path of type pathlib.Path
    if not isinstance(path, Path):
        path = Path(path)
    file_paths = []
    if not path.exists():
        print(f"Could not find {path}.", file=sys.stderr)
        return file_paths
    # If the path is a directory, glob for the extensions
    if path.is_dir():
        for ext in extensions:
            file_paths.extend(path.rglob(f"*{ext}")) if recursive else file_paths.extend(path.glob(f"*{ext}"))
    # If it's a file, check that it has a matching extension.
    elif path.is_file():
        if path.suffix not in extensions:
            print(f"Not one of the specified file types: {path}.", file=sys.stderr)
            return file_paths
        file_paths.append(path)
    else:
        print(f"Not a file or directory: {path}", file=sys.stderr)

    return file_paths


def find_files(extensions: Union[str, Sequence[str]], paths: Union[os.PathLike, Sequence[os.PathLike]],
               recursive: bool = False, num_threads: int = 4) -> Tuple[Path]:
    """
            Finds files with the specified extensions in the specified paths and returns them as a tuple.
            :param extensions: The extension of the file, starting with a '.' is optional (e.g. '.png')
            :param paths:  A list of Path objects pointing to specific files, or directories to search.
            :param recursive: Flag to indicate if the directory search should be recursive or not.
            :param num_threads: Number of worker threads to complete search.
            :return: A tuple of valid Path objects.
        """
    extensions = [ext if ext.startswith(".") else "." + ext for ext in extensions]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        tasks = [executor.submit(find_files_threaded, path, extensions, recursive) for path in paths]
        file_paths = [result for task in concurrent.futures.as_completed(tasks) for result in task.result()]

    return tuple(file_paths)


def get_extensions_for_type(general_type):
    """
    A tool to list all the possible extensions for a given file type.
    :param general_type:
    :return:
    """
    mimetypes.init()
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext


def parse_args():
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument("-v", "--verbose", action="store_true", help="Print information.")
    subparsers = parent_parser.add_subparsers(dest="command")
    copy_images = subparsers.add_parser("copy_images",
                                        add_help=True,
                                        description="Copy images from directories to a destination.")
    copy_images.add_argument("folders", type=Path, nargs="+", help="Directories to search through.")
    copy_images.add_argument("-o", "--output", default=".", type=Path, help="Folder to copy images into. Default current folder.")
    copy_images.add_argument("-i", "--images", type=str, nargs="+", help="File extensions to search for.", default=list(get_extensions_for_type("image")))
    copy_images.add_argument("-u", "--uuid", action="store_true", help="Generate UUIDv4s for files. Ensures all images are copied.")
    copy_images.add_argument("-r", "--recursive", action="store_true", help="Flag to recursively search directories.")
    copy_images.add_argument("--dry_run", action="store_true", help="Do not copy, just output mappings.")
    copy_images.add_argument("-w", "--workers", type=int, default=multiprocessing.cpu_count() - 1,
                             help="Specify number of workers.")
    crop_images = subparsers.add_parser("crop_images",
                                        add_help=True,
                                        description="Crop images from directories to a destination.")
    crop_images.add_argument("folders", type=Path, nargs="+", help="Directories to search through.")
    crop_images.add_argument("-o", "--output", default=".", type=Path, help="Folder to copy images into. Default current folder.")
    crop_images.add_argument("-i", "--images", type=str, nargs="+", help="File extensions to search for.", default=list(get_extensions_for_type("image")))
    crop_images.add_argument("-p", "--padding", type=int, default=0, help="Pad the crop.")
    crop_images.add_argument("-r", "--recursive", action="store_true", help="Flag to recursively search directories.")
    crop_images.add_argument("-w", "--workers", type=int, default=multiprocessing.cpu_count() - 1, help="Specify number of workers.")
    crop_images.add_argument("--dry_run", action="store_true", help="Do not copy, just output mappings.")
    detect_anomalies = subparsers.add_parser("detect_anomalies",
                                        add_help=True,
                                        description="Detect anomalies.")
    detect_anomalies.add_argument("folders", type=Path, nargs="+",
                             help="Directories to search through.")
    detect_anomalies.add_argument("-o", "--output", default="./anomalies.txt", type=Path,
                             help="File to copy images into. Default ./anomalies.txt")
    detect_anomalies.add_argument("-i", "--images", type=str, nargs="+", help="File extensions to search for.",
                             default=list(get_extensions_for_type("image")))
    detect_anomalies.add_argument("-c", "--clusters", type=int, default=10, help="Number of clusters to attempt anomaly detection across.")
    detect_anomalies.add_argument("--dry_run", action="store_true", help="Do not copy, just output mappings.")
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


def copy_worker(args: argparse.Namespace):
    def do_work(image_path: Path):
        if not args.dry_run:
            output_path = args.output.joinpath(image_path.name) if not args.uuid else args.output.joinpath(image_path.stem + f"_{uuid.uuid4()}" + image_path.suffix)
            if output_path.exists():
                if args.verbose:
                    print(f"File exists ", output_path)
                    return False
            if args.verbose:
                print(f"Copying {image_path} to {output_path}")
            shutil.copy2(str(image_path), str(output_path))
        return True
    return do_work


def copy_images(args: argparse.Namespace):
    # Check the output directory exists
    args.output.mkdir(exist_ok=True, parents=True)
    # Create iterator for searching source directories for images
    image_paths = find_files(args.images, args.folders, args.recursive, args.workers)
    # Create automatic crops from source to destination
    with tqdm.tqdm(total=len(image_paths), desc="Copying...") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            worker = copy_worker(args)
            futures = [pool.submit(worker, image_path) for image_path in image_paths]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                pbar.update(1)
            if args.verbose and args.dry_run:
                print("Dry run complete.")


def crop_worker(args: argparse.Namespace):
    def do_work(image_path: Path):
        if not args.dry_run:
            output_path = args.output.joinpath(image_path.name)
            if output_path.exists():
                if args.verbose:
                    print(f"File exists ", output_path)
                    return False
            if args.verbose:
                print(f"Cropping {image_path} to {output_path}")
            img = threshold_and_crop(image_path, args.padding)
            return cv2.imwrite(str(output_path), img)
        return True
    return do_work


def crop_images(args: argparse.Namespace):
    # Check the output directory exists
    args.output.mkdir(exist_ok=True, parents=True)
    # Create iterator for searching source directories for images
    image_paths = find_files(args.images, args.folders, args.recursive, args.workers)
    # Create automatic crops from source to destination
    with tqdm.tqdm(total=len(image_paths), desc="Cropping...") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            worker = crop_worker(args)
            futures = [pool.submit(worker, image_path) for image_path in image_paths]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                pbar.update(1)
            if args.verbose and args.dry_run:
                print("Dry run complete.")


if __name__ == "__main__":
    args = parse_args()
    if args.command == "copy_images":
        copy_images(args)
    if args.command == "crop_images":
        crop_images(args)
    if args.command == "detect_anomalies":
        raise NotImplementedError("Anomaly detection requires more work.")
        # imgs = search4images(args)
        # outliers = detect_anomalies(imgs, 5)
        # with open(args.output, "w") as f:
        #     f.writelines([str(o)+'\n' for o in outliers])
