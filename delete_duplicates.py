import os
from PIL import Image
import imagehash
from skimage.metrics import structural_similarity as ssim
import numpy as np


def compute_phash(image_path, hash_size=8):
    with Image.open(image_path) as img:
        return imagehash.phash(img, hash_size)


def get_ssim(img_path1, img_path2):
    img1 = Image.open(img_path1).convert('L')  # Convert to grayscale
    img2 = Image.open(img_path2).convert('L')

    img1 = np.array(img1.resize((256, 256)))
    img2 = np.array(img2.resize((256, 256)))

    return ssim(img1, img2)


def remove_duplicates(directory_path, hash_size=8, ssim_threshold=0.90):
    seen_hashes = {}
    duplicates = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                file_path = os.path.join(root, file)
                phash = compute_phash(file_path, hash_size)

                if phash in seen_hashes:
                    ssim_val = get_ssim(file_path, seen_hashes[phash])
                    if ssim_val > ssim_threshold:
                        duplicates.append(file_path)
                else:
                    seen_hashes[phash] = file_path

    # Delete duplicates
    for duplicate in duplicates:
        print(f"Deleting duplicate: {duplicate}")
        os.remove(duplicate)


# Usage
remove_duplicates('/home/nehoray/Documents/test_images')
