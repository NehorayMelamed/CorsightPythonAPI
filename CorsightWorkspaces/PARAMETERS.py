from files import load_json_from_file

username = "Gal"
password = "Galb9389"
json_keys_data = load_json_from_file("keys_and_data.json")
access_token = json_keys_data["access_token"]

