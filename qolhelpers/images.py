import cv2
from pathlib import Path
import os
import cv2
import numpy as np
from skimage.feature import hog
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from typing import List, Generator, Union
from multiprocessing import Pool, cpu_count


def extract_features(image_file: Path):
    img = cv2.imread(str(image_file), cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (128, 128))
    fd = hog(img, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1))
    return image_file, fd


def load_images_and_extract_features(image_directory: Union[List[Path], Generator[Path, None, None]]):
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(extract_features, image_directory)
    image_directory, features = zip(*results)
    return list(image_directory), features


def detect_anomalies(image_directory, n_clusters=10, threshold=2.5):
    image_files, features = load_images_and_extract_features(image_directory)

    # Standardize features
    scaler = StandardScaler()
    standardized_features = scaler.fit_transform(features)

    # Cluster images using KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(standardized_features)

    # Calculate distance between each image feature and its cluster centroid
    distances = pairwise_distances(standardized_features, kmeans.cluster_centers_, metric='euclidean')
    cluster_distances = distances[np.arange(len(distances)), kmeans.labels_]

    # Define outliers based on threshold
    outliers = np.where(cluster_distances > threshold)[0]
    outlier_images = [image_files[i] for i in outliers]

    return outlier_images


def threshold_and_crop(image, padding=0):
    if isinstance(image, (Path, str)):
        image = cv2.imread(str(image))
    # Grayscale
    gray = image.copy()
    if image.ndim > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold the image to create a binary image
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    x, y, w, h = cv2.boundingRect(thresh)

    # Add padding to the bounding rectangle
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(image.shape[1] - x, w + 2 * padding)
    h = min(image.shape[0] - y, h + 2 * padding)

    cropped_image = image[y:y+h, x:x+w, ...]

    return cropped_image



