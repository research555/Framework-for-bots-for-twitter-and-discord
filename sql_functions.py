from database_credentials import *
import re

#cursor, mydb = DatabaseAuth()


# # # # Check If ID Is In Database And Update If Not # # # #

def LogTweet(tweet_id, op_handle, full_name, op_url):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    # # # # For tweets table # # # #

    sql = "SELECT tweet_id FROM tweets WHERE tweet_id = (%s)"
    cursor.execute(sql, (tweet_id,)) # Checks if tweet is already logged in tweets table
    result = cursor.fetchall()

    if not result: # If tweet is not already logged, insert it
        sql = "INSERT INTO tweets (tweet_id, handle, full_name, URL) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (tweet_id, op_handle, full_name, op_url,))
        mydb.commit()


    # # # # For assigned_mentors table # # # #

    sql = "SELECT tweet_id FROM mentors_assigned WHERE tweet_id = (%s)"
    cursor.execute(sql, (tweet_id,))  # Checks if tweet is already logged in assigned_mentors table
    result = cursor.fetchall()

    if not result:  # If tweet is not already logged, insert it
        sql = "INSERT INTO mentors_assigned (tweet_id) VALUES (%s)"
        cursor.execute(sql, (tweet_id,))
        mydb.commit()

    cursor.close()
    mydb.close()


    return tweet_id

# # # # Checks that the tweetID that was assigned on discord

def CheckID(message):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    discord_tweet_id = re.search(r"\(([A-Za-z0-9_]+)\)", message).group(1)  # finds substring within parentheses ()
    sql = "SELECT tweet_id FROM tweets WHERE tweet_id = (%s)"
    cursor.execute(sql, (discord_tweet_id,))  # Checks if substring already in tweets table
    result = cursor.fetchone()  # If tweet ID not in tweets table returns None
    cursor.close()
    mydb.close()

    return result, discord_tweet_id

# # # # Checks the major that was assigned on Discord and returns the handles of someone attached to that major # # # #

def AppendMentors(message, tweet_id):   # Why message.content in function?? FINISH
    from post_to_discord import PostToDiscord
    from exceptions import AllMentorsUnavailable, SingleMentorUnavailable, IncorrectAssignment
    from dotenv import load_dotenv
    import os
    from text import ExceptionMessages
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    try:
        if '{' in message.content:
            assignment = re.search(r"\{(.*?)\}", message.content).group(1)
            sql = "SELECT currently_active FROM lists WHERE handle = %s"
            cursor.execute(sql, (assignment,))
            query = cursor.fetchone()
            for activity in query:
                if activity == 0:
                    sql = "UPDATE mentors_assigned SET expert1 = %s WHERE tweet_id = %s"
                    cursor.execute(sql, (assignment, tweet_id,))
                    handles = [None, assignment]
                elif activity == 1:
                    raise SingleMentorUnavailable

        elif '[' in message.content:
            assignment = re.search(r"\[(.*?)\]", message.content).group(1)  # Finds substring within square brackets []
            sql = "SELECT handle FROM lists WHERE major = (%s) AND currently_active = 0 ORDER BY rand() LIMIT 2"  # this line ensures we only get a max of two mentors every time
            cursor.execute(sql, (assignment,))
            result = cursor.fetchall()
            handles = [assignment] # Ensures major is always on index 0
            for handle in result:
                handles.append(handle)
            if len(handles) == 1:
                raise AllMentorsUnavailable

        elif '%' in message.content:
            print('this is for general career advice %career% ')
            assignment = re.search(r"%(.*?)%", message).group(1)


        else:
            raise IncorrectAssignment
    except Exception:
        text = ExceptionMessages()
        load_dotenv()
        url = os.getenv('ASSIGN_MENTOR_URL')
        if SingleMentorUnavailable:
            PostToDiscord(message=text['single_mentor_unavailable'], url=url)
        if AllMentorsUnavailable:
            PostToDiscord(message=text['all_mentors_unavailable'], url=url)
        if IncorrectAssignment:
            PostToDiscord(message=text['incorrect_assignment'], url=url)
        else:
            pass
    finally:
        cursor.close()
        mydb.close()

    return handles, assignment

# # # # Check if mentors are already assigned, if not return False # # # # UNUSED

