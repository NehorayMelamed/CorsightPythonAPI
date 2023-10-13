import requests
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

url = 'http://127.0.0.1:8000/detect_face/'
watchlist_id = "42a7f5b4-0848-492f-ab9a-1b904ee6666a"
image_path = '/home/gal/PycharmProjects/Nehedar/data/output/match_results/sess_2/match_results/image_179_face_1_match_0/original_full_image.png'

base64_image = image_to_base64(image_path)
response = requests.post(url, json={'base64_img': base64_image, 'get_crops': True})

# print(response.json())
