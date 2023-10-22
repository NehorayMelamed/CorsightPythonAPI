import json
import os
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image, ImageDraw
from io import BytesIO
import base64
import PARAMETERS

BASE_URL = "https://localhost:8080/poi_db"
# BASE_URL = "https://host.docker.internal:8080/poi_db"

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {PARAMETERS.access_token}"
}
# output_base = "/home/gal/PycharmProjects/Nehedar/data/output"
# outpus_pois_path = os.path.join(output_base, "pois_2")
# if os.path.exists(outpus_pois_path) is False:
#     os.mkdir(outpus_pois_path)


class CustomOutput:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def save_dict_to_json(data, output_path):
    """
    Save a dictionary to a JSON file.

    Parameters:
    - data (dict): The dictionary to save.
    - output_path (str): The path where the JSON file should be saved.
    """
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def save_base64_image(base64_string, output_path):
    """
    Save a base64 encoded image to a file.

    Parameters:
    - base64_string (str): The base64 encoded string of the image.
    - output_path (str): The path where the image should be saved.
    """
    # Decode the base64 string
    image_data = base64.b64decode(base64_string)

    # Write the decoded data to a file
    with open(output_path, 'wb') as image_file:
        image_file.write(image_data)


def create_watchlist(watchlist_name):
    data = {
        "display_name": watchlist_name,
        # Add other required parameters for watchlist creation here
    }
    response = requests.post(f"{BASE_URL}/watchlist/", headers=HEADERS, json=data, verify=False)
    if response.status_code != 200:
        print(f"Error creating watchlist: {response.status_code}")
        return None
    return response.json()["data"]["watchlist_id"]


def detect_face_return_full_response(base64_img):
    """
    Detect faces in the given image.

    Parameters:
    - base64_img (str): The base64 encoded string of the image.

    Returns:
    - list: A list of base64 encoded strings of the detected faces.
    """
    print("Detect face")
    data = {
        "get_crops": True,
        "imgs": [{"img": base64_img}]
    }
    response = requests.post(f"{BASE_URL}/face/detect/", headers=HEADERS, json=data, verify=False)
    if response.status_code != 200:
        print(f"Error detecting faces: {response.text}")
        return []
    return response.status_code, response.json()


def detect_faces_returns_crops(base64_img):
    status, response = detect_face_return_full_response(base64_img)
    if status != 200:
        print(f"Error detecting faces: {response.text}")
        return []
    detected_faces_base64_list = [detection['img'] for detection in response["data"]["detections"][0]]
    return detected_faces_base64_list


def detect_and_add_all_pois_in_image_to_watchlist(base64_img, watchlist_id, poi_identifier_display_name="poi_identifier_display_name"):
    detected_faces_lst = detect_faces_returns_crops(base64_img)
    if detected_faces_lst:
        for face_base64 in detected_faces_lst:
            data = {
                "pois": [
                    {
                        "display_name": f"{poi_identifier_display_name}",
                        "display_img": face_base64,
                        "poi_notes": {
                            "file_name": poi_identifier_display_name
                        },
                        "poi_watchlists": [
                            watchlist_id
                        ],
                        "face": {
                            "force": True,
                            "save_crop": True,
                            "image_payload": {
                                "img": face_base64,
                                "detect": True,
                                "use_detector_lms": True,
                                "fail_on_multiple_faces": False
                            }
                        }
                    }
                ]
            }
            response = requests.post(f"{BASE_URL}/poi/", headers=HEADERS, json=data, verify=False)
            try:
                if response.status_code != 200 or response.json()["metadata"]["success_list"][0]["success"] is False:
                    print(f"Error creating POI: {response.text}")
                    continue
                else:
                    return response.json()["data"]
            except KeyError:
                print("Failed to add poi for image", response.json()["metadata"]["success_list"][0]["msg"])
                return None


