# I forgot why this code exists.

#handles = ['bme', 'inooraddin', 'atas_messagebot', 1346204132994994176]


def CreateMessage(handles):

    if len(handles) == 3: # If only one mentor is available for assignment
        mentor_1 = handles[1]
        tweet_id = handles[2]
        cursor.execute("SELECT * FROM tweets WHERE tweet_id = (%s)", (tweet_id,))
        question_asker = cursor.fetchone()
        question_asker = question_asker[2]

        message_mentor = f"Hi {mentor_1}!\n\n" \
                         f"We think you might be interested in answering a question submitted to us by {question_asker} " \
                         f"You can find the question on the link below:\n\n" \
                         f"https://twitter.com/{question_asker}/status/{tweet_id}"

        return [message_mentor]


    if len(handles) == 4: # If two mentors assigned

        mentor_1 = handles[1]
        mentor_2 = handles[2]
        tweet_id = handles[3]

        cursor.execute("SELECT * FROM tweets WHERE tweet_id = (%s)", (tweet_id,)) # Finds the handle of who asked the question
        question_asker = cursor.fetchall()
        question_asker = question_asker[0][2]


        message_mentor_1 = f"Hi {mentor_1}!\n\n" \
                           f"We think you might be interested in answering a question submitted to us by {question_asker} " \
                           f"You can find the question on the link below:\n\n" \
                           f"https://twitter.com/{question_asker}/status/{tweet_id}"

        message_mentor_2 = f"Hi {mentor_2}!\n\n" \
                           f"We think you might be interested in answering a question submitted to us by {question_asker} " \
                           f"You can find the question on the link below:\n\n" \
                           f"https://twitter.com/{question_asker}/status/{tweet_id}\n\n\n"

        return [message_mentor_1, message_mentor_2]




