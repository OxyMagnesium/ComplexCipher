# New and improved core that is actually useful and has applications (maybe)
VERSION = '2.0.0'

# [[A(2)] [B(1)] [C(v)] [text(v)]] (62)
# A specifies the length of the entire lock
# B specifies the number of lock digits to be read at a time
# C represents the lock digits which affect the offset being used

# The entire generated block gets converted into a hexadecimal representation of
# each character in it to make it easier on the eyes and avoid rendering issues
# with the non-graphical characters in there. The number thus generated is
# multiplied with a two digit hexadecimal number that is appended to the start
# of the string to make it look less not random and bring the total length of
# the block to 128 characters, which happens to be the length of a SHA512 hash.

# The only way to decode the cipher even if you do have this program is to have
# the correct dictionary. As a dictionary is 92 characters long, there are is a
# total of 92! unique dictionaries, a number that is on the order of 10^142.

from secrets import randbelow

standard_dictionary = (  '\n !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKL'
                       + 'MNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz')

def randof(digits):
    return 10**(digits - 1) + randbelow(10**(digits) - 10**(digits - 1))


def to_hex(text):
    string = ''
    for char in text:
        string += ('' if ord(char) >= 16 else '0') + hex(ord(char))[2 : ]
    return string


def from_hex(text):
    if len(text) % 2 != 0:
        raise ValueError('length of the string must be odd')
    string = ''
    for i in range(0, len(text), 2):
        string += chr(int(text[i : i + 2], 16))
    return string


def generate_dictionary():
    dictionary = [char for char in standard_dictionary]
    for _ in range(len(dictionary)):
        for i in range(len(dictionary)):
            j = randbelow(len(dictionary))
            t = dictionary[j]
            dictionary[j] = dictionary[i]
            dictionary[i] = t
    return ''.join(dictionary)


def transform(dict, lock, text, mode):
    if mode not in ('e', 'd'):
        raise ValueError(f'\'{mode}\' is not a valid mode')
    elif mode == 'e':
        sign = 1
    elif mode == 'd':
        sign = -1

    string = [char for char in text]

    lock_len = int(lock[ : 2])
    read_len = int(lock[2])
    read_pos = int(lock[read_len])
    offset = sign*int(lock[read_pos : read_pos + read_len])

    for i in range(len(text)):
        if read_pos + read_len > lock_len:
            offset += sign*int(lock[read_pos : ]
                               + lock[2 : 2 + (read_pos + read_len) % lock_len])
            read_pos = 2 + (read_pos + read_len) % lock_len
        else:
            offset += sign*int(lock[read_pos : read_pos + read_len])
            read_pos = read_pos + read_len

        if offset % 2 != 0:
            sign *= -1

        string[i] = dict[(dict.index(string[i]) + offset) % len(dict)]

    return ''.join(string)


def encode(text, dict = standard_dictionary):
    if len(text) > 50: # Temporary until I figure out a good way to do this
        raise ValueError('strings longer than 50 characters are not supported')

    blocks = []
    while len(text) > 50:
        blocks.append(text[-50 : ])
        text = text[ : -64]
    blocks.append(text)

    lock = str(randof(60 - len(text)))
    while int(lock) % int(lock[0]) == 0:
        lock = str(randof(60 - len(text)))
    lock = str(len(lock) + 2) + lock

    packaged = to_hex(lock + transform(dict, lock, ''.join(blocks), 'e'))

    scrambler = 17 + randbelow(16**2 - 17)
    packaged = hex(scrambler*int(packaged, 16))[2 : ]
    while len(packaged) < 126:
        packaged = '0' + packaged
    packaged = hex(scrambler)[2 : ] + packaged

    return packaged.upper()


def decode(text, dict = standard_dictionary):
    text = from_hex(hex(int(text[2 : ], 16)//int(text[ : 2], 16))[2 : ])

    lock = text[ : int(text[ : 2])]
    text = text[int(text[ : 2]) : ]

    return transform(dict, lock, text, 'd')


# For testing
if __name__ == '__main__':
    f = input("Enter task (e = encode, d = decode, g = generate dictionary): ")
    if f in ('e', 'd'):
        u_dict = input("Enter dictionary to use (blank for default): ")
        if u_dict == '':
            dict = standard_dictionary
        else:
            dict = from_hex(u_dict)
            for char in standard_dictionary:
                if char not in dict or len(dict) != 92:
                    print("\nInvalid dictionary.")
                    exit()
        t = input("Enter text to be encoded/decoded: ")
        print('\n' + (encode(t, dict) if f == 'e' else decode(t, dict)))
    elif f == 'g':
        print('\n' + to_hex(generate_dictionary()))
    else:
        print("\nInvalid input.")
    print('')