def build_watchlist_and_add_pois_for_directory_of_images(directory_path, watchlist_name=None,watchlist_id=None):
    # Create a watchlist
    if watchlist_name is None and watchlist_id is not None:
        watchlist_id = create_watchlist(watchlist_name)
    elif watchlist_name is not None and watchlist_id is None:
        pass
    else:
        print("watchlist_id or watchlist_name is required ")
        return None

    # Get the total number of files that match the criteria
    total_files = sum(1 for filename in os.listdir(directory_path) if filename.endswith((".jpg", ".jpeg")))

    # Initialize a counter
    file_counter = 0
    # Add POIs to the watchlist
    for filename in os.listdir(directory_path):
        file_counter += 1
        print(f"Processing file {file_counter} of {total_files} - {filename}| directory - {directory_path}")
        if filename.endswith((".jpg", ".jpeg")):
            image_path = os.path.join(directory_path, filename)
            base64_img = image_to_base64(image_path)

            # Detect faces in the image
            detected_faces_base64 = detect_faces_returns_crops(base64_img)
            for face_base64 in detected_faces_base64:
                poi_id = detect_and_add_all_pois_in_image_to_watchlist(face_base64, watchlist_id) #ToDo add file name
                if not poi_id:
                    print(f"Failed to add POI for detected face in image: {image_path}")
                else:
                    print(f"Successfully added POI with ID: {poi_id} for detected face in image: {image_path}")

    return watchlist_id


def search_poi_in_watchlist(base64_img_face, watchlist_id, min_confidence, max_matches):
    data = {
        "get_crops": True,
        "min_confidence": min_confidence,
        "get_signature_payload": True,
        "max_matches": max_matches,
        "watchlists": [watchlist_id],
        "image_payload": {
            "img": base64_img_face,
            "detect": True,
            "use_detector_lms": True,
            "fail_on_multiple_faces": False
        }
    }
    response = requests.post(f"{BASE_URL}/face/search", headers=HEADERS, json=data, verify=False)
    try:
        output_list = []
        for item in response.json()["data"]["matches"]:
            for face in item['faces']:
                transformed_data = {
                    "poi_id": item["poi_id"],
                    "file name": item["display_name"],
                    "crop": item["display_img"],
                    "confidence": item["poi_confidence"],
                    "gender": face["face_attributes"]["gender_outcome"]
                }
                output_list.append(transformed_data)
        # print(output)
        # return response.json()["data"]["matches"]
        output = CustomOutput(output_list)
        return output
    except Exception:
        return None


def get_all_pois_from_watchlist(watchlist_id):
    """
    Fetch all POIs from a specific watchlist.

    Parameters:
    - watchlist_id (str): The ID of the watchlist from which to fetch the POIs.

    Returns:
    - list: A list of POIs associated with the given watchlist.
    """
    # Endpoint to get details of a specific watchlist
    url = f"{BASE_URL}/watchlist/{watchlist_id}/"

    response = requests.get(url, headers=HEADERS, verify=False)

    if response.status_code != 200:
        print(f"Error fetching POIs from watchlist: {watchlist_id}")
        return []

    # Extract POIs from the response
    pois = response.json()["data"]["pois"]

    return pois


if __name__ == "__main__":
    WATCHLIST_ID = create_watchlist("Test_before_cloud_2")
    # WATCHLIST_ID = '42a7f5b4-0848-492f-ab9a-1b904ee6666a'
    #
    one_face_path_img = "/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני/photo1696803996.jpeg"
    many_faces_path_img = "/home/gal/Pictures/Screenshot from 2023-10-16 22-52-03.png"
    # base_64_one_face = image_to_base64(one_face_path_img)
    base_64_many_faces = image_to_base64(many_faces_path_img)

    ###  Detect and add one poi to watchlist
    # # Get full response
    # print(detect_face_return_full_response(base_64_one_face))
    # # Get crops images respone
    # faces_base_64 = detect_faces_returns_crops(base_64_many_faces)

    # ### Detect and add poi to list
    res_data = detect_and_add_all_pois_in_image_to_watchlist(base_64_many_faces, watchlist_id=WATCHLIST_ID)
    # response = search_poi_in_watchlist(base_64_many_faces, WATCHLIST_ID, 0, 3)
    # print(response.json())
    ### Search in watchlist




























