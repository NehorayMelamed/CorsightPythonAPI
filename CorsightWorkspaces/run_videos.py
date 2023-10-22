import argparse
import os
import time

from sc_sdk.domain.api_clients.api_client import APIClient
from sc_sdk.domain.api_clients.cameras_client import CamerasClient
from sc_sdk.domain.common import AnalysisQuality, AnalysisModes
from sc_sdk.domain.objects.stream_config import CaptureStreamConfig, CaptureStreamConfigParams, StreamConfig

from CorsightWorkspaces import PARAMETERS


def run_videos(video_dir):
    cameras_client = CamerasClient()
    cameras_client.set_analysis_mode(AnalysisModes.investigate.value)

    for video_name in os.listdir(video_dir):
        cam_dict = dict(capture_config=CaptureStreamConfig(mode=CaptureStreamConfigParams.Modes.video.value,
                                                           address=os.path.join(video_dir, video_name)),
                        config=StreamConfig(analysis_quality=AnalysisQuality.deep),
                        description=video_name)

        status_code, camera, _ = cameras_client.create_camera(**cam_dict)
        print(f"starting camera: {video_name}")
        cameras_client.start_camera(camera.camera_id, analyze=True)

        time.sleep(.1)

        status_code, running_camera = cameras_client.get_camera(camera_id=camera.camera_id)
        while running_camera.status_data.is_running:
            time.sleep(2)
            status_code, running_camera = cameras_client.get_camera(camera_id=camera.camera_id)

        print(f"Finished to run camera: {video_name} successfully")


def setup():
    parser = argparse.ArgumentParser(description="Build process Runner")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--video_dir")
    return parser.parse_args()
#

if __name__ == '__main__':
    # args = setup()
    APIClient.user_session_token = PARAMETERS.access_token
    run_videos("/media/gal/T7 Shield/red data naor")
