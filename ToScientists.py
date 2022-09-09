from tweepy import Stream
from tweepy.streaming import StreamListener
from post_to_discord import *
from sql_functions import *
from twitter_auth import TSTwitterAuth
from dotenv import load_dotenv
import os
import time
import pdb

# Listen to replies

cursor, mydb = DatabaseAuth()
api, auth = TSTwitterAuth()
class StdOutListener(StreamListener):

    def on_error(self, status):
        return status

    def on_status(self, status):
        truncated = status.truncated
        print('ifh')

        if truncated is True:
            tweet = status.extended_tweet['full_text']
            if "#atas" in tweet.lower():
                # Define variables
                tweet_id = status.id
                op_handle = status.user.screen_name
                full_name = status.user.name
                op_url = f"https://twitter.com/{op_handle}/status/{tweet_id}"
                message = f'``` Handle: {op_handle},\n Name: {full_name},\n URL: {op_url},\n\n Question: {tweet}```'
                second_message = f'({tweet_id}) [bme] '

                # Log tweet in database
                LogTweet(tweet_id, op_handle, full_name, op_url)

                # Post to Discord
                load_dotenv()
                url = os.getenv('ASSIGN_MENTOR_URL')
                PostToDiscord(message, url, second_message)

                # Send OP a message
                time.sleep(10)
                api.update_status(f'@{op_handle} Hang tight! We are fetching you some mentors.'
                                  f' Expect an answer within 24 hours. :)', tweet_id)
        if truncated is False:
            tweet = status.text
            if "#atas" in tweet.lower():
                # Define variables
                tweet_id = status.id
                op_handle = status.user.screen_name
                full_name = status.user.name
                op_url = f"https://twitter.com/{op_handle}/status/{tweet_id}"
                message = f'``` Handle: {op_handle},\n Name: {full_name},\n URL: {op_url},\n\n Question: {tweet}```'
                second_message = f'({tweet_id}) [bme] '


                # Log tweet in database
                LogTweet(tweet_id, op_handle, full_name, op_url)

                # Post to Discord
                load_dotenv()
                url = os.getenv('ASSIGN_MENTOR_URL')
                PostToDiscord(message, url, second_message)

                # Send OP a message
                time.sleep(10)
                api.update_status(f'@{op_handle} Hang tight! We are fetching you some mentors.'
                                  f' Expect an answer within 24 hours. :)', tweet_id)


try:
    listener = StdOutListener()
    stream = Stream(auth, listener)
    tweets = stream.filter(track=['toscientists'])

except Exception as e:
    error = traceback.format_exc()
    discord_url = os.getenv('EXCEPTIONS_URL')
    message = f'**There has been an error in the ToScientists tweet stream. See details below:**\n\n```py\n{error}```'
    PostToDiscord(message=message, url=discord_url)
finally:
    cursor.close()
    mydb.close()