def AreMentorsAssigned():
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    cursor.execute("SELECT mentors_assigned FROM mentors_assigned WHERE tweet_id = (%s)")
    is_assigned = cursor.fetchone()

    if is_assigned is None:  # No tweet_id results in None type
        error = 'Tweet ID does not exist on mentors_assigned table'

    elif is_assigned[0] is not None:  # Mentors already assigned
        error = 'Mentors have already been assigned to this tweet ID'
    else:  ## make except statement
        error = False

    cursor.close()
    mydb.close()

    return error

# # # # Logs mentors assigned via Discord into mentors_assigned table # # # #

def LogMentorAssignment(handles):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    if len(handles) == 4: # Tweet_id, major and 2 experts
        sql = "UPDATE mentors_assigned SET major = %s, expert1 = %s, expert2 = %s WHERE tweet_id = %s"
        cursor.execute(sql, (handles[0], handles[1], handles[2], handles[3],))
        success = True

    elif len(handles) == 3: # Tweet_id, major and 1 expert
        sql = "UPDATE mentors_assigned SET major = %s, expert1 = %s WHERE tweet_id = %s"
        cursor.execute(sql, (handles[0], handles[1], handles[2],))
        mydb.commit()
        success = True

    else:
        success = False

    cursor.close()
    mydb.close()

    return success

# # # # Logs message ID when messaging mentors into mentors_assigned # # # #

def LogMessageID(handles, message_ids):
    import traceback
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    try:
        if len(handles) == 4: # major and 2 experts and tweet_id
            sql = "UPDATE mentors_assigned SET message_id_1 = %s, message_id_2 = %s WHERE tweet_id = %s"
            cursor.execute(sql, (message_ids[0], message_ids[1], handles[3],))
            mydb.commit()
            success = True

        elif len(handles) == 3: # major and 1 expert and tweet_id
            sql = "UPDATE mentors_assigned SET message_id_1 = %s WHERE tweet_id = %s"
            cursor.execute(sql, (message_ids[0], handles[2],))
            mydb.commit()
            success = True
    except Exception as e:
        return e

    finally:
        cursor.close()
        mydb.close()

# # # # Logs the mentors into response_time after messaging # # # #

def LogMessageTime(handles, reassigned=None):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    if reassigned is None:
        if len(handles) == 4:
            sql = "INSERT INTO response_time (tweet_id, expert1, expert2) VALUES (%s, %s, %s)"
            cursor.execute(sql, (handles[3], handles[2], handles[1],))
            mydb.commit()
            success = True
        elif len(handles) == 3:
            sql = "INSERT INTO response_time (tweet_id, expert1) VALUES (%s, %s)"
            cursor.execute(sql, (handles[2], handles[1],))
            mydb.commit()
            success = True
        else:
            success = False

        return success

    # # # # UNTESTED # # # #

    if reassigned is not None:  ## need fix?
        if len(handles) == 4:
            sql = "UPDATE response_time SET expert1 = %s, expert2 = %s WHERE tweet_id = %s"
            cursor.execute(sql, (handles[1], handles[2], handles[3]))
            mydb.commit()
            success = True
        elif len(handles) == 3:
            sql = "UPDATE response_time SET expert1 = %s WHERE tweet_id = %s"
            cursor.execute(sql, (handles[1], handles[2]))
            mydb.commit()
            success = True
        else:
            success = False
        return success

    cursor.close()
    mydb.close()

# # # # Searches for str within { } in Discord to assign individual mentor # # # #

def AssignNewMentor(message, tweet_id):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    mentor = re.search(r"{([A-Za-z0-9_]+)}", message.content).group(1)
    sql = "SELECT handle FROM lists WHERE handle = %s"
    cursor.execute(sql, (mentor,))
    sql = "UPDATE mentors_assigned SET expert1 = %s WHERE tweet_id = %s"
    cursor.execute(sql, (mentor, tweet_id,))

    cursor.close()
    mydb.close()


    # # # # FINISH # # # #

# # # # Logs response from the mentors quick replies into response_time # # # #

