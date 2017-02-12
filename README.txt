Installation:
	not yet supported. But you could just put it into your i3 config location

Usage:
	start the myoverview.py once. It will run in the background until killed.
	start the notifier.py to raise and hide the window (i have it binded to mod+y, thats how I intended to use it)
	
	If you want to set it fullscreen in your i3 config: for_window[class="i3-overview"] fullscreen enable   
	
	closing it by killing it via i3 (mod+shift+q or whatever you have it binded to) will cause a crash.
	use the notifier call to close(hide) it or kill the whole python process, if you want to get rid of it.
dependencies:
	For easier calls to i3: https://github.com/ziberna/i3-py
	For the GUI Pythons GTK3+: http://python-gtk-3-tutorial.readthedocs.io/en/latest/install.html
