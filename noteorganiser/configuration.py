import sys
import os

def initialise():

    # Platform independent recovery of the home directory
    home = os.path.expanduser("~")
    main = os.path.join(home, '.noteorganiser')
    # Check if the folder ".noteorganiser" exists
    if os.path.isdir(main):
        print main, ' is there!'
    else:
        os.mkdir(main)
        print main, 'was created!'

if __name__ == "__main__":
    initialise()
