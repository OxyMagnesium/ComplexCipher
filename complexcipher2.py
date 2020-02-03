# New and improved core that is actually useful and has applications (maybe)

# This cipher works by iterating over the characters in a given string and
# substituting them for a different character some distance away from them in
# a dictionary according to some offsets determined by random elements generated
# during the encoding process as well as the contents of the string itself.

# In the encoding process, the string is first divided into multiple discrete
# blocks such that the number of blocks created is the minimum required, but
# the sections of text in each block are of a variable length. Then, for each
# block, a random 20 bit key (four base 32 digits) is generated, padding of
# random characters is added on either side of the block, so the length comes
# up to 12 characters. Two 4 bit numbers signifying the position of the actual
# text in the block and its length are appended to the end. The entire block
# is transformed using the previously generated key, the output is converted to
# its Unicode values in base 12 represented in base 32, and appended to the key.

# The final product is a 125 bit number that can be uniquely decoded to the
# segment of the original string that that particular block contained. By
# chaining multiple blocks like this, a cipher is produced that -
# -> obsfucates the exact length of the message being sent
# -> has at MINIMUM over a million different possible ciphers for a single
#    message, with the possibilities growing exponentially with message length
# -> is completely resistant to manipulation by editing the cipher

VERSION = '2.1.1'

import logging
from secrets import randbelow, choice
from numpy import base_repr as base_n
from timeit import default_timer as timer

# A standard dictionary with characters arranged according to Unicode values.
standard_dictionary = (  '0A28292A2B303132333435363738393A3B40414243444546'
                       + '4748494A4B505152535455565758595A5B60616263646566'
                       + '6768696A6B707172737475767778797A7B80818283848586'
                       + '8788898A8B909192939495969798999A9BA0A1A2A3A4A5A6')

# Returns a random number of the given number of digits in the given base.
def randof(digits, base = 10):
    return base**(digits - 1) + randbelow(base**(digits) - base**(digits - 1))

# Returns a random string composed of characters in the dictionary.
def randstr(length, dictionary = None):
    if not dictionary:
        dictionary = from_base(standard_dictionary, 12)
    string = ''
    for i in range(length):
        string += dictionary[randbelow(len(dictionary))]
    return string

# Converts each character in the given string into its Unicode value.
def to_base(text, base = 16):
    string = ''
    for char in text:
        string += ('' if ord(char) >= base else '0')
        string += base_n(ord(char), base)
    return string

# Reverses the effect of the above function.
def from_base(text, base = 16):
    if len(text) % 2 != 0:
        raise ValueError('length of the string must be even')
    string = ''
    for i in range(0, len(text), 2):
        string += chr(int(text[i:i + 2], base))
    return string

# Converts the given number from its current base b1 to the given base b2.
def convert_base(num, b1, b2):
    return base_n((int(num, b1)), b2)

# Generates a random dictionary.
def generate_dictionary():
    dictionary = [char for char in from_base(standard_dictionary, 12)]
    for _ in range(len(dictionary)):
        for i in range(len(dictionary)):
            j = randbelow(len(dictionary))
            t = dictionary[j]
            dictionary[j] = dictionary[i]
            dictionary[i] = t
    return to_base(''.join(dictionary), 12).upper()

# Returns True if the given string is a valid dictionary, else False.
def check_dictionary(dictionary):
    dictionary = from_base(dictionary, 12)
    reference = from_base(standard_dictionary, 12)
    for char in reference:
        if char not in dictionary:
            return False
    return True

# Performs the main transformation on the given segment of the string.
def transform(text, key, dict, mode):
    if mode not in ('e', 'd'): # Checking the mode is valid
        raise ValueError(f'\'{mode}\' is not a valid mode')
    elif mode == 'e': # For encoding, just use the key as it is.
        base_sign = 1
        iter_key = key
    elif mode == 'd': # For decoding, reverse the key and the initial sign.
        base_sign = -1
        iter_key = key[ : :-1]

    string = [char for char in text] # Convert the string into a list.

    # For each digit in the key:
    # The first two digits of the key become a limiting value for the offset.
    # The last two digits of the key become an additive offset.
    for pass_num, digit in enumerate(iter_key):
        sign = base_sign
        modifier = int(key[ :2], 32)
        offset = sign*int(key[2: ], 32)

        # Every character in the string is iterated over
        for i in range(len(text)):
            if mode == 'e': #When encoding, iterate over even passes in reverse.
                if pass_num % 2 != 0:
                    i = len(text) - i - 1

                # Replace this character with a character that is {offset} away
                # from it in the dictionary, and then create a multiplicative
                # offset based on the character that it got replaced with.
                string[i] = dict[(dict.index(string[i]) + offset) % len(dict)]
                multiplier = ord(string[i])

            if mode == 'd': #When decoding, iterate over odd passes in reverse.
                if pass_num % 2 == 0:
                    i = len(text) - i - 1

                # Create the multiplicative offset based on the character the
                # original got replaced with as during encoding, and restore
                # the original by using the negative of the original offset.
                multiplier = ord(string[i])
                string[i] = dict[(dict.index(string[i]) + offset) % len(dict)]

            # Using the multiplier and modifier, perform some mutations on the
            # offset to percievably randomize it for the next character.
            offset *= multiplier
            offset %= (modifier if offset > 0 else -modifier)
            offset += sign*modifier*int(digit, 32)
            sign = (-sign if offset % 2 == 0 else sign)

    return ''.join(string)

