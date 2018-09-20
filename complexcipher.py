#UI for running ComplexCipher locally.
from complexciphercore import convert

print("Welcome to ComplexCipher v1.4.1 by Om Gupta!")

while True:
  while True:
    type = (input("Enter function to be performed. (Encode/Decode): ").lower()).strip()
    if type == "encode" or type == "decode" or type == "e" or type == "d":
      break
    else:
      print("")
      print("Sorry, that doesn't make sense.")

  print("")

  print("Special characters except (!), (?), (.), (:), (,) and (') are not supported.")
  text = input("Enter text to be %sd: " % type)

  print("")

  print("Output:")
  print(convert(text,type))

  print("")
