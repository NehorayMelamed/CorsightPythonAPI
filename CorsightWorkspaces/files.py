import json

def load_json_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def write_dict_to_json_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage:
# my_data = {
#     "name": "John",
#     "age": 30,
#     "city": "New York"
# }
# write_dict_to_json_file(my_data, 'path_to_output_file.json')



# Example usage:
# data = load_json_from_file('path_to_json_file.json')
# print(data)

import os
import shutil


def copy_videos(src_dir, dest_dir, video_extensions=('mp4', 'mkv', 'avi', 'mov', 'flv')):
    """
    Recursively copy video files from src_dir to dest_dir.

    Parameters:
    - src_dir (str): Source directory to search for video files.
    - dest_dir (str): Destination directory to copy video files to.
    - video_extensions (tuple): Tuple of video file extensions to search for. Default is ('mp4', 'mkv', 'avi', 'mov', 'flv').

    Returns:
    - None
    """

    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Walk through the source directory
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.endswith(video_extensions):
                src_file_path = os.path.join(dirpath, filename)
                dest_file_path = os.path.join(dest_dir, filename)

                # Ensure unique filenames in destination directory
                counter = 1
                while os.path.exists(dest_file_path):
                    name, ext = os.path.splitext(filename)
                    dest_file_path = os.path.join(dest_dir, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.copy2(src_file_path, dest_file_path)
                print(f"Copied {src_file_path} to {dest_file_path}")

# copy_videos('/path/to/source/directory', '/home/gal/PycharmProjects/Nehedar/data/videos_telegram')


# import os
#
#
# def rename_images_to_ascii(directory_path, img_extensions=('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff')):
#     """
#     Rename image files in the given directory to valid ASCII filenames.
#
#     Parameters:
#     - directory_path (str): Directory containing the image files to be renamed.
#     - img_extensions (tuple): Tuple of image file extensions to consider. Default is ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff').
#
#     Returns:
#     - None
#     """
#
#     counter = 1
#     for filename in os.listdir(directory_path):
#         if filename.endswith(img_extensions):
#             # Generate a new valid ASCII filename using a counter
#             new_filename = f"image_{counter}.{filename.split('.')[-1]}"
#             src_file_path = os.path.join(directory_path, filename)
#             dest_file_path = os.path.join(directory_path, new_filename)
#
#             os.rename(src_file_path, dest_file_path)
#             print(f"Renamed {filename} to {new_filename}")
#             counter += 1
#
# # Example usage:
# rename_images_to_ascii('/home/gal/PycharmProjects/Nehedar/CorsightWorkspaces/blue_data')
#

#
# from google.cloud import translate_v2 as translate
#
# def hebrew_to_english(filename):
#     # Set up the client
#     client = translate.Client()
#
#     # Split the filename into name and extension
#     name, ext = os.path.splitext(filename)
#
#     # Transliterate the name
#     result = client.translate(name, source_language='iw', target_language='en', format_='text')
#     transliterated_name = result['input']
#
#     # Replace spaces with underscores
#     english_name = transliterated_name.replace(' ', '_')
#
#     # Return the new filename with the original extension
#     return english_name.lower() + ext
#
# # Test
# filename = "ענת דהן.png"
# new_filename = hebrew_to_english(filename)
# print(new_filename)  # Outputs: anat_dahan.png
#



