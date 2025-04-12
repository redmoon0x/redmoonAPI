import requests
import json
from typing import Union , Literal

RATIO = Literal[
    "1:1",
    "16:9",
    "9:16",
    "3:2",
    "4:3",
    "5:4"
]

MODELS = Literal[
    "flux-schnell",
    "imagen-3-fast",
    "imagen-3",
    "recraft-v3"
]

STYLES = Literal

def generate_image(prompt, model=Union[str,MODELS], style="none",
                   aspect_ratio="9:16"):  # flux-schnell, "imagen-3-fast", "imagen-3", "recraft-v3":

    url = "https://www.pixelmuse.studio/api/predictions"

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://www.pixelmuse.studio",
        "referer": "https://www.pixelmuse.studio/",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    payload = {
        "prompt": prompt,
        "model": model,
        "style": style,
        "aspect_ratio": aspect_ratio  # only 1.1 is available for now
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None




if __name__ == "__main__":
    Prompt = '''
            An cool company logo of classy watches with proffesional and attractive loonof company and text will be related to  classy watches
             '''
    result = generate_image(
        prompt=Prompt,
        aspect_ratio="16:9",
        model="imagen-3"    )
    if result:
        print(result["output"])