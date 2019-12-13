# New and improved core that is actually useful and has applications (maybe)
VERSION = '2.1.0'

import logging
from secrets import randbelow, choice
from numpy import base_repr as base_n
from timeit import default_timer as timer

standard_dictionary = (  '0A28292A2B303132333435363738393A3B40414243444546'
                       + '4748494A4B505152535455565758595A5B60616263646566'
                       + '6768696A6B707172737475767778797A7B80818283848586'
                       + '8788898A8B909192939495969798999A9BA0A1A2A3A4A5A6')

def randof(digits, base = 10):
    return base**(digits - 1) + randbelow(base**(digits) - base**(digits - 1))


def randstr(length, dictionary = None):
    if not dictionary:
        dictionary = from_base(standard_dictionary, 12)
    string = ''
    for i in range(length):
        string += dictionary[randbelow(len(dictionary))]
    return string


def to_base(text, base = 16):
    string = ''
    for char in text:
        string += ('' if ord(char) >= base else '0')
        string += base_n(ord(char), base)
    return string


def from_base(text, base = 16):
    if len(text) % 2 != 0:
        raise ValueError('length of the string must be even')
    string = ''
    for i in range(0, len(text), 2):
        string += chr(int(text[i:i + 2], base))
    return string


def convert_base(num, b1, b2):
    return base_n((int(num, b1)), b2)


def generate_dictionary():
    dictionary = [char for char in from_base(standard_dictionary, 12)]
    for _ in range(len(dictionary)):
        for i in range(len(dictionary)):
            j = randbelow(len(dictionary))
            t = dictionary[j]
            dictionary[j] = dictionary[i]
            dictionary[i] = t
    return to_base(''.join(dictionary), 12).upper()


def transform(text, key, dict, mode):
    if mode not in ('e', 'd'):
        raise ValueError(f'\'{mode}\' is not a valid mode')
    elif mode == 'e':
        base_sign = 1
        iter_key = key
    elif mode == 'd':
        base_sign = -1
        iter_key = key[ : :-1]

    string = [char for char in text]

    for pass_num, digit in enumerate(iter_key):
        sign = base_sign
        modifier = int(key[ :2], 36)
        offset = sign*int(key[2: ], 36)

        for i in range(len(text)):
            if mode == 'e':
                if pass_num % 2 != 0:
                    i = len(text) - i - 1
                string[i] = dict[(dict.index(string[i]) + offset) % len(dict)]
                multiplier = ord(string[i])

            if mode == 'd':
                if pass_num % 2 == 0:
                    i = len(text) - i - 1
                multiplier = ord(string[i])
                string[i] = dict[(dict.index(string[i]) + offset) % len(dict)]

            offset *= multiplier
            offset %= (modifier if offset > 0 else -modifier)
            offset += sign*modifier*int(digit, 36)
            sign = (-sign if offset % 2 == 0 else sign)

    return ''.join(string)


def encode(text, dictionary = standard_dictionary):
    dictionary = from_base(dictionary, 12)

    blocks = []
    while len(text) > 12:
        min_per_block = -(-len(text))//(1 + (len(text) - 1)//12)
        in_this_block = 12 - randbelow(12 - min_per_block + 1)
        blocks.append(text[-in_this_block: ])
        text = text[ :-in_this_block]
    blocks.append(text)

    block = ''
    cipher = ''
    ciphers = []
    while len(blocks):
        block = blocks.pop()
        key = base_n(randof(4, 36), 36)
        pos = base_n(randbelow(12 - len(block) + 1), 18)
        pad = randstr(12 - len(block)) + pos + base_n(len(block), 18)
        block = pad[ :int(pos, 18)] + block + pad[int(pos, 18): ]

        cipher = transform(block, key, dictionary, 'e')
        cipher = convert_base(to_base(cipher, 12), 12, 36)
        cipher = ('' if len(cipher) == 20 else '0') + cipher

        ciphers.append(key + cipher)

    return ''.join(ciphers).upper()


def decode(text, dictionary = standard_dictionary):
    dictionary = from_base(dictionary, 12)

    ciphers = []
    while len(text):
        ciphers.append(text[-24:-20] + convert_base(text[-20: ], 36, 12))
        text = text[ :-24]

    cipher = ''
    block = ''
    blocks = []
    while len(ciphers):
        cipher = ciphers.pop()
        key = cipher[ :4]
        cipher = ('' if len(cipher[4: ]) == 28 else '0') + cipher[4: ]
        block = from_base(cipher, 12)

        block = transform(block, key, dictionary, 'd')
        block = block[int(block[-2], 18):int(block[-2], 18) + int(block[-1], 18)]

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
            string = ''.join(choice(dictionary) for _ in range(n))
            enc = encode(string, d)
            dec = decode(enc, d)
            if string != dec:
                print(string)
    except Exception as error:
        print(string)
        raise error
    end_t = timer()
    print(f"Checked {iters} strings successfully in {end_t - start_t} s")


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
