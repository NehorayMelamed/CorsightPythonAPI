import base64
import os

import requests
import json

from CorsightWorkspaces import PARAMETERS

BASE_URL_8080 = "https://localhost:8080"
BASE_URL_5003 = "https://localhost:5003"

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {PARAMETERS.access_token}"
}
output_base = "/home/gal/PycharmProjects/Nehedar/data/output/match_results/sess_2"


def search_img_in_videos(b64_img, token=PARAMETERS.access_token, min_confidence=10, max_matches=10):
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
             "crop": appearance["crop_data"]['face_crop_img'], "confidence": match["match_confidence"]})

    return matched_appearances


def search_img_in_app_db(b64_img, token=PARAMETERS.access_token, min_confidence=10, max_matches=10):
    payload = json.dumps({
        "min_confidence": min_confidence,
        "max_matches": max_matches,
        "image_payload": {
            "img": b64_img,
            "detect": True,
            "use_detector_lms": True,
            "fail_on_multiple_faces": False
        }
    })

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url=f"{BASE_URL_5003}/history/search/app_img/", headers=headers, data=payload, verify=False)

    print(response.text)
    matches = None
    if response.status_code:
        try:
            matches = response.json()['data']['matches']
        except KeyError:
            return 999, []
    return response.json(), matches


def get_appearances(appearance_id, token=PARAMETERS.access_token):
    import requests
    import json

    url = f"{BASE_URL_5003}/history/"

    payload = json.dumps({
        "appearance_ids": [
            appearance_id
        ]
    })
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    appearance = None

    if response.status_code == 200:
        matches = response.json()["data"]["matches"]
        if matches:
            appearance = matches[0]

    return response, appearance


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


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

def save_dict_to_json(data, output_path):
    """
    Save a dictionary to a JSON file.

    Parameters:
    - data (dict): The dictionary to save.
    - output_path (str): The path where the JSON file should be saved.
    """
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def detect_face(base64_img):
    print("Detect face")
    """
    Detect faces in the given image.

    Parameters:
    - base64_img (str): The base64 encoded string of the image.

    Returns:
    - list: A list of base64 encoded strings of the detected faces.
    """
    data = {
        "get_crops": True,
        "imgs": [{"img": base64_img}]
    }
    response = requests.post(f"{BASE_URL_8080}/poi_db/face/detect/", headers=HEADERS, json=data, verify=False)
    if response.status_code != 200:
        print(f"Error detecting faces: {response.text}")
        return []
    print("Faced detected")
    # Extract the base64 strings of the detected faces
    detected_faces_base64 = [detection['img'] for detection in response.json()["data"]["detections"][0]]
    return detected_faces_base64





if __name__ == '__main__':
    directory_path = "/home/gal/PycharmProjects/Nehedar/CorsightWorkspaces/blue_data"
    directory_path = "/home/gal/PycharmProjects/Nehedar/CorsightWorkspaces/grandma"
    output_result = os.path.join(output_base, "match_results")
    if os.path.exists(output_result) is False:
        os.mkdir(output_result)
    all_files = os.listdir(directory_path)

    sorted_files = sorted([f for f in all_files if f.startswith("image_")],
                          key=lambda x: int(x.split('_')[1].split('.')[0]))
    for image in sorted_files:
        base64_image = image_to_base64(os.path.join(directory_path, image))
        faces_detections = detect_face(base64_image)
        for face_count, detected_face_in_image in enumerate(faces_detections):
            match_results = search_img_in_videos(detected_face_in_image)
            base_name = os.path.basename(image)
            image_name_without_extension = os.path.splitext(base_name)[0]
            image_directory_path = os.path.join(output_result, f"{image_name_without_extension}_face_{face_count}")
            if match_results:
                for match_count, match_result in enumerate(match_results):
                    match_in_image_path = os.path.join(f"{image_directory_path}_match_{match_count}")
                    if os.path.exists(match_in_image_path) is False:
                        os.mkdir(match_in_image_path)
                    save_base64_image(base64_image, os.path.join(match_in_image_path, "original_full_image.png"))
                    save_base64_image(detected_face_in_image, os.path.join(match_in_image_path, "original_face_image.png"))
                    save_base64_image(match_result["crop"], os.path.join(match_in_image_path, "match.png"))
                    save_dict_to_json(match_result, os.path.join(match_in_image_path, "data.json"))


                    #1. 0. 0
                    #1. 0. 1