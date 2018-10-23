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
servers = {}
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

with open('config.txt') as file: #Get list of serviced servers and their corresponding output channels and IDs.
    for line in file:
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        line = line.split('=', maxsplit = 1)
        try:
            if section == 'SERVERS':
                name = line[0].strip()
                id = (line[1].split('"'))[1]
                servers[id] = name
            if section == 'CHANNELS':
                name = line[0].strip()
                id = (line[1].split('"'))[1]
                channels[name] = id
        except IndexError:
            continue
print("\nServers and channels initialized.\nservers = {0}\nchannels = {1}\n".format(servers, channels))

#Initialization end
#--------------------------------------------------
#Commands start

@bot.command(pass_context = True) #Command to change operating channel for cipher functions.
async def setchannel(ctx):
    msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
    content = ctx.message.content.split(' ', maxsplit = 1)[1]
    if content == 'current':
        servers[ctx.message.server.id] = ctx.message.server
        channels[ctx.message.server] = ctx.message.channel.id
        print("Channel added.\nServer: {0}\nChannel: #{1}\n".format(ctx.message.server, ctx.message.channel))
        await bot.say('Set channel #{0} as output channel.'.format(ctx.message.channel))
        return

@bot.command(pass_context = True) #Command to encode text.
async def e(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
        print("Ident as encode request.")
        msg = '{0} {1.message.author.mention} asked to encode ` {2} ` in #{1.message.channel}:'.format(msgtime, ctx, content)
        output = '``` {0} ```'.format(complexciphercore.convert(content, 'encode'))
        await bot.send_message(dest_channel, msg)
        await bot.send_message(dest_channel, output)
        print("Succesfully encoded.\n")
    except IndexError:
        await bot.say('Invalid syntax. (~e <text>)')

@bot.command(pass_context = True) #Command to decode text.
async def d(ctx):
    try:
        msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
        content = ctx.message.content.split(' ', maxsplit = 1)[1]
        print("Ident as decode request.")
        msg = '{0} {1.message.author.mention} said in #{1.message.channel}:'.format(msgtime, ctx)
        output = '``` {0} ```'.format(complexciphercore.convert(content, 'decode'))
        await bot.send_message(dest_channel, msg)
        await bot.send_message(dest_channel, output)
        print("Succesfully decoded.\n")
    except IndexError:
        await bot.say('Invalid syntax. (~d <text>)')

@bot.command(pass_context = True) #Command to accept suggestions.
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
                buffer += '{0} = "{1}"\n'.format(ctx.message.server.id, content)
                write = False
    with open('config.txt', 'w') as file:
        file.write(buffer)
    await bot.say('Your suggestion has been recorded.')
    print("Suggestion added.\n")

@bot.command(pass_context = True) #Command to manage suggestions.
async def suggestions(ctx):
    msgtime = time.strftime('[%H:%M:%S UTC]', time.gmtime())
    content = ctx.message.content.split(' ', maxsplit = 2)[1]
    if content == 'view': #Subcommand to view existing suggestions for the server.
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
                if line[0].strip() == ctx.message.server.id:
                    buffer += '{0}: {1}\n'.format(seq, line[1].strip())
                    seq = chr(ord(seq) + 1)
        await bot.say('Current suggestions:\n' + buffer + '```')
        print("Displayed suggestions.\n")
        return
    if content == 'clear': #Subcommand to clear all existing suggestions for the server.
        buffer = ''
        with open('config.txt', 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    section = line[1:-1]
                if section == 'SUGGESTIONS' and line.split('=', maxsplit = 1)[0].strip() == ctx.message.server.id:
                    continue
                buffer += line + '\n'
        with open('config.txt', 'w') as file:
            file.write(buffer)
        await bot.say('Suggestions cleared.')
        print("Cleared suggestions.\n")
        return
    if content == 'remove': #Subcommand to remove specific suggestions for the server.
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
                if section == 'SUGGESTIONS' and line.split('=', maxsplit = 1)[0].strip() == ctx.message.server.id:
                    if seq in r_list:
                        seq += 1
                        continue
                    seq += 1
                buffer += line + '\n'
        with open('config.txt', 'w') as file:
            file.write(buffer)
        await bot.say('Suggestions removed.')
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
            await bot.change_presence(game = discord.Game(name = 'Maintenance mode'))
            await bot.say('Maintenance mode is enabled.')
            return
        if message.content.split(' ', maxsplit = 1)[1] == 'disable':
            maintenance = False
            print('{0} Maintenance mode is disabled.\n'.format(msgtime))
            await bot.change_presence(game = discord.Game(name = 'Making ciphers circa 2018'))
            await bot.say('Maintenance mode is disabled.')
            return
    except IndexError:
        pass

    if maintenance == True:
        return

    global dest_channel
    if channel.is_private == True: #Determining message destination.
        server = 'DM'
        dest_channel = bot.get_channel(channel.id)
    else:
        server = servers[message.server.id]
        dest_channel = bot.get_channel(channels[server])

    print("{0} Checking message by {1.author} in {2}: #{3}...".format(msgtime, message, server, channel))

    if message.content.lower() == 'hi' or message.content.lower() == 'hello': #:wave:
        print("Ident as greeting.")
        dest_channel = channel
        msg = "{0} :wave:".format(random.choice(['Hi', 'Hello', 'Hey']))
        await bot.send_message(dest_channel, msg)
        print("Succesfully greeted.\n")

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print('\nLogged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('Running ComplexCipher {0}.\n'.format(complexciphercore.VERSION))
    await bot.change_presence(game = discord.Game(name = 'Making ciphers circa 2018'))

bot.run(token)