def LogResponse(response, tweet_id):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    sql = "SELECT response, been_reassigned FROM response_time WHERE tweet_id = %s"
    cursor.execute(sql, (tweet_id,))
    result = list(cursor.fetchone())
    response_db = result[0]
    been_reassigned = result[1]

    if been_reassigned == 0:
        if response_db is None:  # If this is the first instance of responding
            sql = "UPDATE response_time SET response = %s, has_responded = True WHERE tweet_id = %s"
            cursor.execute(sql, (response, tweet_id,))
            mydb.commit()
            cursor.close()
            mydb.close()

        elif result[0] is not None:  # Makes sure that two responses are added separately
            sql = "UPDATE response_time SET response_2 = %s WHERE tweet_id = %s"
            cursor.execute(sql, (response, tweet_id,))
            mydb.commit()
            cursor.close()
            mydb.close()

    elif been_reassigned == 1:
        sql = "UPDATE reassignment SET response = %s WHERE tweet_id = %s"
        cursor.execute(sql, (response, tweet_id,))
        mydb.commit()
        cursor.close()
        mydb.close()


# # # # Updates the been_reassigned column in response_time # # # #

def UpdateBeenReassigned(tweet_id, been_reassigned):
    from database_credentials import DatabaseAuth

    cursor, mydb = DatabaseAuth()

    sql = "UPDATE response_time SET been_reassigned = %s WHERE tweet_id = %s"
    cursor.execute(sql, (been_reassigned, tweet_id,))
    mydb.commit()
    cursor.close()
    mydb.close()

# # # # Finds new mentor and updates response_time accordingly # # # #

def UpdateFetchReassign(major_of, tweet_id, not_experts):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    # Find URL
    sql = "SELECT URL FROM tweets WHERE tweet_id = %s"
    cursor.execute(sql, (tweet_id,))
    tweet_url_tup = cursor.fetchone()
    tweet_url = tweet_url_tup[0]

    # update tables
    #sql = "UPDATE response_time SET expert1 = NULL, expert2 = NULL WHERE tweet_id = %s"
    #cursor.execute(sql, (tweet_id,))  # url_for is tweet_id
    #mydb.commit()

    # find major
    sql = "SELECT major FROM lists WHERE handle = %s"
    cursor.execute(sql, (major_of,))  # major_of is handle
    major_tup = cursor.fetchone()
    major = major_tup[0]

    # reassign
    sql = "SELECT handle FROM lists WHERE major = %s AND NOT (handle = %s OR handle = %s OR currently_active = 1)"
    cursor.execute(sql, (major, not_experts[0], not_experts[1],))
    new_mentor = cursor.fetchall()
    cursor.close()
    mydb.close()

    return major, tweet_url, new_mentor

# # # # returns respondes from the mentors # # # #

def FetchResponses(tweet_id):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    sql = "SELECT response, response_2 FROM response_time WHERE tweet_id = %s"
    cursor.execute(sql, (tweet_id,))
    responses = cursor.fetchall()
    cursor.close()
    mydb.close()

    return responses

# # # # Gets the URL through a tweet_id # # # #

def GetURL(tweet_id):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    sql = "SELECT URL FROM tweets WHERE tweet_id = %s"
    cursor.execute(sql, (tweet_id,))
    op_url = cursor.fetchone()
    cursor.close()
    mydb.close()

    return op_url[0]

# # # # Removes a mentor from the mentors_assigned table # # # #

def RemoveFromDatabase(tweet_id):  # whats the point of this
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    sql = "UPDATE mentors_assigned SET major = NULL, expert1 = NULL, expert2 = NULL, mentors_assigned = NULL WHERE tweet_id = %s"
    cursor.execute(sql, (tweet_id,))
    row_count = cursor.rowcount()
    cursor.close()
    mydb.close()
    return row_count

# # # # Change currently_active # # # #

def AlterActivity(experts, activity_options):
    import datetime
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    for expert in experts:
        if None:
            pass
        elif activity_options == 1:
            onedayfromnow = datetime.datetime.now() + datetime.timedelta(minutes=10)
            sql = 'UPDATE lists SET expires = %s, currently_active = 1 WHERE handle = %s'
            cursor.execute(sql, (onedayfromnow, expert,))
            mydb.commit()

        elif activity_options == 0:
            sql = 'UPDATE lists SET expires = NULL, currently_active = 0 WHERE handle = %s'
            cursor.execute(sql, (expert,))
            mydb.commit()
    cursor.close()
    mydb.close()

def LogReassignment(handles):
    from database_credentials import DatabaseAuth
    cursor, mydb = DatabaseAuth()

    # Insert before update so the message_sent column
    sql = "INSERT INTO reassignment(tweet_id, mentor) VALUES(%s, %s)"
    cursor.execute(sql, (handles[2], handles[1],))
    mydb.commit()
    cursor.close()
    mydb.close()


