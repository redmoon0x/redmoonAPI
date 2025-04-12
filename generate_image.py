import time
import requests

def main():
    prompt = input("Enter image description: ")

    url = "https://ai-api.magicstudio.com/api/ai-art-generator"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.7",
        "origin": "https://magicstudio.com",
        "referer": "https://magicstudio.com/",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    data = {
        "prompt": prompt,
        "output_format": "bytes",
        "user_profile_id": "null",
        "anonymous_user_id": "bbc381a1-0924-4b70-a08a-64508b871262",
        "request_timestamp": str(time.time()),
        "user_is_subscribed": "false",
        "client_id": "pSgX7WgjukXCBoYwDM8G8GLnRRkvAoJlqa5eAVvj95o"
    }

    print("Sending request to generate image...")
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        with open("generated_image.png", "wb") as f:
            f.write(response.content)
        print("Image successfully saved as generated_image.png")
    else:
        print("Failed to generate image. Status code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    main()
