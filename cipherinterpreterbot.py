#Discord bot for running ComplexCipher (and other random stuff).

import discord
from discord.ext import commands
import complexcipher2
import logging
import time
import os
import io
import random
import pickle

logging.basicConfig(format = '%(levelname)s:%(name)s:(%(asctime)s): %(message)s',
                    datefmt = '%d-%b-%y %H:%M:%S',
                    level = logging.INFO)

################################################################################
#Initialization start

bot = commands.Bot('~')
token = '' #Manually add token here.
dicts = {}
guilds = {}
channels = {}
maintenance = False
bot.remove_command('help')

if token == '': #Get token if it's not already in the code.
    try:
        file = open('token.txt')
        token = file.read()
        file.close()
        logging.info("Token acquired from file.")
    except FileNotFoundError:
        logging.warning("Token file not found.")
        try:
            token = os.environ['CIB_TOKEN']
            logging.info("Token acquired from environment variable.")
        except KeyError:
            logging.warning("Token environment variable not found.")
            logging.error("Token auto detection failed. Stopping execution.")
            input("Press enter to quit.")
            quit()
else:
    logging.info("Token acquired from code.")

with open('config.txt') as file: #Load stored items into memory.
    for line in file:
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        line = line.split('=', maxsplit = 1)
        try:
            if section == 'DICTIONARIES':
                id = int(line[0].strip())
                dict = line[1].strip()
                dicts[id] = dict
            if section == 'GUILDS':
                name = line[0].strip()
                id = int(line[1].split('"')[1])
                guilds[id] = name
            if section == 'CHANNELS':
                name = line[0].strip()
                id = int(line[1].split('"')[1])
                channels[name] = id
        except (IndexError, ValueError):
            continue
logging.info("Guilds, channels, and dictionaries initialized.")

logged = [int(guild) for guild in os.listdir('logs_active')]
logging.info("Logging messages in {0} guilds".format(len(logged)))

#Initialization end
################################################################################
#Helper functions start

def decode_log(log):
    entries = []
    cache = {}

    for entry in log:
        items = []

        if entry['version'] == 1:
            if entry['channel_id'] not in cache:
                cache[entry['channel_id']] = bot.get_channel(entry['channel_id'])

            if entry['author_id'] not in cache:
                cache[entry['author_id']] = bot.get_user(entry['author_id'])

            if cache[entry['channel_id']] is None:
                entry_channel_name = '#' + entry['channel_name'] + 'as seen'
            else:
                entry_channel_name = '#' + cache[entry['channel_id']].name

            if cache[entry['author_id']] is None:
                entry_author_name = entry['author_name'] + 'as seen'
            else:
                entry_author_name = cache[entry['author_id']].name

            items.append(str(entry['timestamp']))
            items.append(str(entry['message_id']))
            items.append(entry_channel_name)
            items.append(entry_author_name)
            items.append(entry['content'])

        else:
            raise NotImplementedError('Invalid entry version {0}'.format(entry['version']))

        entries.append(items)

    return entries

#Helper functions end
################################################################################
#Commands start

@bot.command() #Command to display help.
async def help(ctx):
    buffer = '''```
    CIPHER FUNCTIONS
    ~e <text>                                                                   - Encode text
    ~d <text>                                                                   - Decode text

    SUGGESTION FUNCTIONS
    ~suggest <text>                                                             - Add suggestion to list
    ~suggestions <function> <*parameters>
        view                                                                    - View current suggestions
        clear                                                                   - Clear all current suggestions
        remove <X, Y, Z,...>                                                    - Remove suggestions tagged X, Y, Z,...
    ```'''
    await ctx.send(buffer)
    logging.info("Displayed help for {0}.".format(ctx.message.author))

