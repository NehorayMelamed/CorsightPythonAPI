import os
from PIL import Image
import imagehash
import numpy as np
import multiprocessing
import time

def compute_phash(image, hash_size=8):
    return imagehash.phash(image, hash_size)

def get_mse(img1, img2):
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img1.shape[1])
    return err

def worker_process(file_path, seen_hashes, hash_size, mse_threshold, duplicates):
    with Image.open(file_path) as img:
        phash = compute_phash(img, hash_size)
        if phash in seen_hashes:
            img2_path = seen_hashes[phash]
            with Image.open(img2_path) as img2:
                mse_val = get_mse(np.array(img.resize((256, 256))), np.array(img2.resize((256, 256))))
                if mse_val < mse_threshold:
                    duplicates.append(file_path)
        else:
            seen_hashes[phash] = file_path

def bin_by_size(image_files):
    bins = {}
    for image_file in image_files:
        file_size = os.path.getsize(image_file)
        if file_size not in bins:
            bins[file_size] = []
        bins[file_size].append(image_file)
    return bins

def remove_duplicates(directory_path, hash_size=8, mse_threshold=95):
    start_time = time.time()

    manager = multiprocessing.Manager()
    seen_hashes = manager.dict()
    duplicates = manager.list()

    pool = multiprocessing.Pool()

    for root, _, files in os.walk(directory_path):
        image_files = [os.path.join(root, file) for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'))]
        image_bins = bin_by_size(image_files)

        for _, binned_files in image_bins.items():
            for file_path in binned_files:
                pool.apply_async(worker_process, (file_path, seen_hashes, hash_size, mse_threshold, duplicates))

    pool.close()
    pool.join()

    for duplicate in duplicates:
        print(f"Deleting duplicate: {duplicate}")
        os.remove(duplicate)

    end_time = time.time()
    print(f"Execution Time: {end_time - start_time} seconds")


if __name__ == "__main__":
    remove_duplicates('/home/nehoray/Documents/test_duplicate (4th copy)')

