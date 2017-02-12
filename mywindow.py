import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
from random import randint
from threading import Thread
from time import sleep
import i3

def do_nothing():
    return

def do_nothing(a, b):
    return

# needed so one can jump to a specific window on button click.
# there are probably way better ways to do this...
class WindowButton():
    def __init__(self, a_id, a_window):
        self.id = a_id
        self.button = Gtk.Button()
        self.window = a_window

    def clicked(self, widget):
        i3.focus(id=self.id)
        self.window._close_window()

# the class that handles the Window
class mywindow:
    def __init__(self):
        #needed because the whole window is running in a seperate thread from the loop that reads the fifo
        Gdk.threads_init()
        GObject.threads_init()
        Thread(target=self._init_helper).start()  

    # the real __init__ that gets started as a new Thread
    def _init_helper(self):
        self.win = Gtk.Window()

        # important for my i3 config. it gets set to fullscreen by that
        self.win.set_role("i3-overview")
        self.win.connect("delete-event", do_nothing)
        self.open = False

        #initial setup for the window components
        self.populate_window()
        Gtk.main()
        
    
    def populate_window(self):
        
        #top-level boxes stacking horizontally
        self.mbox = Gtk.Box(spacing=6, orientation=1)
        self.tree_grid = Gtk.Grid()
        self.tree_grid.override_background_color(0,Gdk.RGBA(0,0,0,1))
        self.mbox.pack_start(self.tree_grid, True, True, 0)
        self.win.add(self.mbox)

        # this adds a big fat exit button to the bottom of the window
        #bbox = Gtk.Box(spacing=6, )
        #exit_but = Gtk.Button(label="exit")
        #exit_but.connect("clicked", self.exit_button_click)
        #bbox.pack_start(exit_but, True, True, 0)
        #self.mbox.pack_end(bbox, True, True, 0)
        
        #this creates the tree of labels/buttons
        self._create_tree()

    def _create_tree(self):
        
        #clean the tree-box from all children
        for child in self.tree_grid.get_children():
            self.tree_grid.remove(child)

        #get the current tree layout
        tree = i3.get_tree()

        # the top level of the trees are the displays
        num_displays = len(tree["nodes"]) - 1 # ignore the __i3 thingy
        display_counter = 0
        for display in tree["nodes"]:
            if "__i3" in display["name"]: # ignores the __i3 thingy. i think it contains the i3bar
                continue
            
            # every display gets his own label on the top
            disp_label = Gtk.Label(label=display["name"])
            disp_label.override_background_color(0, Gdk.RGBA(0.8,0,0,1))
            disp_label.override_color(0, Gdk.RGBA(1,1,1,1))

            display_grid = Gtk.Grid() #every display gets its own grid, so we can present them tidely
            display_grid.override_background_color(0, Gdk.RGBA(0,0,0,1))
            spacer = Gtk.Label(label="Hah")
            spacer.override_background_color(0, Gdk.RGBA(0,0,0,1)) # needed because grids dont support spacing 
            spacer.override_color(0, Gdk.RGBA(0,0,0,1))

            row =  0
            if display_counter > num_displays / 2 - 1:
                row = 1
            line = display_counter % (num_displays / 2)

            self.tree_grid.attach(disp_label, line, row*3, 1 , 1)
            self.tree_grid.attach(display_grid, line, row*3+1, 1 , 1)
            self.tree_grid.attach(spacer, line, row*3 + 2, 1 , 1)

            for cont in display["nodes"]: 
                if "content" == cont["name"]: #each display has content and top/bottom docker. we only want the content
                    ws_counter = 0
                    num_ws = len(cont["nodes"])
                    for workspace in cont["nodes"]:
                        if len(workspace["nodes"]) == 0:
                            continue

                        # every workspace gets his own label on the top
                        label = Gtk.Label()
                        label.set_label(workspace["name"])
                        label.override_color(0,Gdk.RGBA(1,1,1,1))
                        label.override_background_color(0,Gdk.RGBA(0,0.1,0.6,0.6))


                        grid = Gtk.Grid()
                        next_level_box = Gtk.Box(spacing=0, ) # here is the place where the containers/windows get added
                        grid.attach(label,0,0,1,1)
                        grid.attach(next_level_box,0,1,1,1);
                        spacerh = Gtk.Label(label="Hah") # needed because grids dont support spacing
                        spacerv = Gtk.Label(label="Hah") # needed because grids dont support spacing
                        spacerh.override_background_color(0, Gdk.RGBA(0,0,0,1))  
                        spacerv.override_background_color(0, Gdk.RGBA(0,0,0,1))  
                        spacerh.override_color(0, Gdk.RGBA(0,0,0,1))
                        spacerv.override_color(0, Gdk.RGBA(0,0,0,1))

                        # partion the workspaces into three rows (and in my case maximum 3 lines)
                        row =  0
                        if ws_counter > num_ws / 3 - 1:
                            row = 1
                        if ws_counter > (num_ws*2) / 3 - 1:
                            row = 2
                        line = ws_counter % (num_ws / 3)

                        display_grid.attach(grid, line*2, row*2, 1 , 1)
                        display_grid.attach(spacerh, line*2, row*2 + 1, 1 , 1) 
                        display_grid.attach(spacerv, line*2 + 1, row*2, 1 , 1) 
                        self._rec_tree_func(workspace, next_level_box, 0)
                        ws_counter += 1
            display_counter += 1

    def _rec_tree_func(self, root, parent_box, level):
        #decide wether the leave is a container or a window
        for leave in root["nodes"] :
            if len(leave["nodes"]) == 0:
                label = str(leave["name"]).split("-")[-1] # only display the text after the last dash. in most cases the programs name
                button = WindowButton(leave["window"], self)
                button.button.set_label(label)
                button.button.connect("clicked", button.clicked) #jumps to the window and closes the overview
                parent_box.pack_start(button.button, True, True, 0)
                button.button.override_background_color(0,Gdk.RGBA(0,0,0,1))
                button.button.override_color(0,Gdk.RGBA(1,1,1,1))
            else:
                # generating some nice grey tones for the labels for better differentiation
                label = Gtk.Label()
                label.override_color(0,Gdk.RGBA(1,1,1,1))
                r = 0.7 - 0.1*level
                label.override_background_color(0,Gdk.RGBA(r,r,r,1))
                
                if leave["name"]: #sometimes the containers do not have names. defaulting to "container"
                    label.set_label(leave["name"])
                else:
                    label.set_label("container")
                
                grid = Gtk.Grid()
                next_level_box = Gtk.Box(spacing=0, ) # here is the place for the next level of recursion
                grid.attach(label,0,0,1,1)
                grid.attach(next_level_box,0,1,1,1);
                parent_box.pack_start(grid, True, True, 0)
                self._rec_tree_func(leave, next_level_box, level + 1)   # start next level of recursion only if we didnt operate on a window
                                                                        # wouldnt make much of a difference but ya know 
    # not needed anymore. leaving it still
    def exit_button_click(self, button):
        self._close_window()

    #open window from within the thread
    def _open_window(self):
        self._create_tree()
        self.win.show_all()
        self.open = True

    #open window from outside the thread
    def open_window(self):
        Gdk.threads_enter()
        self._open_window()
        Gdk.threads_leave()
    
    #closing window from within the thread
    def _close_window(self):
        self.win.hide()
        self.open = False
    
    #closing window from outside the thread
    def close_window(self):
        Gdk.threads_enter()
        self._close_window()
        Gdk.threads_leave()

    #toggel the window from within the Thread
    def _toggle_window(self):
        if(self.open):
            self._close_window()
        else:
            self._open_window()
        
    #toggel the window from outside the Thread
    def toggle_window(self):
        if(self.open):
            self.close_window()
        else:
            self.open_window()
    
    #exit the Gtk loop
    def exit(self):
        Gtk.main_quit()
