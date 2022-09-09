def AssignmentText(assignment, handles):

    text = {

        'success_1': f'```Woo! You have successfully assigned {handles[1]}, who is an expert in {assignment}.'
                     f' Bear in mind, this is our only expert in {assignment}, so maybe think twice'
                     f' about assigning him again soon!\n\nIf you think you have made a mistake,' 
                     f' please react to this message within 30 seconds!```',
        'success_2': f'```Woo! You have successfully assigned {handles[1]} and {handles[2]} to the '
                     f'question. They are experts in {assignment}.\n\nIf you think this is a mistake, '
                     f'please react to this message within 30 seconds```'
    }
    return text

def LongText():
    text = {
        'error_id': "```There doesn't seem to be a Tweet ID matching the one you just sent me,"
                           " are you sure you have entered the correct ID?```\n\n",
        'error_major': f"```Unfortunately, the major you typed in does not currently exist on our database."
                       f" Are you sure you typed it in correctly?\n\n To view all of our current majors, "
                       f"please use the command .showallmajors in the #database channel.```",
        'abort': '```Your assignment has been aborted, mentors have been unassigned.```',
        'no_abort': '```You have not aborted the assignment. Mentors have been messages```',
        'error': '```There has been an error. See details below\n\n',
        'error_appending': f'```There has been an issue appending the mentors to the assigned_mentors'
                           f' table. Please review error log on #errors```',
        'assignment_success': '```Success logging to database and message sent to mentor```',
        'error_message': '```There has been an error while sending the message to the mentors.'
                         ' Please look at the #exceptions channel for more info```'
    }
    return text

def ExceptionMessages():

    text = {
        'single_mentor_unavailable': '```The mentor you tried to assign is currently not available```',
        'all_mentors_unavailable': '```There does not seem to be any mentors with this expertise available.```',
        'incorrect_assignment': '```You can only assign using either (foo), [baz] or %bar%, please try again```'



    }