#     directory_path = "/home/gal/PycharmProjects/Nehedar/data/videos_red_telegram"
#     directory_path_of_images_to_search = "/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני"
#     desired_poi_image_path = "/home/gal/PycharmProjects/Nehedar/data/test/photo1696803996.jpeg"
#     watchlist_name = "MARK_RED_VIDEO_TELEGRAM_finaL_2"
#     # base_output_path = "/home/gal/PycharmProjects/Nehedar/data/output"
#     executor = ThreadPoolExecutor(max_workers=os.cpu_count())
#     # Build the watchlist and add POIs from the directory
#     watchlist_id = build_watchlist_and_add_pois(directory_path, watchlist_name)
#     if not watchlist_id:
#         print("No watchlist ID. Exiting.")
#         exit()
#
#     for filename in os.listdir(directory_path_of_images_to_search):
#         desired_poi_image_path = os.path.join(directory_path_of_images_to_search, filename)
#
#         ### Convert the desired POI image to base64 and search for it in the watchlist
#         desired_base64_img = image_to_base64(desired_poi_image_path)
#
#         executor.submit(add_image_to_wl)

        # ### Searching
        # matches = search_poi_in_watchlist(desired_base64_img, watchlist_id)
        #
        # # Print the matches
        # if not matches:
        #     print("No matches found.")
        # else:
        #     print(matches)
        #     for match in matches:
        #         base_dir_per_match = os.path.join(base_output_path, match["poi_id"])
        #         if os.path.exists(base_dir_per_match) is False:
        #             os.mkdir(base_dir_per_match)
        #         save_base64_image(match["display_img"], os.path.join(base_dir_per_match, "image.png"))
        #         save_dict_to_json(match, os.path.join(base_dir_per_match, "data.json"))
        #         print(f"Matched POI: {match['display_name']} with confidence: {match['poi_confidence']}")

        # watchlist_id = create_watchlist()
        # print(get_pois_from_watchlist(watchlist_id))




# if __name__ == "__main__":
#     directory_path = "/media/gal/T7 Shield/red_frames"
#     base_output_path = "/home/gal/PycharmProjects/Nehedar/data/output"
#     directory_path_of_images_to_search = "/media/gal/T7 Shield/blue_with_names"
#     watchlist_name = "real_red_1"
#
#     # Build the watchlist and add POIs from the directory
#     watchlist_id = build_watchlist_and_add_pois(directory_path, watchlist_name)
#     if not watchlist_id:
#         print("No watchlist ID. Exiting.")
#         exit()
#
#
#     for filename in os.listdir(directory_path_of_images_to_search):
#         desired_poi_image_path = os.path.join(directory_path_of_images_to_search, filename)
#
#         ### Convert the desired POI image to base64 and search for it in the watchlist
#         desired_base64_img = image_to_base64(desired_poi_image_path)
#
#         ### Searching
#         matches = search_poi_in_watchlist(desired_base64_img, watchlist_id)
#
#         # Print the matches
#         if not matches:
#             print("No matches found.")
#         else:
#             print(matches)
#             for match in matches:
#                 base_dir_per_match = os.path.join(base_output_path, match["poi_id"])
#                 if os.path.exists(base_dir_per_match) is False:
#                     os.mkdir(base_dir_per_match)
#                 save_base64_image(match["display_img"], os.path.join(base_dir_per_match, "image.png"))
#                 save_dict_to_json(match, os.path.join(base_dir_per_match, "data.json"))
#                 print(f"Matched POI: {match['display_name']} with confidence: {match['poi_confidence']}")
#
#     # watchlist_id = create_watchlist()
#     # print(get_pois_from_watchlist(watchlist_id))