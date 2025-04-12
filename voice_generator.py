import requests

def download_audio(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return False

def generate_voice(text, language='hi-IN', voice='c1t0dOAv2a9b19e3d32381e715de8e11dfb7e8795sJ8BCpctY_standard'):
    url = "https://aivoicegenerator.com/home/tryme_action/"
    
    # Headers based on the request information
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://aivoicegenerator.com",
        "referer": "https://aivoicegenerator.com/",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Brave\";v=\"134\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    # Get initial cookies by making a GET request first
    session = requests.Session()
    initial_response = session.get("https://aivoicegenerator.com/")
    csrf_token = session.cookies.get('csrf_cookie_name', '827e1517f5a9109f98b52b514ef3a255')
    
    # Payload data
    data = {
        "csrf_test_name": csrf_token,
        "front_tryme_language": language,
        "front_tryme_voice": voice,
        "front_tryme_text": text
    }
    
    try:
        response = session.post(url, headers=headers, data=data)
        response_json = response.json()
        
        if response_json['result']:
            return {
                'success': True,
                'audio_url': response_json['tts_uri']
            }
        else:
            return {
                'success': False,
                'message': response_json.get('message', 'Unknown error occurred')
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

if __name__ == "__main__":
    # Example Hindi text from the provided payload
    sample_text = """ज़िंदगी एक अजीब सफर है, जहाँ हर मोड़ पर नए इम्तिहान खड़े होते हैं। कभी हँसी की बारिश होती है, तो कभी ग़म के बादल घिर आते हैं। लोग मिलते हैं, साथ चलते हैं, फिर किसी मोड़ पर बिछड़ जाते हैं। कुछ रिश्ते नाम के होते हैं, तो कुछ बेनाम होकर भी दिल के सबसे करीब। मगर इस सफर में जो सबसे ज़रूरी है, वो है खुद से की गई मोहब्बत, क्योंकि जब दुनिया सवाल करे, तब भी खुद का साथ देना ही असली जीत होती है।"""
    
    # Get user input
    text = input("Enter the text to convert to speech (press Enter to use sample text): ").strip()
    if not text:
        text = sample_text
    
    language = input("Enter language code (press Enter for Hindi/hi-IN): ").strip() or "hi-IN"
    
    result = generate_voice(text, language)
    
    if result['success']:
        print("\nSuccess! Audio URL:", result['audio_url'])
        print("\nDownloading audio file...")
        
        # Generate filename using timestamp
        import time
        filename = f"generated_audio_{int(time.time())}.mp3"
        
        if download_audio(result['audio_url'], filename):
            print(f"\nAudio saved as: {filename}")
        else:
            print("\nFailed to download audio file")
    else:
        print("\nError:", result['message'])
