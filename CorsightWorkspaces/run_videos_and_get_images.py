import json
import os
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


def get_appearances( token, camera_id=None, after_id=None):

    url = f"https://{BASE_URL}:5003/history/"
    if camera_id is None:
        cam_ids = []
    else:
        cam_ids = [camera_id]
    if after_id is not None:
        payload = json.dumps({
            "cam_ids": cam_ids,
            "after_id": after_id
        })
    else:
        payload = json.dumps({
            "cam_ids": cam_ids
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


def running_on_videos(base_directory):
    if os.path.exists(base_directory):
        for video_name in os.listdir(base_directory):
            print(video_name)
            full_path_to_current_video = os.path.join(base_directory, video_name)
            current_crops = get_all_crops_from_video(full_path_to_current_video, video_name, TOKEN, "balanced")



if __name__ == '__main__':
    crops = get_all_crops_from_video("/home/sc/share/Videos_from_telegram/273925376807776989.MP4", "check_corsight.mp4", TOKEN, "deep")
    print(crops)
    # token = PARAMETERS.access_token
    # all_apperanaces = get_appearances(token, after_id="be07e154-c33e-41af-b069-d4ee5a488b78")
    # base_directory = "/home/sc/share/red data naor"
    # running_on_videos(base_directory)
