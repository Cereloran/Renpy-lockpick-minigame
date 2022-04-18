init python:
    import pygame
    import math

    renpy.music.register_channel("Lock_Move", mixer= "sfx", loop=True)
    renpy.music.register_channel("Lock_Click", mixer= "sfx", loop=False, tight=True)

    class Lock(renpy.Displayable):

        #The lock class constructor
        def __init__(self, difficulty, resize=1920, **kwargs):
            super(Lock, self).__init__(**kwargs)

            # Set Up images and resize
            self._width = resize
            self._lock_plate_image = Transform("images/lock_plate.png", size = (resize, resize))
            self._lock_cylinder_image = Transform("images/lock_cylinder.png", size = (resize, resize))
            self._lock_tension_image = Transform("images/lock_tension.png", size = (resize, resize))
            self._lock_pick_image = Transform("images/lock_pick.png", size = (resize, resize))
            self._offset = (resize*2**0.5-resize)/2

            # Variables
            self._cylinder_min = 0 # The minimum angle allowed for the cylinder
            self._cylinder_max = 90 # The maximum angle allowed for the cylinder
            self._cylinder_rotate = 0 # The current angle of cylinder
            self._cylinder_try_rotate = False # If the cylinder is attempting to rotate (which mean the left mouse button is held down)
            self._pick_rotate = 90 # The current angle of the pick
            self._pick_can_rotate = True # If the pick can rotate
            self._pick_broke = False # If the pick just broke
            self._correct_pos = renpy.random.randint(0,180) # A point between 0 and 180 determined randomly when the lock is created
            self._difficulty = difficulty # A number between 1 and 29 - the lower the number, the more difficult the lock
            self._break_time = difficulty/10 +0.75 # A number based on difficulty, the amount of time before the lock pick breaks

        # Checking for events
        def event(self, ev, x, y, st):
            
            LEFT = 1
            RIGHT = 3

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == LEFT:
                # If holding left mouse button
                self._cylinder_try_rotate = True # the cylinder will try to rotate
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == LEFT:
                # If release left mouse button
                renpy.sound.stop(channel="Lock_Move")
                self._cylinder_try_rotate = False
                self._pick_can_rotate = True
                self._pick_broke = False

        # Function that continuously updates the graphics of the lock
        def render(self, width, height, st, at):

            if self._pick_can_rotate: 
                # Calculating the pick rotate angle based on mouse position 
                # This is more accurate than the formular on renpy cookbook             
                mouse_pos = renpy.get_mouse_pos() # Current mouse postion
                mouse_on_ox = (mouse_pos[0], 1080/2) # Perpendicular of mouse pos on coordinate x axis
                root = (1920/2, 1080/2) # Origin of the coordinate (but in vietnam we call it root)

                len_mouse_to_ox = calculate_length(mouse_pos, mouse_on_ox) # Calculate the distance from mouse pos to its perpendicular on coordinate x axis
                len_mouse_to_root = calculate_length(mouse_pos, root) # Calculate the distance from mouse pos to the origin
                
                if len_mouse_to_root != 0: # To prevent the weird situation when the player try to put there mouse in the exact middle of the screen, if we just calculate the angle without the condition and that weird situation happen, an error "divide by zero" will raise
                    the_angle = calculate_angle(len_mouse_to_ox, len_mouse_to_root)
                else:
                    the_angle = 0 # Just set it to 0

                if mouse_pos[0] > 1920/2: # If mouse is on the right half of the screen
                    if mouse_pos[1] >= 1080/2: # If mouse if on the lower part of the screen
                        self._pick_rotate = 180 # Pick can't rotate further than 180 degree
                    else: # If mouse is on the upper part of the screen (and is on the right half)
                        self._pick_rotate = 180 - the_angle # Draw the angle on a coordinate system, you will understand why it's 180 - the_angle
                elif mouse_pos[0] < 1920/2: # If mouse is on the left part of the screen 
                    if mouse_pos[1] >= 1080/2: # If mouse is on the lower part of the screen
                        self._pick_rotate = 0 # Pick can't rotate smaller than 0
                    else: # If the mouse is on the upper part of the screen (and is on the left half)
                        self._pick_rotate = the_angle


                # If the position of the pick is close to the correct spot, the cylinder can rotate
                # if self._pick_rotate in range((self._correct_pos-(self._difficulty)/2), (self._correct_pos+((self._difficulty)/2)+1)):
                # The comment above doesn't works but i like to leave it here
                if abs(self._pick_rotate - self._correct_pos) < self._difficulty/2:
                    # If it's "close enough" as determined by the difficulty
                    self._cylinder_max = 90 # Allow winning
                else:
                    self._cylinder_max = 90 - abs(self._pick_rotate - self._correct_pos)*(30/self._difficulty)
                    # If it's not close enough, it can still rotate a bit, based on how far away it is
                    if self._cylinder_max <= 0: # Just in case
                        self._cylinder_max = 0
                
            
            # Move the pick (set up the image rotation)
            if self._pick_broke:
                pick = Transform(child=None)
            else:
                pick = Transform(child=self._lock_pick_image, rotate=self._pick_rotate, subpixel=True)    

            #The following is all the render information for Lock and parts
            # Create transform to rotate the moving parts
            if self._cylinder_try_rotate: # If the button is down, which mean the player is trying to rotate
                
                self._cylinder_rotate += (2*st)/(at+1) # Start increasing the angle
                # Start to rotate the tension and cylinder image, which i think is more easier if they are 1 image only in the very beginning, but i can't draw and i don't own the image so who am i to say right :D
                cylinder = Transform(child=self._lock_cylinder_image, rotate=self._cylinder_rotate, subpixel=True)
                tension = Transform(child=self._lock_tension_image, rotate=self._cylinder_rotate, subpixel=True)

                # It can only rotate up to self.cylinder_max (this prevent line 103 from turning the cylinder to a fidget spinner)
                if self._cylinder_rotate > self._cylinder_max:
                    self._cylinder_rotate = self._cylinder_max

                # If cylinder_rotate gets to 90, you win
                if self._cylinder_rotate == 90:
                    # Play the sound and display notify of victory
                    renpy.sound.stop(channel="Lock_Move") # stop every sound before it
                    renpy.sound.play("audio/lock_unlock.mp3", channel="Lock_Click")
                    renpy.notify("You unlocked the chest!")

                    global timers
                    timers = 0
                    global set_timers
                    set_timers = False

                    self._cylinder_try_rotate = False

                    global current_chest

                    renpy.hide_screen("lock_picking")
                    renpy.show_screen("loot", False, current_chest)

                elif self._cylinder_rotate == self._cylinder_max:
                    # Jiggle jiggle jiggle when it gets to self.cylinder_max (this is checked only if it's not 90 so don't worry that it gonna jiggle for your winning)
                    if not renpy.sound.is_playing: # If not already playing the lock moving sound
                        renpy.sound.play("audio/lock_moving.mp3", channel="Lock_Move")
                    
                    # Setting up image jiggling
                    jiggle_cylinder = self._cylinder_rotate + renpy.random.randint(-2,2)
                    jiggle_tension = self._cylinder_rotate + renpy.random.randint(-3,3)
                    cylinder = Transform(child=self._lock_cylinder_image, subpixel=True, rotate=jiggle_cylinder)
                    tension = Transform(child=self._lock_tension_image, subpixel=True, rotate=jiggle_tension)

                    self.pick_can_rotate = False

                    global lockpicks
                    # If a timer here exceeds self._break_time, break a lock pick (play a sound and hide the image momentarily), reset its position, decrease number of lockpicks
                    global set_timers
                    global timers
                    if not set_timers:
                        timers = at
                        set_timers = True

                    if set_timers:
                        if at > timers+self._break_time:
                            # Play the sound of failure
                            renpy.sound.stop(channel="Lock_Move")
                            renpy.sound.play("audio/lock_pick_break.mp3", channel="Lock_Click")
                            renpy.notify("Broke a lock pick!")

                            mispick = renpy.random.randint(-30, 30)
                            pick = Transform(child=self._lock_pick_image, rotate=self._pick_rotate+(2*mispick), subpixel=True)

                            self._pick_broke = True
                            self._cylinder_try_rotate = False

                            lockpicks -= 1
                            timers = 0
                            set_timers = False
                            pygame.mouse.set_pos([self._width/2, self._width/4])

            else: # Release, slowly rotate back to the starting position
                if self._cylinder_rotate > 15:
                    renpy.sound.play("audio/lock_moving_back.mp3", channel="Lock_Click")
                self._pick_can_rotate = True
                self._cylinder_rotate -= (5*st)/(at+1)

                if self._cylinder_rotate < self._cylinder_min:
                    self._cylinder_rotate = self._cylinder_min
                    renpy.sound.stop(channel="Lock_Click")

                cylinder = Transform(child=self._lock_cylinder_image, rotate=self._cylinder_rotate, subpixel=True)
                tension = Transform(child=self._lock_tension_image, rotate=self._cylinder_rotate, subpixel=True)

            # Create a render for the children.
            lock_plate_render = renpy.render(self._lock_plate_image, width, height, st, at)
            lock_cylinder_render = renpy.render(cylinder, width, height, st, at)
            lock_tension_render = renpy.render(tension, width, height, st, at)
            lock_pick_render = renpy.render(pick, width, height, st, at)

            # Create the render we will return.
            render = renpy.Render(self._width, self._width)

            # Blit (draw) the child's render to our render.
            render.blit(lock_plate_render, (0, 0))
            render.blit(lock_cylinder_render, (-self._offset, -self._offset))
            render.blit(lock_tension_render, (-self._offset, -self._offset))
            render.blit(lock_pick_render, (-self._offset, -self._offset))

            #This makes sure our object redraws itself after it makes changes
            renpy.redraw(self, 0)

            # Return the render.
            return render

    class Chest():
        def __init__(self, name, status = "closed", keys = None, lock = None, reward = None):
            self._name = name # Name can be used to compare if you have the right keys for the right chest
            self._status = status # "closed" or "opened", for image display and tell if you can try to open it again
            self._keys = keys # If you got the keys of the chest, then you can open it without picking
            self._lock = lock # What lock you're using (so that it have different difficulty and random correct_pos)
            self._reward = [] # A list of reward
        @property 
        def name(self):
            return self._name 
        
        @property 
        def status(self):
            return self._status 
        
        @status.setter 
        def status(self, status):
            self._status = status 
        
        @property
        def keys(self):
            return self._keys
        
        @keys.setter 
        def keys(self, keys):
            self._keys = keys
        
        @property
        def lock(self):
            return self._lock 
        
        @property 
        def reward(self):
            return self._reward
        
        @reward.setter 
        def reward(self, reward):
            self._reward = reward

    class Item(): # Well i wanted to make an Item so that i can use Inventory in my project, you can have whatever you want
        def __init__(self, name, info):
            self._name = name 
            self._info = info 

        @property
        def name(self):
            return self._name 
        
        @property
        def info(self):
            return self._info
    
    class Key(): # This make me thinking a lot whether should i make it or not, a class just for the name is too much but strings is not the proper way tho
    # In fact you can create an Object named key that contain a number that match with the chest number by using Item class
        def __init__(self, name):
            self._name = name 
        
        @property
        def name(self):
            return self._name

    def calculate_length(coordinate1, coordinate2):
        # len of a line is square root of (x1-x2)**2 + (y1-y2)**2
        x = float(coordinate1[0]) - float(coordinate2[0])
        y = float(coordinate1[1]) - float(coordinate2[1])
        return math.sqrt(x**2 + y**2)

    def calculate_angle(a, b):
        # sin is the best solution because it can calculate the angle without errors on 90 degree and it's really hard to have b value to 0
        sin_value = float(a)/float(b)
        return math.degrees(math.asin(sin_value))
    
    def pickup(item):
        inventory.append(item)
    
    def remove_item(container, item):
        container.remove(item)

