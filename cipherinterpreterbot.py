#Discord bot for running ComplexCipher.
import discord
import logging
import complexciphercore
import time
import os

logging.basicConfig(level=logging.INFO)

token = '' #Manually add token here.
servers = {}
channels = {}

if token == '': #Get token if it's not already in the code.
    try:
        file = open('token.txt')
        token = file.read()
        file.close()
        print("Token acquired from file.")
    except FileNotFoundError:
        print("Token file not found.")
        try:
            token = os.environ('TOKEN')
            print("Token acquired from environment variable.")
        except KeyError:
            print("Token environment variable not found.")
            print("Token auto detection failed. Stopping execution.")
            end_stop = input("Press enter to quit.")
            quit()

file = open('config.txt') #Get list of serviced servers and their corresponding IDs.

for line in file:
    line = line.strip()
    if line.startswith('[') and line.endswith(']'):
        section = line[1:-1]
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
        pass

file.close()
print("\nServers and channels initialized.\nservers = {0}\nchannels = {1}\n".format(servers, channels))

client = discord.Client()

@client.event
async def on_message(message):
    gmtime = time.gmtime() #Get message parameters.
    msgtime = '{0}:{1}:{2} UTC'.format(gmtime.tm_hour, gmtime.tm_min, gmtime.tm_sec)
    content = message.content
    channel = message.channel

    if message.author == client.user:
        return

    if channel.is_private == True: #Ascertain message destination.
        server = 'DM'
        dest_channel = client.get_channel(channel.id)
    else:
        server = servers[message.server.id]
        dest_channel = client.get_channel(channels[server])

    print("(@{0}) Checking message by {1.author} in {2}: #{3}...".format(msgtime, message, server, channel))

    try:
        if content.startswith('!e') or content.startswith('~e'): #Check for encode request.
            print("Ident as encode request.")
            content = content.split(' ', maxsplit = 1)
            content.pop(0)
            msg = '(@{0}) {1.author.mention} asked to encode ` {2} ` in #{3}:'.format(msgtime, message, *content, channel)
            output = '``` {0} ```'.format(complexciphercore.convert(*content, 'encode'))
            await client.send_message(dest_channel, msg)
            await client.send_message(dest_channel, output)
            print("Succesfully encoded.\n")
            return

        if int(content[0:(int(content[0]) + 1)]) in range(11,9999999999): #Check for encoded text.
            print("Ident as code to be decoded.")
            msg = '(@{0}) {1.author.mention} said in #{2}:'.format(msgtime, message, channel)
            output = '``` {0} ```'.format(complexciphercore.convert(content, 'decode'))
            await client.send_message(dest_channel, msg)
            await client.send_message(dest_channel, output)
            print("Succesfully decoded.\n")
            return

        else:
            print("Message not relevant.\n")
            return

    except (ValueError, IndexError): #The method used to check for encoded text throws errors if it turns out not to be a cipher, hence this.
        print("Message not relevant.\n")
        return

@client.event
async def on_ready():
    print('\nLogged in as')
    print(client.user.name)
    print(client.user.id)
    print('Running ComplexCipher {0}.\n'.format(complexciphercore.VERSION))

client.run(token)
