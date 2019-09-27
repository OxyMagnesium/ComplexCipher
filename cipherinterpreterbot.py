#Discord bot for running ComplexCipher.
import discord
from discord.ext import commands
import complexciphercore
import logging
import time
import os
import random
import requests

logging.basicConfig(format = '%(levelname)s:%(name)s:(%(asctime)s): %(message)s',
                    datefmt = '%d-%b-%y %H:%M:%S',
                    level = logging.INFO)

################################################################################
#Initialization start

bot = commands.Bot('~')
token = '' #Manually add token here.
guilds = {}
channels = {}
maintenance = False
bot.remove_command('help')

me = bot.get_channel(591295364498194571)

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

with open('config.txt') as file: #Get list of serviced guilds and their corresponding output channels and IDs.
    for line in file:
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        line = line.split('=', maxsplit = 1)
        try:
            if section == 'GUILDS':
                name = line[0].strip()
                id = int(line[1].split('"')[1])
                guilds[id] = name
            if section == 'CHANNELS':
                name = line[0].strip()
                id = int(line[1].split('"')[1])
                channels[name] = id
        except IndexError:
            continue
logging.info("Guilds and channels initialized.")

#Initialization end
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
    content = ctx.message.content.split(' ', maxsplit = 1)[1]
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
        msg = '{0} {1.message.author.mention} asked to encode ` {2} ` in #{1.message.channel}:'.format(msgtime, ctx, content)
        output = '``` {0} ```'.format(complexciphercore.convert(content, 'encode', '-noprint'))
        await dest_channel.send(msg)
        await dest_channel.send(output)
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
        msg = '{0} {1.message.author.mention} asked to decode ` {2} ` in #{1.message.channel}:'.format(msgtime, ctx, content)
        output = '``` {0} ```'.format(complexciphercore.convert(content, 'decode', '-noprint'))
        await dest_channel.send(msg)
        await dest_channel.send(output)
        return
    except IndexError:
        await ctx.send('Invalid syntax. Usage: ~d <text>')
        return

@bot.command() #Command to accept suggestions.
async def suggest(ctx):
    msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
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

@bot.command() #Command to manage suggestions.
async def suggestions(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
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

#Commands end
################################################################################

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    channel = message.channel
    msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())

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
        if isinstance(channel, discord.abc.PrivateChannel): #Determining message destination.
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
        await dest_channel.send(msg)
        return

    await bot.process_commands(message)

@bot.event
async def on_ready():
    logging.info('Logged in as {0.name} (ID: {0.id})'.format(bot.user))
    logging.info('Running ComplexCipher {0}.'.format(complexciphercore.VERSION))
    await bot.change_presence(activity = discord.Game(name = 'Making ciphers circa 2018'))

    ip = requests.get('https://api.ipify.org').text
    logging.info(f'Current external IP address is {ip}.')
    dest = bot.get_channel(channels['Egto'])
    await dest.send(f'I just came online with IP address {ip}.')
    logging.info('Sent logon message to Egto.')

bot.run(token)
