"""For building watchlist for the red IMAGES"""

import argparse
import os

from pydantic import BaseModel
import tqdm
from sc_sdk.domain.api_clients.api_client import APIClient

from sc_sdk.domain.api_clients.poi_db_client import FaceClient, WatchlistClient
from sc_sdk.domain.utils.img import image_path_to_base64
from sc_sdk.domain.utils.timer import get_timestamp

from CorsightWorkspaces import PARAMETERS

CHUNK_SIZE = 30


class CropRecord(BaseModel):
    poi_name: str
    img: str
    confidence: float
    watchlist: str


def get_watchlist_id(watchlist_name):
    watchlist_client = WatchlistClient()
    resp, watchlists = watchlist_client.get_all_watchlists(False)

    watchlist_id = None
    for watchlist in watchlists:
        if watchlist["display_name"] == watchlist_name:
            watchlist_id = watchlist["watchlist_id"]
            break

    if not watchlist_id:
        raise Exception("Watchlist does not exist")

    return watchlist_id


def compare_db(probe_dir, token, output_dir, watchlist_name=None, min_confidence=10, max_matches=10):
    failed_images = []
    matches_dict = {}
    APIClient.user_session_token = token
    face_client = FaceClient()

    watchlist_id = get_watchlist_id(watchlist_name) if watchlist_name else None

    for probe_name in tqdm.tqdm(os.listdir(probe_dir)):
        probe_image = image_path_to_base64(os.path.join(probe_dir, probe_name))
        if not probe_image:
            failed_images.append(probe_name)
            continue

        status_code, matches = face_client.search_faces_in_image(img=probe_image, min_confidence=min_confidence, max_matches=max_matches,
                                                     watchlist_ids=[watchlist_id] if watchlist_id else None, get_crops=True,
                                                     detect=True)

        if status_code != 200:
            failed_images.append(probe_name)
            continue

        for i, poi_match in enumerate(matches):
            test_probe_name = f"{probe_name}.{i}"
            if not poi_match["matches"]:
                continue
            matches_dict[test_probe_name] = [CropRecord(poi_name=test_probe_name, img=probe_image, confidence=100, watchlist="Search")]
            for match in poi_match["matches"]:
                print(poi_match)
                matches_dict[test_probe_name].append(CropRecord(poi_name=match['display_name'], img=match['display_img'], confidence=match['poi_confidence'],
                                                           watchlist=match['watchlists'][0]['display_name']))

    create_html(matches_dict, output_dir)

    print(f"Failed in images: {failed_images}")


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

    for probe_name, poi_records in matches_dict.items():
        html_content += f"<h2>{probe_name}:</h2>\n"
        html_content += "<div class='data-list'>"
        for poi_record in poi_records:
            html_content += "<div class='data-item'>"
            # Display the image
            html_content += f"<img src='data:image/png;base64,{poi_record.img}' alt='{poi_record.poi_name}'/><br/>"
            html_content += f"<span>name: {poi_record.poi_name}</span><br/>"
            html_content += f"<span>confidence: {poi_record.confidence:.2f}</span><br/>"
            html_content += f"<span>watchlist: {poi_record.watchlist}</span>"
            html_content += "</div>"
        html_content += "</div><br/>\n"

    html_content += """
    </body>
    </html>
    """

    # Now, save the html_content to a file
    with open(os.path.join(output_dir, f"output{get_timestamp()}.html"), "w") as f:
        f.write(html_content)


def setup():
    parser = argparse.ArgumentParser(description="Build process Runner")
    parser.add_argument("--search_dir", help="The directory we want to search in")
    parser.add_argument("--watchlist_name", default=None, help="The watchlist we want to compare to")
    parser.add_argument("--username", help="Fortify username")
    parser.add_argument("--password", help="Fortify password")
    parser.add_argument("--min_confidence", type=float, default=10, help="min confidence")
    parser.add_argument("--max_matches", type=int, default=10, help="max matches to get per each search")
    parser.add_argument("--output_dir", help="The directory to create the html in")

    return parser.parse_args()


if __name__ == '__main__':
    # args = setup()
    search_dir = "/home/gal/PycharmProjects/Nehedar/data/real_data/blue_data"
    watchlist_name = "blue_images_for_cloud_test"
    username = "Gal"
    password = "Galb9389"
    min_confidence = 70
    max_matches = 5
    output_dir = "/home/gal/PycharmProjects/Nehedar/data/output/htmls_output"


    compare_db(probe_dir=search_dir, watchlist_name=watchlist_name, token=PARAMETERS.token,
               min_confidence=min_confidence, max_matches=max_matches, output_dir=output_dir)
