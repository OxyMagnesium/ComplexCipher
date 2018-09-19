#UI for running ComplexCipher locally.
from complexciphercore import convert

print("Welcome to ComplexCipher v1.4.1 by Om Gupta!")

quit_wish = "Y"

while quit_wish == "Y":
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

  while True:
    quit_wish = input("Do you want to continue? (Y/N): ").upper()
    if quit_wish == "Y" or quit_wish == "N":
      break
    else:
      print("")
      print("Sorry, that doesn't make sense.")

print("")

end_stop = input("Press enter to quit.")
