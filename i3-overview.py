import os, time
from mywindow import mywindow

win = mywindow()

pipe_path = "/tmp/mypipe"
if not os.path.exists(pipe_path):
    os.mkfifo(pipe_path)

def wait_on_input():
    #need to open / close so often, or else the read wont block after first read :(
    pipe_fd = os.open(pipe_path, os.O_RDONLY) 
    pipe = os.fdopen(pipe_fd)
    message = pipe.read()   
    pipe.close()
    return message

while True:
    message = wait_on_input()
    if message:
        print("Received: '%s'" % message)
        win.toggle_window()
    print("Doing other stuff")
    time.sleep(0.5)