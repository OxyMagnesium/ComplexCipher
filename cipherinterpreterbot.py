#Discord bot for running ComplexCipher.
import discord
import logging
import complexciphercore
import time

logging.basicConfig(level=logging.INFO)

token = '' #Manually add token here.
server_channel = '491938711693426688' #secret-codes

if token == '':
    try:
        file = open('token.txt')
        token = file.read()
        file.close()
    except FileNotFoundError:
        print("Token not found. Please check that the file is correctly named or add the token directly into the code.")
        end_stop = input("Press enter to quit.")
        quit()

client = discord.Client()

@client.event
async def on_message(message):
    gmtime = time.gmtime()
    msgtime = '%s:%s:%s UTC' % (gmtime.tm_hour, gmtime.tm_min, gmtime.tm_sec)
    content = message.content
    channel = message.channel

    if message.author == client.user:
        return

    print("\n(@%s) Checking message by %s in %s..." % (msgtime, message.author, channel))

    if channel.is_private == True:
        dest_channel = client.get_channel(channel.id)
    else:
        dest_channel = client.get_channel(server_channel)

    try:
        if content.startswith('!e'): #Check for encode request.
            print("Ident as encode request.")
            content = (content.split(' ',maxsplit = 1))
            content.pop(0)
            msg = ('(@%s) {0.author.mention} asked to encode ` %s ` in %s: ' % (msgtime, *content, channel)).format(message)
            output = '``` %s ```' % complexciphercore.convert(*content, 'encode')
            await client.send_message(dest_channel, msg)
            await client.send_message(dest_channel, output)
            print("Succesfully encoded.")
            return

        if int(content[0:(int(content[0]) + 1)]) in range(11,9999999999): #Check for encoded text.
            print("Ident as code to be decoded.")
            msg = ('(@%s) {0.author.mention} said in %s: ' % (msgtime, channel)).format(message)
            output = '``` %s ```' % complexciphercore.convert(content, 'decode')
            await client.send_message(dest_channel,msg)
            await client.send_message(dest_channel, output)
            print("Succesfully decoded.")
            return

        else:
            print("Message not relevant.")
            return

    except ValueError: #The method used to check for encoded text throws errors if it turns out not to be a code, hence this.
        print("Message not relevant.")
        return
    except IndexError:
        print("Message not relevant.")
        return

@client.event
async def on_ready():
    print('\nLogged in as')
    print(client.user.name)
    print(client.user.id)
    print('Running ComplexCipher %s.' % complexciphercore.VERSION)
    print('------')

client.run(token)
