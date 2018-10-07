#Core function of ComplexCipher.
VERSION = '1.5.0'

def convert(text, type): #Main function.
    import random
    dictionary = ['0' , '!' , 'a' , 'b' , '1' , 'c' , 'd' , '2' , 'e' , '(' , 'f' , ',' , 'g' , '/' , 'h' , '3' , 'i' , 'j' , '.' , 'k' , 'l' , '4' , 'm' , ' ' , 'n' , '5' , 'o' , 'p' , ':' , 'q' , 'r' , '6' , 's' , '-' , 't' , '\'' , 'u' , ')' , 'v' , '7' , 'w' , 'x' , '8' , 'y' , 'z' , '?' , '9']

    text = text.strip() #Setting up requirements for the algorithm.
    buffer = ''
    offset_included = 0
    caps = False
    change_case = False

    if type == 'encode': #Checking whether to encode or decode. If encoding, a random offset is added to the front of the string and used to offset the multiplier, increasing scrambling.
        random.seed()
        randlist = [random.randint(1,9), random.randint(10,99), random.randint(100,999), random.randint(1000,9999), random.randint(10000,99999), random.randint(100000,999999), random.randint(1000000,9999999), random.randint(10000000,99999999), random.randint(100000000,999999999)]
        offset = random.choice(randlist)
        offset_l = len(str(offset))

        mult = 1 * offset
        output = '%s%s' % (str(offset_l),str(offset))

    elif type == 'decode': #If decoding, the initial offset is retrieved from the front of the string and that character is skipped by the algorithm.
        offset_l = int(text[0]) + 1
        offset = int(text[1:(offset_l)])
        offset_included = offset_l

        mult = -1 * offset
        output = ''

    #Algorithm start

    for letter in range(offset_included,len(text)):
        input = text[letter] #Selecting a character.

        if input.isalpha() and type == 'encode':
            if input.isupper() and caps == False:
                caps = True
                change_case = True
            if input.islower() and caps == True:
                caps = False
                change_case = True

        if input == '|':
            if caps == False:
                caps = True
            elif caps == True:
                caps = False
            continue

        if input == '`': #'`' is converted back into a space.
            input = ' '

        if input.lower() not in dictionary: #Checking if the user entered an unsupported character.
            return "Sorry, \'%s\' is not supported." % (input)

        key = (dictionary.index(input.lower()) + mult) #Converts the input character into its index in the dictionary, and then adds the multiplier to it to convert it to something else.
        key %= len(dictionary) #Ensuring that the index is in the range of the dictionary.

        if change_case == True:
            change_case = False
            buffer += '|'

        if caps == True and type == 'decode':
            buffer += dictionary[key].upper()
        elif caps == False and type == 'decode':
            buffer += dictionary[key].lower()
        else:
            buffer += random.choice([dictionary[key].upper(), dictionary[key].lower()])

        output += buffer #Converting the new index to a character and adding it to the output string.
        buffer = ''
        print("%s -> %s (%s)" % (input,dictionary[key],key))

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