@bot.command() #Command to change operating channel for cipher functions.
async def setchannel(ctx):
    try:
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
    except IndexError:
        content = 'current'
    buffer = ''
    writeG = False
    writeC = False
    if content == 'current':
        guilds[ctx.message.guild.id] = ctx.message.guild
        channels[ctx.message.guild] = ctx.message.channel.id
        with open('config.txt', 'r') as file:
            overwrite = False
            for line in file:
                if line.split('=', maxsplit = 1)[0].strip() == ctx.message.guild.name:
                    overwrite = True
        with open('config.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    section = line[1:-1]
                    if section == 'GUILDS' and overwrite == False:
                        writeG = True
                    elif section == 'CHANNELS' and overwrite == False:
                        writeC = True
                if line.split('=', maxsplit = 1)[0].strip() == ctx.message.guild.name and section == 'GUILDS':
                    buffer += '{0} = "{1}"\n'.format(ctx.message.guild.name, ctx.message.guild.id)
                    continue
                elif line.split('=', maxsplit = 1)[0].strip() == ctx.message.guild.name and section == 'CHANNELS':
                    buffer += '{0} = "{1}" #{2}\n'.format(ctx.message.guild.name, ctx.message.channel.id, ctx.message.channel.name)
                    continue
                buffer += line + '\n'
                if writeG:
                    buffer += '{0} = "{1}"\n'.format(ctx.message.guild.name, ctx.message.guild.id)
                    writeG = False
                elif writeC:
                    buffer += '{0} = "{1}" #{2}\n'.format(ctx.message.guild.name, ctx.message.channel.id, ctx.message.channel.name)
                    writeC = False
        with open('config.txt', 'w') as file:
            file.write(buffer)
        logging.info("Channel added - Guild: {0}; Channel: #{1}.".format(ctx.message.guild, ctx.message.channel))
        await ctx.send('Set channel #{0} as output channel.'.format(ctx.message.channel))
        return

@bot.command() #Command to encode text.
async def e(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
        logging.info("Processing encode request from {0}.".format(ctx.message.author))
        msg = '{0} {1.message.author.mention} asked to encode `{2}` in #{1.message.channel}.'.format(msgtime, ctx, content)
        try:
            dict = dicts[ctx.message.author.id]
        except KeyError:
            dict = None
            msg += '\nWARNING: No dictionary is linked to this account. Using standard dictionary.'
        try:
            msg += '\n```{0}```'.format(complexcipher2.encode(content, dict))
        except:
            await ctx.send('An internal error occurred. You may have used an unsupported character.')
            return
        await dest_channel.send(msg)
        return
    except IndexError:
        await ctx.send('Invalid syntax. Usage: ~e <text>')
        return

@bot.command() #Command to decode text.
async def d(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
        logging.info("Processing decode request from {0}.".format(ctx.message.author))
        msg = '{0} {1.message.author.mention} asked to decode `{2}` in #{1.message.channel}.'.format(msgtime, ctx, content)
        try:
            dict = dicts[ctx.message.author.id]
        except KeyError:
            dict = None
            msg += '\nWARNING: No dictionary is linked to this account. Using standard dictionary.'
        try:
            msg += '\n```{0}```'.format(complexcipher2.decode(content, dict))
        except:
            await ctx.send('An internal error occurred. The cipher may be corrupted or you may not have the correct dictionary.')
            return
        await dest_channel.send(msg)
        return
    except IndexError:
        await ctx.send('Invalid syntax. Usage: ~d <text>')
        return

@bot.command()
async def key(ctx):
    try:
        content = ctx.message.content.split(' ', maxsplit = 2)
        logging.info("Processing dict change request from {0}.".format(ctx.message.author))
        write_new_dict = False

        if content[1] == 'generate':
            new_dict = complexcipher2.generate_dictionary()
            write_new_dict = True
            msg = 'A new dictionary has been generated and linked to your account.'
            msg += '\nYour dictionary is: `{0}`'.format(new_dict)

        if content[1] == 'link':
            new_dict = content[2]
            if complexcipher2.check_dictionary(new_dict):
                write_new_dict = True
                msg = 'Dictionary was successfully linked to your account.'
            else:
                msg = 'Invalid dictionary. Check for copying errors or generate a new one.'

        if write_new_dict:
            dicts[ctx.message.author.id] = new_dict
            buffer = ''
            with open('config.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                        if section == 'DICTIONARIES':
                            write = True
                            check = True
                        else:
                            check = False
                    if check and line.split('=')[0].strip() == str(ctx.message.author.id):
                        pass
                    else:
                        buffer += line + '\n'
                    if write:
                        buffer += '{0} = {1}\n'.format(ctx.message.author.id, new_dict)
                        write = False
            with open('config.txt', 'w') as file:
                file.write(buffer)
            logging.info("New dict successfully added to file.")

        await ctx.send(msg)
        return
    except IndexError:
        await ctx.send('Invalid syntax. Usage: ~d <text>')
        return

@bot.command() #Command to accept suggestions.
async def suggest(ctx):
    content = ctx.message.content.split(' ', maxsplit = 1)[1]
    buffer = ''
    write = False
    with open('config.txt', 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                if section == 'SUGGESTIONS':
                    write = True
            buffer += line + '\n'
            if write:
                buffer += '{0} = "{1}"\n'.format(ctx.message.guild.id, content)
                write = False
    with open('config.txt', 'w') as file:
        file.write(buffer)
    await ctx.send('Your suggestion has been recorded.')
    logging.info("Suggestion added in {0}.".format(ctx.message.guild))
    return

@bot.command() #Command to manage suggestions.
async def suggestions(ctx):
    try:
        content = ctx.message.content.split(' ', maxsplit = 2)[1]

        if content == 'view': #Subcommand to view existing suggestions for the guild.
            buffer = '```\n'
            seq = 'A'
            with open('config.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                    if section != 'SUGGESTIONS':
                        continue
                    line = line.split('=', maxsplit = 1)
                    if line[0].strip() == str(ctx.message.guild.id):
                        buffer += '{0}: {1}\n'.format(seq, line[1].strip())
                        seq = chr(ord(seq) + 1)
            if buffer == '```\n':
                await ctx.send('No current suggestions. Use ~suggest <text> to add new ones.')
                return
            msg = await ctx.send('Current suggestions:\n' + buffer + '```')
            seq = ord(seq)
            seq_i = 'A'
            while seq > 65:
                emoji = discord.utils.get(bot.emojis, name = 'letter_{0}'.format(seq_i))
                await msg.add_reaction(emoji)
                seq -= 1
                seq_i = chr(ord(seq_i) + 1)
            logging.info("Displayed suggestions in {0}.".format(ctx.message.guild))
            return

        elif content == 'clear': #Subcommand to clear all existing suggestions for the guild.
            buffer = ''
            with open('config.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                    if section == 'SUGGESTIONS' and line.split('=', maxsplit = 1)[0].strip() == str(ctx.message.guild.id):
                        continue
                    buffer += line + '\n'
            with open('config.txt', 'w') as file:
                file.write(buffer)
            await ctx.send('Suggestions cleared.')
            logging.info("Cleared suggestions in {0}.".format(ctx.message.guild))
            return

        elif content == 'remove': #Subcommand to remove specific suggestions for the guild.
            buffer = ''
            r_list = ctx.message.content.split(' ', maxsplit = 2)[2].split(', ')
            seq = 65
            for i in range(0, len(r_list)):
                r_list[i] = ord(r_list[i].upper())
            with open('config.txt', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('[') and line.endswith(']'):
                        section = line[1:-1]
                    if section == 'SUGGESTIONS' and line.split('=', maxsplit = 1)[0].strip() == str(ctx.message.guild.id):
                        if seq in r_list:
                            seq += 1
                            continue
                        seq += 1
                    buffer += line + '\n'
            with open('config.txt', 'w') as file:
                file.write(buffer)
            await ctx.send('Suggestions removed.')
            logging.info("Removed suggestions in {0}.".format(ctx.message.guild))
            return

        else:
            await ctx.send('Invalid syntax. Usage: ~suggestions <function> <*parameters>')
            return

    except IndexError:
        await ctx.send('Invalid syntax. Usage: ~suggestions <function> <*parameters>')
        return

@bot.command() #Command to manage logging.
async def logs(ctx):
    try:
        content = ctx.message.content.split(' ', maxsplit = 2)[1]
        active_loc = 'logs_active/{0}'.format(ctx.message.guild.id)
        archive_loc = 'logs_archive/{0}'.format(ctx.message.guild.id)

        if content == 'enable': #Subcommand to enable logging for the guild.
            if str(ctx.message.guild.id) in os.listdir('logs_active'):
                await ctx.send('Logging is already enabled for this guild')
                return
            elif str(ctx.message.guild.id) in os.listdir('logs_archive'):
                os.rename(archive_loc, active_loc)
            else:
                with open(active_loc, 'wb') as file:
                    pickle.dump([], file)
            logged.append(ctx.message.guild.id)
            await ctx.send('Logging successfully enabled')
            logging.info('Logging enabled for {0}'.format(ctx.message.guild.name))
            return

        if content == 'disable': #Subcommand to disable logging for the guild.
            if str(ctx.message.guild.id) not in os.listdir('logs_active'):
                await ctx.send('Logging is not enabled for this guild')
                return
            os.rename(active_loc, archive_loc)
            logged.remove(ctx.message.guild.id)
            await ctx.send('Logging successfully disabled for this guild')
            logging.info('Logging disabled for {0}'.format(ctx.message.guild.name))
            return

        if content == 'export': #Subcommand to dump the guild log as a text file
            if str(ctx.message.guild.id) in os.listdir('logs_active'):
                tgt_file = active_loc
            elif str(ctx.message.guild.id) in os.listdir('logs_archive'):
                tgt_file = archive_loc
            else:
                await ctx.send('No log exists for this guild')
                return
            with open(tgt_file, 'rb') as file:
                log = pickle.load(file)
            out = '\n'.join(','.join(item.replace(',', '').replace('\n', '  ')
                            for item in entry) for entry in decode_log(log))
            await ctx.send(file=discord.File(io.StringIO(out), '{0}.csv'.format(time.time())))
            logging.info('Logs dumped for {0}'.format(ctx.message.guild.name))
            return
            
    except IndexError:
        await ctx.send('Invalid syntax. Usage: ~logs <function>')
        return

#Commands end
################################################################################

@bot.event
async def on_message(message):
    if message.guild.id in logged: #Log message if needed
        content = message.clean_content
        for attachment in message.attachments:
            content += '\nATTACHMENT: {0.filename} ({0.url})'.format(attachment)
        with open('logs_active/{0}'.format(message.guild.id), 'rb') as file:
            log = pickle.load(file)
        log.append({
            'version': 1,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'message_id': message.id,
            'channel_id': message.channel.id,
            'channel_name': message.channel.name,
            'author_id': message.author.id,
            'author_name': message.author.display_name,
            'content': content,
        })
        with open('logs_active/{0}'.format(message.guild.id), 'wb') as file:
            pickle.dump(log, file)

    if message.author == bot.user:
        return

    channel = message.channel

    if message.content.split(' ')[0] == '~maintenance':
        try:
            global maintenance #Maintenance mode toggle checking.
            if message.content.split(' ', maxsplit = 1)[1] == 'enable':
                maintenance = True
                logging.warning('Maintenance mode is enabled.')
                await bot.change_presence(activity = discord.Game(name = 'Maintenance mode'))
                await channel.send('Maintenance mode is enabled.')
                return
            if message.content.split(' ', maxsplit = 1)[1] == 'disable':
                maintenance = False
                logging.warning('Maintenance mode is disabled.')
                await bot.change_presence(activity = discord.Game(name = 'Making ciphers circa 2018'))
                await channel.send('Maintenance mode is disabled.')
                return
        except IndexError:
            pass

    if maintenance == True:
        return

    global dest_channel
    try:
        global dest_channel #Determining message destination.
        if isinstance(channel, discord.abc.PrivateChannel):
            guild = 'DM'
            dest_channel = bot.get_channel(channel.id)
        else:
            guild = guilds[message.guild.id]
            dest_channel = bot.get_channel(channels[guild])
    except KeyError: #Guild does not exist in config file.
        guild = message.guild.name
        dest_channel = bot.get_channel(channel.id)

    if message.content.lower() == 'hi' or message.content.lower() == 'hello' or message.content.lower() == 'hey': #:wave:
        logging.info("Processing greeting.")
        dest_channel = channel
        msg = "{0} :wave:".format(random.choice(['Hi', 'Hello', 'Hey']))
        await message.channel.send(msg)
        return

    if 'bruh' in message.content.lower(): #bruh
        logging.info("bruh")
        await message.channel.send(file=discord.File('bruh.mp3'))

    if 'ohhh' in message.content.lower(): #ohhh
        logging.info("ohhh")
        await message.channel.send(file=discord.File('ohhh.mp3'))

    await bot.process_commands(message)

@bot.event
async def on_ready():
    logging.info('Logged in as {0.name} (ID: {0.id})'.format(bot.user))
    logging.info('Running ComplexCipher {0}.'.format(complexcipher2.VERSION))
    await bot.change_presence(activity = discord.Game(name = 'Making ciphers circa 2018'))

if __name__ == '__main__':
    bot.run(token)
