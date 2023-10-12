import os
import imagehash
from PIL import Image

def compute_dhash(image_path, hash_size=64):
    """
    Compute the dHash of an image.
    """
    with Image.open(image_path) as img:
        return str(imagehash.dhash(img, hash_size))

def compute_phash(image_path, hash_size=64):
    """
    Compute the pHash of an image.
    """
    with Image.open(image_path) as img:
        return str(imagehash.phash(img, hash_size))

def remove_duplicates(directory_path, hash_size=64, similarity_threshold=0.9, keep_originals=False):
    """
    Remove duplicate photos from the specified directory using multiple hashing techniques.
    """
    seen_hashes = set()
    duplicates = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                file_path = os.path.join(root, file)
                dhash = compute_dhash(file_path, hash_size)
                phash = compute_phash(file_path, hash_size)

                # Check if either dHash or pHash is already seen
                if dhash in seen_hashes or phash in seen_hashes:
                    print(f"Duplicate found: {file_path}")
                    duplicates.append(file_path)
                else:
                    seen_hashes.add(dhash)
                    seen_hashes.add(phash)

    if keep_originals:
        print("Duplicates found:")
        for duplicate in duplicates:
            print(duplicate)
    else:
        print("Deleting duplicates:")
        for duplicate in duplicates:
            os.remove(duplicate)

# Usage
remove_duplicates('/path/to/your/image/directory', hash_size=64, similarity_threshold=0.9, keep_originals=False)
