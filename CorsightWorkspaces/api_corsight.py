import shutil

import base64
import time
from io import BytesIO
from PIL import Image

import requests
from PIL import Image, ImageDraw
import base64

from CorsightWorkspaces import PARAMETERS
from CorsightWorkspaces.mark_usfull_api import search_img_in_app_db, get_appearances

BASE_URL = "https://localhost:8080/poi_db"
HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {PARAMETERS.access_token}"
}

import os
from PIL import Image


def save_detected_faces(output, directory_path):
    print(output)
    # Ensure the directory exists
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Extract the base64 image and detections
    base64_img = output['data']['detections'][0][0]['img']
    detections = [detection['bbox'] for detection in output['data']['detections'][0]]

    # Save the image with bounding boxes
    image_with_boxes_path = os.path.join(directory_path, "image_with_boxes.jpg")
    draw_and_save_image(base64_img, detections, image_with_boxes_path)

    # Create a sub-directory for cropped faces
    cropped_faces_dir = os.path.join(directory_path, "cropped_faces")
    if not os.path.exists(cropped_faces_dir):
        os.makedirs(cropped_faces_dir)
    # Extract and save cropped faces
    from io import BytesIO
    import base64

    img_data = base64.b64decode(base64_img)
    img = Image.open(BytesIO(img_data))

    for idx, detection in enumerate(detections):
        cropped_face = img.crop((detection['x1'], detection['y1'], detection['x2'], detection['y2']))
        cropped_face_path = os.path.join(cropped_faces_dir, f"face_{idx + 1}.jpg")
        cropped_face.save(cropped_face_path)

    print(f"Saved image with bounding boxes at: {image_with_boxes_path}")
    print(f"Saved cropped faces in directory: {cropped_faces_dir}")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def base64_to_image_path(base64_string, output_path):
    """
    Convert a base64 encoded string to an image and save it to the specified path.

    Parameters:
    - base64_string (str): The base64 encoded string of the image.
    - output_path (str): The path where the image should be saved.

    Returns:
    - None
    """
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    img.save(output_path)


def draw_and_save_image(base64_img, detections, save_path):
    # Convert base64 to Image
    img_data = base64.b64decode(base64_img)
    img = Image.open(BytesIO(img_data))
    draw = ImageDraw.Draw(img)

    # Draw bounding boxes
    for bbox in detections:
        draw.rectangle([(bbox['x1'], bbox['y1']), (bbox['x2'], bbox['y2'])], outline="red", width=2)

    # Save the image
    img.save(save_path)


def create_watchlist(display_name):
    data = {"display_name": display_name}
    response = requests.post(f"{BASE_URL}/watchlist/", headers=HEADERS, json=data, verify=False)
    return response.json()


def detect_face(base64_img):
    data = {
        "get_crops": True,
        "imgs": [{"img": base64_img}]
    }
    response = requests.post(f"{BASE_URL}/face/detect/", headers=HEADERS, json=data, verify=False)
    return response.json()


def analyze_face(base64_img):
    data = {
        "image_payload": {
            "img": base64_img,
            "detect": False,
            "use_detector_lms": True,
            "fail_on_multiple_faces": True
        },
        "get_signature_payload": False
    }
    response = requests.post(f"{BASE_URL}/face/analyze/", headers=HEADERS, json=data, verify=False)
    return response.json()


def create_poi(display_name, display_img, watchlist_id, poi_id):
    data = {
        "pois": [{
            "display_name": display_name,
            "display_img": display_img,
            "poi_consent": {
                "consent": 2,
                "review_time": 1658224960.830217
            },
            "poi_notes": {
                "properties": {
                    "additionalProp1": 0,
                    "additionalProp2": 0,
                    "additionalProp3": 0
                },
                "free_notes": ""
            },
            "poi_watchlists": [watchlist_id],
            "poi_id": poi_id,
            "face": {
                "force": False,
                "save_crop": True,
                "image_payload": {
                    "img": display_img,
                    "detect": False,
                    "use_detector_lms": True,
                    "fail_on_multiple_faces": True
                }
            }
        }]
    }
    response = requests.post(f"{BASE_URL}/poi/", headers=HEADERS, json=data, verify=False)
    return response.json()


def add_faces_to_poi(poi_id, base64_img):
    data = {
        "faces": [{
            "image_payload": {
                "img": base64_img,
                "detect": False,
                "use_detector_lms": True,
                "fail_on_multiple_faces": True
            },
            "force": False,
            "save_crop": True
        }]
    }
    response = requests.post(f"{BASE_URL}/poi/{poi_id}/add_faces/", headers=HEADERS, json=data, verify=False)
    return response.json()


