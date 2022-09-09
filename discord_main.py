from discord.ext import commands
from sql_functions import *
from discord_functions import *
from text import *
from ATAS_MessageBot import *
import traceback
from exceptions import *
import pdb

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
text = LongText()  # Long texts for discord
client = commands.Bot(command_prefix='.')  # Tells us which prefix to use when calling bot

@client.event
async def on_reaction_add(reaction, user):
    await reaction.message.channel.send(reaction)
 

@client.event
async def on_message(message):
    await client.process_commands(message)
    try:
        if str(message.channel) == 'assign-mentor':  # if the message is in the assign-mentors channel
            if client.user.mentioned_in(message):  # Detects mention of @BufferBot
                if message.author.bot is False:  # if user is not a bot, returns False
                    print(message.content)
                    result, discord_tweet_id = CheckID(message=message.content)
                    print(result, discord_tweet_id)
                    if result is None:
                        await message.channel.send(text['error_id'] + discord_tweet_id)
                        raise Exception

                    if result is not None:  # If the ID in the discord message is on the table
                        handles, assignment = AppendMentors(message, tweet_id=discord_tweet_id)  # Appends mentor handles in tuple form to handles
                        handles.append(discord_tweet_id)  # Appends tweet_id as final item on handles
                        handles = RemoveTupleFromHandles(handles)  # Changes the tuple form of the handle into string item on handles
                        print(handles)

                        if len(handles) == 2:  # if major does not exist
                            await message.channel.send(text['error_major'])
                            raise Exception

                        if len(handles) == 3:  # If list only has one mentor
                            assignment_text = AssignmentText(assignment, handles)
                            await message.channel.send(assignment_text['success_1'])
                            abort = None  # So we don't get reference before assignment error
                            try:
                                reaction = await client.wait_for(event='reaction_add', timeout=30)  # Wait for reaction to abort
                                if reaction:  # if user reacts to bot message
                                    abort = True
                                    await message.channel.send(text['assignment_aborted'])
                                    raise AssignmentAbortedError

                            except asyncio.TimeoutError:
                                abort = False

                            if abort is False:
                                success = LogMentorAssignment(handles)  # True if successful, False if not
                                if success is True:  # Mentor assignment is logged properly

                                    MessageOneMentor(handles)  # Correctly messages one mentor
                                    await message.channel.send(text['assignment_success'])
                                else:
                                    raise Exception

                        if len(handles) == 4:  # If list have 2 mentors
                            assignment_text = AssignmentText(assignment, handles)
                            await message.channel.send(assignment_text['success_2'])  # Send success message to channel
                            print('2 mentors')

                            abort = None
                            try:
                                reaction = await client.wait_for(event='reaction_add', timeout=30)  # wait for reaction for 30 seconds
                                if reaction:  # Abort assignment upon reaction
                                    await message.channel.send(text['abort'])
                                    abort = True
                                    print('rxn detect')

                            except asyncio.TimeoutError:  # wait_for timed out without reactions -- assignment imminent
                                abort = False  # Abort not called, continue
                                print('no rxn')

                            if abort is False:
                                print('abort is false')
                                success = LogMentorAssignment(handles)  # True if successfully logged, False if not
                                print(success)
                                if success is True:  # Mentor assignment is logged properly
                                    await message.channel.send(text['assignment_success'])
                                    error_in_message = MessageTwoMentors(handles=handles)
                                    print(error_in_message)
                                    if error_in_message is False:  # Fix
                                        raise Exception
                                else:
                                    raise Exception
        if str(message.channel) == 'mentor-response':
            if client.user.mentioned_in(message):
                print('bufferbot detected')

    except Exception:
        if AllMentorsUnavailable: # ## # # # # # # # # # #
            await message.channel.send('all mentors are unavailable at the moment')
        if AssignmentAbortedError:
            pass
        if SingleMentorUnavailable:
            pass
        if IncorrectAssignment:
            pass
        else:
            channel = client.get_channel(790650142776623174)
            error = traceback.format_exc()
            await channel.send(f'**There has been an error. See details below:**\n\n:```py {error}```')


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(DISCORD_TOKEN)
print('bot is online')
