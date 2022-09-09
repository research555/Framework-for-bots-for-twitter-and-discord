# # # # Now, wheenever they are messaged, it will make active 1, consider making own check time file for this



# # # #  Messages one mentor # # # #

def MessageOneMentor(handles, reassigned=None, old_mentors=None):
    import traceback
    from post_to_discord import PostToDiscord
    import os
    from dotenv import load_dotenv
    from database_credentials import DatabaseAuth
    from twitter_auth import MBTwitterAuth
    from sql_functions import LogMessageTime, GetURL, AlterActivity, UpdateBeenReassigned, LogReassignment

    api, auth = MBTwitterAuth()
    load_dotenv()

    try:
        ticket = handles[2]  # Tweet ID
        tweet_url = GetURL(tweet_id=ticket)
        text = f'We have received a question we believe you would be perfect to answer. Please use one of the quick' \
               f' replies you see on the bottom of this chat box to mark your intention to respond. If you do not mark' \
               f' your intention to respond within 24 hours, it will automatically assign a response of "No" From you.\n' \
               f'The question can be found below:\n\n {tweet_url}\n\n' \
               f'Please do not write us a message here as it would cause your quick replies to disappear. For all' \
               f' enquiries please send us a DM on @ToScientists or visit our website.'
        reply_options = [
            {
                "label": "Yes",
                "description": "Click here if you intend on replying within 24 hours",
                "metadata": f"1{ticket}"
            },
            {
                "label": "No",
                "description": "Click here if you don't intend on replying within 24 hours",
                "metadata": f"0{ticket}"
            }
        ]

        mentor_id_1 = api.get_user(screen_name=handles[1]).id
        expert = [handles[1]]
        api.send_direct_message(mentor_id_1, text, quick_reply_type='options', quick_reply_options=reply_options)
        message = f'Waiting for response for tweet URL: {tweet_url}'
        url = os.getenv('WAIT_FOR_RESPONSE_URL')
        PostToDiscord(message=message, url=url)
        if reassigned is None:
            LogMessageTime(handles=handles)  # Log it on response_time
        else:
            #success = LogMessageTime(handles=handles, reassigned=True)  # Log it on response_time
            LogReassignment(handles=handles)  # Log new mentor & tweet_id on reassignment
            UpdateBeenReassigned(tweet_id=ticket, been_reassigned=True)  # updates been_reassigned to True
            #AlterActivity(experts=old_mentors, activity_options=0)  # sets currently_active to False and removes expiry from old mentors

        AlterActivity(experts=expert, activity_options=1)  # sets currently_active to True and adds expiry to new mentor

    except Exception as e:
        print(e)
        error = traceback.format_exc()
        url = os.getenv('EXCEPTIONS_URL')
        message = f'**There has been an exception messaging one mentor. See below for details:**\n\n```py\n{error}```'
        PostToDiscord(url=url, message=message)


# # # # Message Two Mentors # # # #

def MessageTwoMentors(handles):
    import traceback
    from dotenv import load_dotenv
    from sql_functions import LogMessageID, LogMessageTime, GetURL, AlterActivity
    from twitter_auth import MBTwitterAuth
    from post_to_discord import PostToDiscord
    import os
    import sys

    api, auth = MBTwitterAuth()
    load_dotenv()
    experts = list(handles[1:3])

    try:
        ticket = handles[3]  # Tweet ID
        tweet_url = GetURL(tweet_id=ticket)
        text = f'We have received a question we believe you would be perfect to answer. Please use one of the quick' \
               f'replies you see on the bottom of this chat box to mark your intention to respond. If you do not mark' \
               f'your intention to respond within 24 hours, it will automatically assign a response of "No" From you.\n' \
               f'The question can be found below:\n\n {tweet_url}\n\n' \
               f'Please do not write us a message here as it would cause your quick replies to disappear. For all' \
               f'enquiries please send us a DM on @ToScientists or visit our website.'
        reply_options = [
            {
                "label": "Yes",
                "description": "Click here if you intend on replying within 24 hours",
                "metadata": f"1{ticket}"
            },
            {
                "label": "No",
                "description": "Click here if you don't intend on replying within 24 hours",
                "metadata": f"0{ticket}"
            }
        ]

        mentor_id_1 = api.get_user(screen_name=handles[1]).id
        mentor_id_2 = api.get_user(screen_name=handles[2]).id

        api.send_direct_message(mentor_id_1, text, quick_reply_type='options', quick_reply_options=reply_options)
        api.send_direct_message(mentor_id_2, text, quick_reply_type='options', quick_reply_options=reply_options)

        message = f'Waiting for response for tweet URL: {tweet_url}'
        discord_url = os.getenv('WAIT_FOR_RESPONSE_URL')
        PostToDiscord(message=message, url=discord_url)
        success = LogMessageTime(handles=handles)
        AlterActivity(experts=experts, activity_options=1)

        return success

    except Exception as e:
        error = traceback.format_exc()
        url = os.getenv('EXCEPTIONS_URL')
        message = f'**There has been an exception messaging two mentor. See below for details:**\n\n```py\n{error}```'
        PostToDiscord(url=url, message=message)
        return False


# # # # Send Reassignment message to mentors who did not respond # # # #

def ReassignmentMessage(handles, two_experts=None):

    from twitter_auth import MBTwitterAuth
    from post_to_discord import PostToDiscord
    import os
    from dotenv import load_dotenv
    import traceback

    load_dotenv()
    api, auth = MBTwitterAuth()

    try:
        no_reply_text = "Hi again!\n\n We try to aim for our questions to be answered within a 24 hour time period " \
                        "and since you haven't interacted with the previous message we have chosen to send the question" \
                        " to other mentors on our network. You can of course still respond to the question by clicking" \
                        " on the message link on our previous message to you"
        if two_experts is None:
            mentor_id_1 = api.get_user(screen_name=handles[1]).id
            api.send_direct_message(recipient_id=mentor_id_1, text=no_reply_text)
            message = f'We have reassigned all mentors assigned tweet ID: {handles[2]}'
            url = os.getenv('REASSIGNMENT_URL')
            PostToDiscord(message=message, url=url)
            return True

        if two_experts is not None:
            mentor_id_1 = api.get_user(screen_name=handles[1]).id
            mentor_id_2 = api.get_user(screen_name=handles[2]).id
            api.send_direct_message(recipient_id=mentor_id_1, text=no_reply_text)
            api.send_direct_message(recipient_id=mentor_id_2, text=no_reply_text)
            message = f'Reassigned tweet ID {handles[3]}'
            url = os.getenv('REASSIGNMENT_URL')
            PostToDiscord(message=message, url=url)
            return True

    except Exception:
        error = traceback.format_exc()
        url = os.getenv('EXCEPTIONS_URL')
        message = f'There has been an exception sending the reassigment message. ' \
                  f'See below for details:\n\n```py\n{error}```'
        PostToDiscord(url=url, message=message)
        return False
