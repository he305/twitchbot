import requests
import pprint
import json

def main():
    emotes = requests.get("https://twitchemotes.com/api_cache/v3/subscriber.json").json()

    with open('emotes.txt', mode='w', encoding='utf8') as f:
        json.dump(emotes, f)

if __name__ == "__main__":
    main()