def compare_faces(face_ref_b64, face_test_b64):
    data = {
        "face_ref": {
            "image_payload": {
                "img": face_ref_b64,
                "detect": False,
                "use_detector_lms": True,
                "fail_on_multiple_faces": True
            }
        },
        "face_test": {
            "image_payload": {
                "img": face_test_b64,
                "detect": False,
                "use_detector_lms": True,
                "fail_on_multiple_faces": True
            }
        },
        "convert_to_conf": True
    }
    response = requests.post(f"{BASE_URL}/face/compare/", headers=HEADERS, json=data, verify=False)
    return response.json()


def search_face_in_poi_db(base64_img, watchlist_id):
    data = {
        "get_crops": True,
        "get_signature_payload": False,
        "min_confidence": 100,
        "max_matches": 300,
        "watchlists": [watchlist_id],
        "image_payload": {
            "img": base64_img,
            "detect": False,
            "use_detector_lms": True,
            "fail_on_multiple_faces": True
        }
    }
    response = requests.post(f"{BASE_URL}/face/search/", headers=HEADERS, json=data, verify=False)
    return response.json()



def compare_faces_in_directory(input_directory, image_path):
    # Detect the face in the given image_path
    base64_image = image_to_base64(image_path)
    detect_face_output = detect_face(base64_image)
    if not detect_face_output['metadata']['success_list'][0]['success']:
        print("Failed to detect face in the given image.")
        return

    detected_face_base64 = detect_face_output['data']['detections'][0][0]['img']

    # Iterate over all images in the input_directory and compare with detected_face
    match_confidences = []
    for file_name in os.listdir(input_directory):
        file_path = os.path.join(input_directory, file_name)
        if os.path.isfile(file_path):
            base64_img_to_compare = image_to_base64(file_path)
            detected_faces_output = detect_face(base64_img_to_compare)
            if detected_faces_output['metadata']['success_list'][0]['success']:
                max_confidence_for_image = 0
                for detected_face in detected_faces_output['data']['detections'][0]:
                    detected_face_base64_to_compare = detected_face['img']
                    match_confidence_output = compare_faces(detected_face_base64, detected_face_base64_to_compare)
                    try:
                        max_confidence_for_image = max(max_confidence_for_image, match_confidence_output['data']['match_confidence'])
                    except KeyError:
                        print(max_confidence_for_image)
                match_confidences.append((file_name, max_confidence_for_image))

    # Sort by match confidence and get top 5
    top_5_matches = sorted(match_confidences, key=lambda x: x[1], reverse=True)[:5]

    # Print the top 5 matches
    for file_name, confidence in top_5_matches:
        print(f"Image: {file_name}, Match Confidence: {confidence}")

    return top_5_matches


def get_pois_from_watchlist(watchlist_id):
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


def search_img_in_videos(b64_img, token, min_confidence=10, max_matches=10):
    matched_appearances = []

    status_code, matches = search_img_in_app_db(b64_img=b64_img, token=token, min_confidence=min_confidence, max_matches=max_matches)

    if status_code != 200:
        print(f"Failed, status_code: {status_code}")

    for match in matches:
        status, appearance = get_appearances(appearance_id=match['appearance_id'])
        if not appearance:
            continue

        matched_appearances.append(
            {"appearance_id": appearance["appearance_data"]["appearance_id"], "video_name": appearance["camera_data"]["camera_description"],
             "start_time": appearance["appearance_data"]["utc_time_started"],
             "crop": appearance["crop_data"]['face_crop_img']})

    return matched_appearances


if __name__ == '__main__':

    pass
    ### Detect
    image_1 = image_to_base64("/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני/photo1696803766.jpeg")
    detect_face_output = detect_face(image_1)
    print(detect_face_output)
    id = get_pois_from_watchlist("3b02bbbb-17c2-43e4-9437-ed8b33257534")
    print(id)
    print(len((id)))
    print(len(os.listdir("/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני")))
    #### Compare
    # save_detected_faces(detect_face_output, "/home/gal/PycharmProjects/Nehedar/data/output")
    image_1 = image_to_base64("/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני/photo1696803896.jpeg")
    image_2 = image_to_base64(
       "/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני/photo1696803919.jpeg")
    start = time.process_time()
    #
    # max = 0
    # match_confidence = compare_faces(image_1, image_2)
    # if match_confidence > max:
    #     max = match_confidence
    # base_list_dir = "/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני"
    # for image_path in os.listdir(base_list_dir):
    #
    # print(time.process_time() - start)
    #
    # # print(analyze_face(image_1))

    # Example usage:
    # input_directory_path = "/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני"
    # image_path_to_compare = "/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני/photo1696803896.jpeg"
    # start = time.process_time()
    # print(compare_faces_in_directory(input_directory_path, image_path_to_compare))
    # print("Total of images:", len(os.listdir(input_directory_path)))
    # print("Total running time",time.process_time() - start )
    # print(1)