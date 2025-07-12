import requests

def translate(text, source="en", target="fr"):
    url = "https://libretranslate.com/translate"
    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["translatedText"]
    else:
        return f"Error: {response.status_code} - {response.text}"


print(translate("hello", source="en", target="es")) 
