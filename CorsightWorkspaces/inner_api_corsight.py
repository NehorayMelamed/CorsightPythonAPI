import requests
from PIL import Image
import base64
import io
from CorsightWorkspaces import PARAMETERS


def detect_face(image_path, api_url="https://localhost:8080/poi_db/face/detect/", token=PARAMETERS.access_token):
    # Load and encode image in base64
    with Image.open(image_path) as image:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Prepare headers and data for the request
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "get_crops": True,
        "imgs": [{"img": img_str}]
    }

    # Send the request
    response = requests.post(api_url, headers=headers, json=data, verify=False)

    # Return the response
    return response.json()


if __name__ == '__main__':
    response = detect_face("/home/gal/PycharmProjects/Nehedar/data/blue/telegram/כחול-ידני/photo1696803896.jpeg")
    print(response)
