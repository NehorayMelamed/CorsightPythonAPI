import requests

from CorsightWorkspaces.files import write_dict_to_json_file

KEYS_AND_DATA_JSON = "/home/gal/PycharmProjects/Nehedar/CorsightWorkspaces/keys_and_data.json"
url = "https://localhost:5004/auth/login/"
username = "Gal"
password = "------"
session_time = 99999999
headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "username": username,
    "password": password,
    "session_time": session_time
}

def authenticate():
    response = requests.post(url, headers=headers, data=data, verify=False)
    if response.status_code != 200:
        print("Authentication process failed")
        return False
    write_dict_to_json_file(response.json(), KEYS_AND_DATA_JSON)
    return True

if __name__ == '__main__':
    authenticate()
    # # The verify=False is to skip SSL verification, similar to --insecure in curl
    # response = requests.post(url, headers=headers, data=data, verify=False)
    # response =response.json()
    #
    # print(response)