screen chest_display(chests):
    hbox:
        yalign 0.5
        for chest in chests:
            frame:
                xsize 300
                ysize 300
                vbox:
                    text chest.name 
                    text "Status: {}".format(chest.status)
                    python:
                        if chest.lock._difficulty in range(1, 5):
                            difficulty_display = "hard" # Actually insanely hard but whatever
                        elif chest.lock._difficulty in range(5, 10):
                            difficulty_display = "medium"
                        elif chest.lock._difficulty in range(10, 20):
                            difficulty_display = "easy"
                        elif chest.lock._difficulty in range(20, 30):
                            difficulty_display = "for babies"
                        else:
                            difficulty_display = "You can click anywhere with this" # Which i don't think you want it, it's here so that i can demonstrate what gonna happen if you don't listen to me and have difficulty value out of the ramge(1, 30) 
                    text "Difficulty: {}".format(difficulty_display)
                        
                    textbutton "Open" action If(
                        chest.status == "closed",
                        true = If(
                            chest.keys, # Just Saying if it's not None but in a fancy way
                            true = [Hide("chest_display"), Show("loot", True, chest)],
                            false = [SetVariable("current_chest", chest), Hide("chest_display"), ShowMenu("lock_picking", chest.lock)]),
                        false = Notify("Chest is opened"))

