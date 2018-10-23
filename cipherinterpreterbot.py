#Discord bot for running ComplexCipher.
import discord
from discord.ext import commands
import complexciphercore
import logging
import time
import os
import random

logging.basicConfig(level=logging.INFO)

#--------------------------------------------------
#Initialization start

bot = commands.Bot('~')
token = '' #Manually add token here.
guilds = {}
channels = {}
maintenance = False

if token == '': #Get token if it's not already in the code.
    try:
        file = open('token.txt')
        token = file.read()
        file.close()
        print("Token acquired from file.")
    except FileNotFoundError:
        print("Token file not found.")
        try:
            token = os.environ['TOKEN']
            print("Token acquired from environment variable.")
        except KeyError:
            print("Token environment variable not found.")
            print("Token auto detection failed. Stopping execution.")
            end_stop = input("Press enter to quit.")
            quit()
else:
    print("Token acquired from code.")

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
print("\nGuilds and channels initialized.\nguilds = {0}\nchannels = {1}\n".format(guilds, channels))

#Initialization end
#--------------------------------------------------
#Commands start

@bot.command() #Command to change operating channel for cipher functions.
async def setchannel(ctx):
    msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
    content = ctx.message.content.split(' ', maxsplit = 1)[1]
    if content == 'current':
        guilds[ctx.message.guild.id] = ctx.message.guild
        channels[ctx.message.guild] = ctx.message.channel.id
        print("Channel added.\nGuild: {0}\nChannel: #{1}\n".format(ctx.message.guild, ctx.message.channel))
        await ctx.send('Set channel #{0} as output channel.'.format(ctx.message.channel))
        return

@bot.command() #Command to encode text.
async def e(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
        print("Ident as encode request.")
        msg = '{0} {1.message.author.mention} asked to encode ` {2} ` in #{1.message.channel}:'.format(msgtime, ctx, content)
        output = '``` {0} ```'.format(complexciphercore.convert(content, 'encode'))
        await dest_channel.send(msg)
        await dest_channel.send(output)
        print("Succesfully encoded.\n")
    except IndexError:
        await ctx.send('Invalid syntax. (~e <text>)')

@bot.command() #Command to decode text.
async def d(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
        print("Ident as decode request.")
        msg = '{0} {1.message.author.mention} said in #{1.message.channel}:'.format(msgtime, ctx)
        output = '``` {0} ```'.format(complexciphercore.convert(content, 'decode'))
        await dest_channel.send(msg)
        await dest_channel.send(output)
        print("Succesfully decoded.\n")
    except IndexError:
        await ctx.send('Invalid syntax. (~d <text>)')

@bot.command() #Command to accept suggestions.
async def suggest(ctx):
    msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
    content = ctx.message.content.split(' ', maxsplit = 1)[1]
    buffer = ''
    write = False
    print("Ident as suggestion command.")
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
    print("Suggestion added.\n")

@bot.command() #Command to manage suggestions.
async def suggestions(ctx):
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
        msg = await ctx.send('Current suggestions:\n' + buffer + '```')
        seq = ord(seq)
        seq_i = 'A'
        while seq > 65:
            emoji = discord.utils.get(bot.emojis, name = 'letter_{0}'.format(seq_i))
            await msg.add_reaction(emoji)
            seq -= 1
            seq_i = chr(ord(seq_i) + 1)
        print("Displayed suggestions.\n")
        return
    if content == 'clear': #Subcommand to clear all existing suggestions for the guild.
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
        print("Cleared suggestions.\n")
        return
    if content == 'remove': #Subcommand to remove specific suggestions for the guild.
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
        print("Removed suggestions.\n")
        return

#Commands end
#--------------------------------------------------

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
            print('{0} Maintenance mode is enabled.\n'.format(msgtime))
            await bot.change_presence(activity = discord.Game(name = 'Maintenance mode'))
            await channel.send('Maintenance mode is enabled.')
            return
        if message.content.split(' ', maxsplit = 1)[1] == 'disable':
            maintenance = False
            print('{0} Maintenance mode is disabled.\n'.format(msgtime))
            await bot.change_presence(activity = discord.Game(name = 'Making ciphers circa 2018'))
            await channel.send('Maintenance mode is disabled.')
            return
    except IndexError:
        pass

    if maintenance == True:
        return

    global dest_channel
    if isinstance(channel, discord.abc.PrivateChannel): #Determining message destination.
        guild = 'DM'
        dest_channel = bot.get_channel(channel.id)
    else:
        guild = guilds[message.guild.id]
        dest_channel = bot.get_channel(channels[guild])

    print("{0} Checking message by {1.author} in {2}: #{3}...".format(msgtime, message, guild, channel))

    if message.content.lower() == 'hi' or message.content.lower() == 'hello' or message.content.lower() == 'hey': #:wave:
        print("Ident as greeting.")
        dest_channel = channel
        msg = "{0} :wave:".format(random.choice(['Hi', 'Hello', 'Hey']))
        await dest_channel.send(msg)
        print("Succesfully greeted.\n")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print('\nLogged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('Running ComplexCipher {0}.\n'.format(complexciphercore.VERSION))
    await bot.change_presence(activity = discord.Game(name = 'Making ciphers circa 2018'))

bot.run(token)
