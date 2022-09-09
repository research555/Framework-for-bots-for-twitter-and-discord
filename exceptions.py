class AssignmentAbortedError(Exception):  # Created this exception so it doesnt send traceback to server upon abort
    pass
class NotDMEvent(Exception):
    pass
class NotMessageCreate(Exception):
    pass
class AllMentorsUnavailable(Exception):
    pass
class SingleMentorUnavailable(Exception):
    pass
class IncorrectAssignment(Exception):
    pass
class NoReply(Exception):
    pass