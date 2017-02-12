# this just sends the message to the actual overview, that it should open

import os, time

path = "/tmp/mypipe"
if os.path.exists(path):   
    fifo = open("/tmp/mypipe", "w")
    fifo.write("Message from the sender!\n")
    fifo.close()
