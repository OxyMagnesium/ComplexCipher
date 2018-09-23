# ComplexCipher
This is a script that can generate and decrypt ciphers that may or may not be very hard to crack. Probably aren't if it's on here, but whatever.

1. complexciphercore.py: Contains the core cipher generation/decryption functionality.
2. complexcipherui.py: Contains a local interface for using the script.
3. cipherinterpreterbot.py: Discord bot that can encode text if you message it starting with !e, and decode text if you message it with something that it thinks is a code, although detection on that is a little wonky considering that right now it'll try to decode anything that starts with a number ¯\\\_(ツ)_/¯.
