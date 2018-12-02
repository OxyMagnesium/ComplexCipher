#Core function of ComplexCipher.
VERSION = '1.5.2'

def convert(text, type, args = ''): #Main function.
    import random
    dictionary = ['0' , '!' , 'a' , 'b' , '1' , 'c' , 'd' , '2' , 'e' , '(' , 'f' , ',' , 'g' , '/' , 'h' , '3' , 'i' , 'j' , '.' , 'k' , 'l' , '4' , 'm' , ' ' , 'n' , '5' , 'o' , 'p' , ':' , 'q' , 'r' , '6' , 's' , '-' , 't' , '\'' , 'u' , ')' , 'v' , '7' , 'w' , 'x' , '8' , 'y' , 'z' , '?' , '9']

    text = text.strip() #Setting up requirements for the algorithm.
    buffer = ''
    offset_included = 0
    caps = False
    change_case = False

    if type == 'encode': #Checking whether to encode or decode. If encoding, a random offset is added to the front of the string and used to offset the multiplier, increasing scrambling.
        if '-seed' not in args: #Offset can be manually set using arguments.
            random.seed()
            randlist = [random.randint(1,9), random.randint(10,99), random.randint(100,999), random.randint(1000,9999), random.randint(10000,99999), random.randint(100000,999999), random.randint(1000000,9999999), random.randint(10000000,99999999), random.randint(100000000,999999999)]
            offset = random.choice(randlist)
        else:
            args_s = args.split('-')
            for arg in args_s:
                arg = arg.strip()
                if 'seed' not in arg:
                    continue
                else:
                    offset = int(arg.split('(')[1].split(')')[0])
                    break
        offset_l = len(str(offset))

        mult = 1 * offset
        output = '{0}{1}'.format(str(offset_l), str(offset))

    elif type == 'decode': #If decoding, the initial offset is retrieved from the front of the string and that character is skipped by the algorithm.
        offset_l = int(text[0]) + 1
        offset = int(text[1:(offset_l)])
        offset_included = offset_l

        mult = -1 * offset
        output = ''

    #Algorithm start

    for letter in range(offset_included, len(text)): #Selecting a character.
        input = text[letter]

        if input.isalpha() and type == 'encode': #While encoding, if an input character is uppercase, '|' is added before the converted character.
            if input.isupper() and caps == False:
                caps = True
                change_case = True
            if input.islower() and caps == True:
                caps = False
                change_case = True

        if input == '|' and type == 'decode': #If '|' shows up while decoding, that means that all characters until the next '|' are to be uppercase and vice versa.
            if caps == False:
                caps = True
            elif caps == True:
                caps = False
            continue

        if input == '`': #'`' is converted back into a space.
            input = ' '

        if input.lower() not in dictionary: #Checking if the user entered an unsupported character.
            return "Sorry, \'{0}\' is not supported.".format(input)

        key = (dictionary.index(input.lower()) + mult) #Converts the input character into its index in the dictionary, and then adds the multiplier to it to convert it to something else.
        key %= len(dictionary) #Ensuring that the index is in the range of the dictionary.

        if change_case == True:
            change_case = False
            buffer += '|'

        if caps == True and type == 'decode': #Converting the character into its key in the dictionary. While decoding, the output letter is uppercase or lowercase according to the caps variable, and while encoding it is random.
            buffer += dictionary[key].upper()
        elif caps == False and type == 'decode':
            buffer += dictionary[key].lower()
        else:
            buffer += random.choice([dictionary[key].upper(), dictionary[key].lower()])

        if '-noprint' not in args: #If "-noprint" argument was added, skip printing conversion.
            print("{0} -> {1} ({2})".format(input, buffer, key))

        output += buffer
        buffer = ''

        offset += 1 #Increasing offset, increasing and flipping multiplier for maximum scrambling.
        if mult > 0:
            mult += offset
        elif mult < 0:
            mult -= offset
        mult *= -1

        #Algorithm end

    if output[(len(output) - 1)] == ' ': #If the last character is a space, it is replaced with '`' so it isn't lost.
        output = output[0:(len(output) - 1)] + '`'

    return output
