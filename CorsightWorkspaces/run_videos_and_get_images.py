import json
import time

import requests

from CorsightWorkspaces import PARAMETERS

BASE_URL = "localhost"
TOKEN = PARAMETERS.access_token


def get_all_crops_from_video(video_path, video_name, token, analysis_quality="deep"):
    camera = create_camera(video_path, video_name, token, analysis_quality)
    camera_id = camera['camera_id']

    start_camera(camera_id, token)

    camera = get_camera(camera_id, token)

    while camera['camera_status']['status'] == 1:
        time.sleep(2)
        camera = get_camera(camera_id, token)

    return get_appearances(camera_id, token)


def create_camera(video_path, video_name, token, analysis_quality):
    url = f"https://{BASE_URL}:5002/cameras/"

    payload = json.dumps({
        "description": video_name,
        "capture_config": {"capture_address": video_path, "mode": "video"},
        "config": {"analysis_quality": analysis_quality}
    })
    headers = get_headers(token)

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    if response.status_code != 200:
        raise Exception(f"Failed to create camera: {response.status_code}")

    return response.json()["data"]


def start_camera(camera_id, token):
    url = f"https://{BASE_URL}:5002/cameras/{camera_id}/start/"

    payload = json.dumps({
        "analyze": True
    })
    headers = get_headers(token)

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    if response.status_code != 200:
        raise Exception(f"Failed to start camera: {response.status_code}")


def get_camera(camera_id, token):
    url = f"https://{BASE_URL}:5002/cameras/{camera_id}/"

    headers = get_headers(token)

    response = requests.request("GET", url, headers=headers, verify=False)

    if response.status_code != 200:
        raise Exception(f"Failed to start camera: {response.status_code}")

    return response.json()['data']


def get_appearances(camera_id, token):

    url = f"https://{BASE_URL}:5003/history/"

    payload = json.dumps({
        "cam_ids": [camera_id]
    })
    headers = get_headers(token)

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    appearances = []

    if response.status_code == 200:
        appearances = response.json()["data"]["matches"]
    else:
        raise Exception(f"Failed to get appearances: {response.status_code}")

    return appearances


def get_headers(token):
    return {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }


if __name__ == '__main__':
    crops = get_all_crops_from_video("/home/sc/share/סרטוני שבויים/449901611917784214.MP4", "video_name_example.mp4", TOKEN, "balanced")

