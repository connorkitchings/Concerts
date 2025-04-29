import requests

def make_api_request(endpoint: str, version: str = "v2") -> dict:
    url_templates = {
        "v1": f"https://elgoose.net/api/v1/{{}}.json?",
        "v2": f"https://elgoose.net/api/v2/{{}}.json?",
    }
    url = url_templates.get(version, "").format(endpoint)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
