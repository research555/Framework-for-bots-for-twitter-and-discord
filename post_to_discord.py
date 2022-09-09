import requests
import json
import traceback
import os
from dotenv import load_dotenv

load_dotenv()

def PostToDiscord(message, url, tweet_id=None):
    headers = {}
    headers['content-type'] = 'application/json'

    try:

        if tweet_id is not None:
            message_data = {'content': message}
            message_response = requests.post(url=url, headers=headers, data=json.dumps(message_data)).status_code  # sends tweet to discord
            tweet_id_data = {'content': tweet_id}
            tweet_id_response = requests.post(url=url, headers=headers, data=json.dumps(tweet_id_data)).status_code  # sends tweet id to discord for easier assignment
            return [message_response, tweet_id_response]

        else:
            message_data = {'content': message}
            message_response = requests.post(url=url, headers=headers, data=json.dumps(message_data)).status_code
            return [message_response]

    except Exception:
        e = traceback.format_exc()
        exception_data = {'content': e}
        error_response = requests.post(url=url, headers=headers, data=json.dumps(exception_data)).status_code  #posts traceback on discord
        return [error_response]