screen lock_picking(lock):
    modal True
    add lock:
        xalign 0.5
        yalign 0.5
    text "Lockpicks: [lockpicks]"

screen loot(used_keys, chest):
    if used_keys:
        $ renpy.notify("You used keys")
        $ inventory.remove(chest.keys)
    $ chest.status = "opened"
    $ loots = chest.reward

    vbox:
        align (0.5, 0.5)
        if loots is not None:
            for loot in loots:
                textbutton loot.name action [Function(pickup, loot), Function(remove_item, loots, loot)]
            textbutton "Close" action [Hide("loot"), Jump("start")] # So this make things more realistic, you look at a chest and get to choose what to take out instead of take all of them and then throw away later on
        else:
            text "This chest is empty"
            timer 3.0 action [Hide("loot"), Jump("start")]

screen inventory_icon():
    textbutton "Inventory" action [ShowMenu("inventory"), Hide("chest_display"), Hide("inventory_icon")]
# I got really clumsy with displaying this because it got overlay situation all the time
# But i do this just to display that the reward will go to your inventory so you can add your own

screen inventory():
    vbox:
        for item in inventory:
            text item.name
        textbutton "Return" action [Hide("inventory"), Jump("start")]


default lockpicks = 25
default timers = 0
default set_timers = 0

define apple = Item("Apple", "Adam love it")
define ramen = Item("Ramen", "Naruto's favourite food")

default chest_1 = Chest("Chest 1", lock = Lock(3))
default chest_2 = Chest("Chest 2", lock = Lock(15))
default chest_3 = Chest("Chest 3", lock = Lock(20))
default chest_4 = Chest("Chest 4", lock = Lock(25))
default chest_5 = Chest("Chest 5", lock = Lock(29))
# Should only go from 1 to 29, if it's above 29 then you can click anywhere to unlock, which i don't know why
default current_chest = None

default inventory = []

label start:
    $ chest_5.reward = [apple, ramen]
    $ chest_list = [chest_1, chest_2, chest_3, chest_4, chest_5]
    show screen inventory_icon
    call screen chest_display(chest_list)
    return
