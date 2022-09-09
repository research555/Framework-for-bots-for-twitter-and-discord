# # # # Gets n-th Value In Dictionary # # # #

def GetNthKey(dictionary, n=0):

    if n < 0:
        n += len(dictionary)
    for i, key in enumerate(dictionary.keys()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")

def SendSurvey(handles, user=False, tweet_id=None):
    from twitter_auth import MBTwitterAuth
 # # # # get tweet then user then send them a survei via dm too # # #
    api, auth = MBTwitterAuth()
    survey_link = "shorturl.at/avxF3"
    try:
        if user == True:
            user_id = api.get_status(id=tweet_id).user.id_str
            api.send_direct_message(recipient_id=user_id, text='Please fill out this survey USER ' + survey_link)

        for handle in handles:
            mentor_id = api.get_user(screen_name=handle)
            api.send_direct_message(recipient_id=mentor_id.id_str, text="Please answer this survey MENTOR " + survey_link)

    except Exception:
        return False
