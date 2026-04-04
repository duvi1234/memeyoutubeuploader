import requests

def fetch_meme_text():
    """
    Fetches a meme title (text) from meme-api.com.

    Returns:
        str: Meme title or fallback text in case of failure.
    """
    try:
        response = requests.get("https://meme-api.com/gimme")
        if response.status_code == 200:
            data = response.json()
            return data.get("title", "Funny Meme!")
        else:
            print(f"Error: Received status code {response.status_code}")
            return "Couldn't load meme"
    except Exception as e:
        print(f"Exception occurred while fetching meme: {e}")
        return "Error fetching meme"
