import discord
import logging
import complexciphercore
import time

logging.basicConfig(level=logging.INFO)

token = ''
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
        dest_channel = channel.id
    else:
        dest_channel = server_channel

    try:
        if content.startswith('!e'):
            print("Ident as encode request.")
            content = (content.split(' ',maxsplit = 1))
            content.pop(0)
            msg = ('(@%s) {0.author.mention} asked to encode ``` %s ``` in %s. Output:\n``` %s ```' % (msgtime, *content, channel, complexciphercore.convert(*content,'encode'))).format(message)
            await client.send_message(client.get_channel(dest_channel),msg)
            print("Succesfully encoded.")
            return

        if int(content[0:(int(content[0]) + 1)]) in range(11,6999999):
            print("Ident as code to be decoded.")
            msg = ('(@%s) {0.author.mention} said in %s:\n``` %s ```' % (msgtime, channel, complexciphercore.convert(content,'decode'))).format(message)
            await client.send_message(client.get_channel(dest_channel),msg)
            print("Succesfully decoded.")
            return

        else:
            print("Message not relevant.")
            return

    except ValueError:
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
