import discord
import logging
import complexciphercore
import time

logging.basicConfig(level=logging.INFO)

TOKEN = ''
dest_channel = '491938711693426688' #secret-codes

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

    try:
        if content.startswith('!e'):
            print("Ident as encode request.")
            content = (content.split(' ',maxsplit = 1))
            content.pop(0)
            msg = ('(@%s) {0.author.mention} asked to encode ```%s``` in %s. Output:\n```%s```' % (msgtime, *content, channel, complexciphercore.convert(*content,'encode'))).format(message)
            await client.send_message(client.get_channel(dest_channel),msg)
            print("Succesfully encoded.")

        if int(content[0:(int(content[0]) + 1)]) in range(11,999999):
            print("Ident as code to be decoded.")
            msg = ('(@%s) {0.author.mention} said in %s:\n```%s```' % (msgtime, channel, complexciphercore.convert(content,'decode'))).format(message)
            await client.send_message(client.get_channel(dest_channel),msg)
            print("Succesfully decoded.")
    except ValueError:
        print("Message not relevant.")
    except IndexError:
        print("Message not relevant.")

@client.event
async def on_ready():
    print('\nLogged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
