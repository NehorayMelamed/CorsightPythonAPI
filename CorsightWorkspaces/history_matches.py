import base64
import os

import cv2
from sc_sdk.domain.api_clients.api_client import APIClient
from tqdm import tqdm

from sc_sdk.domain.api_clients.history_client import HistoryClient
from sc_sdk.domain.objects.history_query import HistoryDBQuery
from sc_sdk.domain.utils.img import image_path_to_base64
from sc_sdk.domain.utils.timer import get_timestamp

from CorsightWorkspaces import PARAMETERS

history_client = HistoryClient()

min_confidence = 30
max_matches = 10


def search_image(image_path, failed_images):
    image = image_path_to_base64(image_path)
    if not image:
        failed_images.append(image_path)
        return

    status_code, get_appearances_matches = history_client.search_match_faces_in_image(img=image, min_confidence=min_confidence,
                                                                         max_matches=max_matches, detect=True)

    if status_code != 200:
        failed_images.append(image_path)
        return

    ret_appearances = {}

    for i, match in enumerate(get_appearances_matches):
        probe_name = f"{image_path}.{i}"
        ret_appearances[probe_name] = []

        query_dict = {HistoryDBQuery.Fields.appearance_ids.value: [match["appearance_id"] for match in match["matches"]]}

        history_query = HistoryDBQuery(**query_dict)

        appearances = history_client.get_appearances(query_object=history_query)[1]

        for match in match["matches"]:
            for j, appearance in enumerate(appearances):
                print(appearance)
                if appearance.appearance_id == match["appearance_id"]:
                    ret_appearances[probe_name].append({**appearance.dict(), "match_confidence": match["match_confidence"]})

    return ret_appearances


def create_html(matches_dict, output_dir):
    html_content = """
    <html>
    <head>
        <title>Data Display</title>
        <style>
            .data-item {
                display: inline-block;
                margin: 10px;
                text-align: center;
                width: 200px;  /* adjust as needed */
                height: 300px; /* adjust as needed */
                overflow: hidden;
                vertical-align: top;
            }

            img {
                width: 100px;   /* adjust as needed */
                height: 100px;  /* adjust as needed */
            }

            .data-list > .data-item:first-child {
                background-color: yellow;
            }
        </style>
    </head>
    <body>
    """

    for probe_name, matches in matches_dict.items():
        html_content += f"<h2>{probe_name}:</h2>\n"
        html_content += "<div class='data-list'>"
        if matches:
            for match_name, appearances in matches.items():
                html_content += f"\n"
                for appearance in appearances:
                    html_content += "<div class='data-item'>"
                    # Display the image
                    html_content += f"<img src='data:image/png;base64,{appearance['crop_data']['face_crop_img']}' alt='{appearance['appearance_data']['appearance_id']}'/><br/>"
                    html_content += f"<span>Video Name: {appearance['camera_data']['camera_description']}</span><br/>"
                    html_content += f"<span>confidence: {appearance['match_confidence']:.2f}</span><br/>"
                    html_content += f"<span>watchlist: {appearance['appearance_data']['utc_time_started']}</span>"
                    html_content += "</div>"
        html_content += "</div><br/>\n"

    html_content += """
    </body>
    </html>
    """

    # Now, save the html_content to a file
    with open(os.path.join(output_dir, f"output{get_timestamp()}.html"), "w") as f:
        f.write(html_content)


def poi_folders_in_base_directory(directory):
    POIS = os.listdir(directory)
    failed_images = []

    images_results = {}
    for poi in tqdm(POIS):
        images_results[poi] = search_image(f"{directory}/{poi}", failed_images)

    create_html(images_results, f"{directory}/../")


if __name__ == '__main__':
    APIClient.user_session_token = PARAMETERS.access_token
    poi_folders_in_base_directory(directory='/home/gal/PycharmProjects/Nehedar/CorsightWorkspaces/finall_data/blue_data')