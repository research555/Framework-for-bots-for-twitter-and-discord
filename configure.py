from twitivity import Activity
import os

if __name__ == "__main__":
    API_KEY = os.getenv('conkey')
    API_SECRET_KEY = os.getenv('consec')
    ACCESS_TOKEN = os.getenv('acctok')
    ACCESS_TOKEN_SECRET = os.getenv('accsec')
    ENV_NAME = 'finaldev'

    activity = Activity()
    #activity.refresh(webhook_id='1362000677824851974')
    print(activity.register_webhook(callback_url="https://57bea0136010.ngrok.io/twitter/callback"))
    print(activity.subscribe())
    print(activity.webhooks())
