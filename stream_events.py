from twitivity import Event
from post_to_discord import *
from twitter_functions import *
from database_credentials import *
from twitter_auth import MBTwitterAuth
import time
from sql_functions import LogResponse, AlterActivity

api, auth = MBTwitterAuth()

# # # # Important to note the credentials for the listener bot is separate from the messaging bot. Did this by mistake and havent changed it yet # # # #

cursor, mydb = DatabaseAuth()
load_dotenv()


class StreamEvent(Event):
    CALLBACK_URL: str = "https://dc98f61eb084.ngrok.io/twitter/callback"

    def on_data(self, data: json) -> None:  # On data from Twitter Stream
        event = GetNthKey(dictionary=data, n=1)  # Gets the event type
        if 'direct_message_events' in event:
            sender_id = data[event][0]['message_create']['sender_id']
            user = api.get_user(sender_id).screen_name
            if str(user) != 'ATAS_MessageBot':
                try:
                    metadata = data[f'{event}'][0]['message_create']['message_data']['quick_reply_response']['metadata']
                    metadata_string = str(metadata)
                    response = int(metadata_string[0])
                    tweet_id = metadata_string[1:]
                    #AlterActivity(experts=[user.lower()], activity_options=0)
                    if response == 1:
                        url = os.getenv('MENTOR_RESPONSE_URL')
                        message = f'{str(user)} responded yes to answer the question with ID ' \
                                  f'{tweet_id} <@783741679743795210> '
                        PostToDiscord(message, url)
                        time.sleep(3)
                        LogResponse(response=response, tweet_id=tweet_id)  # UNTESTED #
                        api.send_direct_message(
                            recipient_id=sender_id,
                            text='Thank you for agreeing to answer the question!'
                        )

                    if response == 0:
                        LogResponse(response=response, tweet_id=tweet_id)  # UNTESTED #
                        api.send_direct_message(
                            recipient_id=sender_id,
                            text='Thank you for your reply!'
                        )
                        url = os.getenv('MENTOR_RESPONSE_URL')
                        message = f'{str(user)} responded no to answer the question with ID ' \
                                  f'{tweet_id} <@783741679743795210> '
                        PostToDiscord(message, url)
                except Exception as e: # # # # # # # # # When there is an if/else statement, the code never gets to the else statement # # # # #
                    if KeyError:
                        pass
                    else:
                        error = traceback.format_exc()
                        discord_url = os.getenv('EXCEPTIONS_URL')
                        message = f'**Theres an issue with our Twitter DM stream. See below for details:**\n\n```py\n' \
                                  f'{error}```'
                        PostToDiscord(url=discord_url, message=message)


if __name__ == "__main__":
    stream_event = StreamEvent()
    stream_event.listen()

