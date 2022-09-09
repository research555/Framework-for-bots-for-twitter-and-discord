import asyncio
import random
from collections import deque

def RemoveTupleFromHandles(handles):

    converted_handles = []
    list_to_deque = deque(handles)

    for values in handles:
        popped_item = list_to_deque.popleft()
        if type(popped_item) is tuple:
            tup_to_str = ''.join(popped_item)
            converted_handles.append(tup_to_str)
        else:
            converted_handles.append(popped_item)

    return converted_handles