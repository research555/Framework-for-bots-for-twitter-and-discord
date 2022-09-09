import datetime
import os
from dotenv import load_dotenv
from sql_functions import *
from database_credentials import *
from post_to_discord import PostToDiscord
import traceback
import time
import pdb


# # # # This can now set currently_active & expires to null if over expiry date # # # #
# # # # Is this still necessary? # # # #
# # # # YES, to remove the reassignmed mentors after 24h
"""
WHERE TO INSERT:

when they are assigned DONE
when they are messaged DONE
when they are reassigned DONE
when they respond to q DONE
"""

x = True
while x is True:

    load_dotenv()
    cursor, mydb = DatabaseAuth()

    try:
        now = datetime.datetime.now()# + datetime.timedelta(minutes=10)
        sql = 'SELECT expires FROM lists'
        cursor.execute(sql)
        result = cursor.fetchall()
        for tuples in result:
            for expiry_date in tuples:
                if expiry_date:
                    if expiry_date <= now: # Expiry passed, remove activity
                        sql = 'UPDATE lists SET currently_active = 0, expires = NULL WHERE expires = %s'
                        cursor.execute(sql,(expiry_date,))
                        mydb.commit()
        time.sleep(10)



    except Exception as e:
        error = traceback.format_exc()
        discord_url = os.getenv('EXCEPTIONS_URL')
        message = f'**There has been an error altering the activity of active mentors. See below for details:**\n\n' \
                  f'```py\n {error}```'
        PostToDiscord(url=discord_url, message=message)
        time.sleep(10)
    finally:
        cursor.close()
        mydb.close()
