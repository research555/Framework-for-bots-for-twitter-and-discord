import time
import datetime
from database_credentials import DatabaseAuth
from sql_functions import *
from exceptions import NoReply
from ATAS_MessageBot import MessageOneMentor, MessageTwoMentors, ReassignmentMessage
import random
import traceback
from post_to_discord import PostToDiscord
from dotenv import load_dotenv
import os
import pdb
from twitter_functions import SendSurvey

loop = True
while loop is True:

    load_dotenv()
    cursor, mydb = DatabaseAuth()
    mydb.connect()

    try:
        sql = 'SELECT message_sent, has_responded, expert1, expert2, tweet_id, been_reassigned FROM response_time'
        cursor.execute(sql)
        result = cursor.fetchall()
        for time_details in result:
            message_sent = time_details[0]
            has_responded = time_details[1]
            expert1 = time_details[2]
            expert2 = time_details[3]
            tweet_id = time_details[4]
            been_reassigned = time_details[5]
            old_experts = [expert1, expert2]
            # If they have not responded
            if has_responded == 0:
                print('nobody responded')
                now = datetime.datetime.now()
                time_difference = now - message_sent
                print(time_difference)
                if time_difference > datetime.timedelta(minutes=5):  # if more than 24 hours has passed
                    # For one expert assigned
                    if been_reassigned == 0:  # If the mentor hasn't been notified yet
                        if expert2 is None:  # If only one mentor
                            op_url = GetURL(tweet_id=tweet_id)
                            PostToDiscord(message=f'This question remains unanswered {op_url}\n'
                                                  f'{expert1} is our only expert in this field, so please consider'
                                                  f'answering the question yourself',
                                          url=os.getenv('MENTOR_RESPONSE_URL'),
                                          tweet_id=op_url)
                            UpdateBeenReassigned(tweet_id=tweet_id, been_reassigned=True)
                            SendSurvey([expert1])
                            #AlterActivity(experts=old_experts, activity_options=0)



                        # For two experts assigned
                        if expert2 is not None:
                            major, tweet_url, new_mentor = UpdateFetchReassign(major_of=expert1, tweet_id=tweet_id,
                                                                               not_experts=old_experts)
                            if new_mentor:  # If there are other mentors
                                new_mentor = random.choice(new_mentor)
                                old_handles = [major, expert1, expert2, tweet_id]
                                print(old_handles)
                                new_handles = [major, new_mentor[0], tweet_id]
                                print(new_handles)
                                ReassignmentMessage(handles=old_handles,
                                                    two_experts=True)  # Let the old mentors know theyre getting reassigned
                                MessageOneMentor(handles=new_handles, reassigned=True)  # assign new mentor
                                #LogMentorAssignment(handles=new_handles)  # Logs new mentor on mentors_assigned
                                #LogMessageTime(handles=new_handles, reassigned=True)  # Logs new mentor on response_time
                                UpdateBeenReassigned(tweet_id=tweet_id, been_reassigned=True)
                                #AlterActivity(experts=old_experts, activity_options=0)  # removes expiry date from old mentors
                                AlterActivity(experts=new_handles[1:2], activity_options=1)  # adds expiry daye to new mentor
                                SendSurvey([expert1, expert2])

                            if not new_mentor:  # If there are no other mentors
                                PostToDiscord(message=f'This question remains unanswered {tweet_url}\n'
                                                      f'{expert1} is our only expert in this field, so please consider'
                                                      f'answering the question yourself',
                                              url=os.getenv('MENTOR_RESPONSE_URL'),
                                              tweet_id=tweet_url[0])
                                UpdateBeenReassigned(tweet_id=tweet_id, been_reassigned=True)

                                SendSurvey(handles=old_experts, user=True, tweet_id=tweet_id)

                                #AlterActivity(experts=old_experts, activity_options=0)
                    else:
                        print('all reassigned')
            # If they have responded
            if has_responded == 1:  # Has responded
                if been_reassigned == 0:  # Has not been messaged before
                    now = datetime.datetime.now()
                    time_difference = now - message_sent
                    if time_difference > datetime.timedelta(minutes=5):  # if less than 24 hours has passed
                        responses = FetchResponses(tweet_id=tweet_id)
                        for response in responses:
                            if response[0] == 1:
                                pass
                            if response[0] == 0 and (response[1] == 0 or response[1] is None):  # if expert 1 said no and expert 2 either said no or didnt reply
                                if expert2 is not None:  # If two experts assigned and neither said yes
                                    major, tweet_url, new_mentor_tup = UpdateFetchReassign(major_of=expert1,
                                                                                           tweet_id=tweet_id,
                                                                                           not_experts=old_experts)
                                    if new_mentor_tup:  # if another mentor is available
                                        new_mentor = random.choice(new_mentor_tup)
                                        old_handles = [major, expert1, expert2, tweet_id]
                                        new_handles = [major, new_mentor[0], tweet_id]
                                        PostToDiscord(message=f"We have removed the mentors: {old_experts} "
                                                              f"assigned to the tweet {tweet_url} with the new expert:"
                                                              f" {new_mentor} because they did not interact with our"
                                                              f" message within 24 hours",
                                                      url=os.getenv('REASSIGNMENT_URL'))
                                        MessageOneMentor(handles=new_handles, reassigned=True, old_mentors=old_experts)  # assign new mentor
                                        #AlterActivity(experts=old_experts, activity_options=0)  # removes expiry from old experts


                                    if not new_mentor_tup:  # if another mentor is not available
                                        PostToDiscord(message=f'This question remains unanswered {tweet_url}\n'
                                                              f' {expert1} is our only expert in this field, so please consider'
                                                              f' answering the question yourself',
                                                      url=os.getenv('MENTOR_RESPONSE_URL'),
                                                      tweet_id=tweet_url)
                                        UpdateBeenReassigned(tweet_id=tweet_id, been_reassigned=True)
                                        #AlterActivity(experts=old_experts, activity_options=0)
                                        break

                                if expert2 is None:  # If no expert 2

                                    tweet_url = GetURL(tweet_id=tweet_id)
                                    PostToDiscord(message=f'This question remains unanswered {tweet_url}\n'
                                                          f'{expert1} is our only expert in this field, so please consider'
                                                          f' answering the question yourself',
                                                  url=os.getenv('MENTOR_RESPONSE_URL'),
                                                  tweet_id=tweet_url)
                                    UpdateBeenReassigned(tweet_id=tweet_id, been_reassigned=True)

                                    raise NoReply
                                    #AlterActivity(experts=old_experts, activity_options=0)

        time.sleep(5) #Run every 5 minutes?

    except Exception:
        if NoReply:
            pass
        print('exception encountered')
        error = traceback.format_exc()
        discord_url = os.getenv('EXCEPTIONS_URL')
        message = f'**There has been an exception in the time check implementation. See below:**\n\n ```py\n{error}```'
        PostToDiscord(message=message, url=discord_url)

    finally:
        cursor.close()
        mydb.close()