# Returns the text encoded with the given dictionary if all characters in it
# are valid, else returns None.
def encode(text, dictionary = None):
    if not dictionary:
        dictionary = from_base(standard_dictionary, 12)
    else:
        dictionary = from_base(dictionary, 12)
    text = text.strip()

    blocks = []
    while len(text) > 12:
        min_per_block = len(text)//(1 + (len(text) - 1)//12)
        in_this_block = 12 - randbelow(12 - min_per_block + 1)
        blocks.append(text[-in_this_block: ])
        text = text[ :-in_this_block]
    blocks.append(text)

    block = ''
    cipher = ''
    ciphers = []
    while len(blocks):
        block = blocks.pop()
        key = base_n(randof(4, 32), 32)
        pos = base_n(randbelow(12 - len(block) + 1), 16)
        pad = randstr(12 - len(block)) + pos + base_n(len(block), 16)
        block = pad[ :int(pos, 16)] + block + pad[int(pos, 16): ]

        try:
            cipher = transform(block, key, dictionary, 'e')
        except ValueError:
            return None

        cipher = convert_base(to_base(cipher, 12), 12, 32)
        cipher = ('' if len(cipher) == 21 else '0') + cipher

        ciphers.append(key + cipher)

    return ''.join(ciphers).upper()

# Returns the cipher decoded using the given dictionary if the cipher-dictionary
# combination is valid, else returns None.
def decode(text, dictionary = None):
    if not dictionary:
        dictionary = from_base(standard_dictionary, 12)
    else:
        dictionary = from_base(dictionary, 12)
    text = text.strip()

    ciphers = []
    while len(text):
        ciphers.append(text[-25:-21] + convert_base(text[-21: ], 32, 12))
        text = text[ :-25]

    cipher = ''
    block = ''
    blocks = []
    while len(ciphers):
        cipher = ciphers.pop()
        key = cipher[ :4]
        cipher = ('' if len(cipher[4: ]) == 28 else '0') + cipher[4: ]
        block = from_base(cipher, 12)

        try:
            block = transform(block, key, dictionary, 'd')
        except ValueError:
            return None

        pos = int(block[-2], 16)
        block = block[pos:pos+ int(block[-1], 16)]

        blocks.append(block)

    return ''.join(blocks)

# For testing
def check(iters):
    start_t = timer()
    dictionary = from_base(standard_dictionary, 12)
    try:
        for _ in range(iters):
            d = standard_dictionary
            #d = generate_dictionary()
            n = 1 + randbelow(100)
            string = ''.join(choice(dictionary) for _ in range(n)).strip()
            enc = encode(string, d)
            dec = decode(enc, d)
            if string != dec:
                print("INCORRECT RESULT START")
                print(string)
                print("INCORRECT RESULT END")
    except Exception as error:
        print(string)
        raise error
    end_t = timer()
    print(f"Checked {iters} strings successfully in {end_t - start_t} s")

# Also for testing
if __name__ == '__main__':
    f = input("Enter task (e = encode, d = decode, g = generate dictionary): ")
    if f in ('e', 'd'):
        u_dict = input("Enter dictionary to use (blank for default): ")
        if u_dict == '':
            dict = standard_dictionary
        else:
            dict = u_dict
            for char in from_base(standard_dictionary, 12):
                if char not in from_base(dict, 12) or len(dict) != 192:
                    print("\nInvalid dictionary.")
                    exit()
        t = input("Enter text to be encoded/decoded: ")
        print('\n' + (encode(t, dict) if f == 'e' else decode(t, dict)))
    elif f == 'g':
        print('\n' + generate_dictionary())
    else:
        print("\nInvalid input.")
    print('')
