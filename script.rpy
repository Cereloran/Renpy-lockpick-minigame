init python:
    import pygame
    import math
    renpy.music.register_channel("Lock_Move", mixer= "sfx", loop=True)
    renpy.music.register_channel("Lock_Click", mixer= "sfx", loop=False, tight=True)

    class Lock(renpy.Displayable):

        #The lock class constructor
        def __init__(self, difficulty, resize=1920, **kwargs):
            super(Lock, self).__init__(**kwargs)

            #These lines are for setting up the images used and the size of them
            self._width = resize
            self._lock_plate_image = Transform("images/lock_plate.png", size = (resize, resize))
            self._lock_cylinder_image = Transform("images/lock_cylinder.png", size = (resize, resize))
            self._lock_tension_image = Transform("images/lock_tension.png", size = (resize, resize))
            self._lock_pick_image = Transform("images/lock_pick.png", size = (resize, resize))
            self._offset = (resize*2**0.5-resize)/2

            #Variables
            self._cylinder_min = 0
            self._cylinder_max = 90
            self._cylinder_rotate = 0 # the current angle of cylinder
            self._cylinder_try_rotate = False #if the cylinder is attempting to rotate
            self._pick_rotate = 90 #where the pick currently is
            self._pick_can_rotate = True
            self._pick_broke = False #if the pick just broke
            self._correct_pos = renpy.random.randint(0,180) #a point between 0 and 180 determined randomly when the lock is created
            self._difficulty = difficulty #a number between 1 and 29 - the lower the number, the more difficult the lock
            self._break_time = (difficulty/10 + 0.75) #a number based on difficulty, the amount of time before the lock pick breaks


        def event(self, ev, x, y, st):
            
            LEFT = 1
            RIGHT = 3

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == LEFT:
                # if holding left mouse button
                self._cylinder_try_rotate = True # the cylinder will try to rotate
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == LEFT:
                # if release left mouse button
                renpy.sound.stop(channel="Lock_Move")
                self._cylinder_try_rotate = False
                self._pick_can_rotate = True
                self._pick_broke = False
                #renpy.hide_screen("lock_picking")

        # Function that continuously updates the graphics of the lock
        def render(self, width, height, st, at):

            if self._pick_can_rotate: 
                #calculating the pick rotate angle based on mouse position              
                mouse_pos = renpy.get_mouse_pos() # current mouse postion
                mouse_on_ox = (mouse_pos[0], 1080/2) # perpendicular of mouse pos on coordinate x axis
                root = (1920/2, 1080/2) # origin of the coordinate

                len_mouse_to_ox = calculate_length(mouse_pos, mouse_on_ox) # calculate the distance from mouse pos to its perpendicular on coordinate x axis
                len_mouse_to_root = calculate_length(mouse_pos, root) # calculate the distance from mouse pos to the origin

                the_angle = calculate_angle(len_mouse_to_ox, len_mouse_to_root)

                if mouse_pos[0] > 1920/2: # if mouse is on the right half of the screen
                    if mouse_pos[1] >= 1080/2: # if mouse if on the lower part of the screen
                        self._pick_rotate = 180 # pick can't rotate further than 180 degree
                    else: # if mouse is on the upper part of the screen (and is on the right half)
                        self._pick_rotate = 180 - the_angle
                elif mouse_pos[0] < 1920/2: # if mouse is on the left part of the screen 
                    if mouse_pos[1] >= 1080/2: # if mouse is on the lower part of the screen
                        self._pick_rotate = 0 # pick can't rotate smaller than 0
                    else: # if the mouse is on the upper part of the screen (and is on the left half)
                        self._pick_rotate = the_angle


                #if the position of the pick is close to the sweet spot, the cylinder can rotate
                if abs(self._pick_rotate - self._correct_pos) < self._difficulty/2:
                #if self._pick_rotate in range((self._correct_pos-(self._difficulty)/2), (self._correct_pos+((self._difficulty)/2)+1)):

                    #if it's "close enough" as determined by the difficulty
                    self._cylinder_max = 90
                else:
                    self._cylinder_max = 90 - abs(self._pick_rotate - self._correct_pos)*(30/self._difficulty)
                    #if it's not close enough, it can still rotate a bit, based on how far away it is
                    if self._cylinder_max <= 0:
                        self._cylinder_max = 0
                
            
            #move the pick
            if self._pick_broke:
                pick = Transform(child=None)
            else:
                pick = Transform(child=self._lock_pick_image, rotate=self._pick_rotate, subpixel=True)    

            #The following is all the render information for Lock and parts
            # Create transform to rotate the moving parts
            if self._cylinder_try_rotate:
                # if the button is down, which mean the player is trying to rotate
                self._cylinder_rotate += (2*st)/(at+1) # start increasing the angle
                # start to rotate the tension and cylinder image, which should have been 1 image only in the very beginning
                cylinder = Transform(child=self._lock_cylinder_image, rotate=self._cylinder_rotate, subpixel=True)
                tension = Transform(child=self._lock_tension_image, rotate=self._cylinder_rotate, subpixel=True)

                #it can only rotate up to self.cylinder_max
                if self._cylinder_rotate > self._cylinder_max:
                    self._cylinder_rotate = self._cylinder_max

                # if it gets to 90, you win
                if self._cylinder_rotate == 90:
                    # play the sound and display notify of victory
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
                    #jiggle when it gets to self.cylinder_max
                    if not renpy.sound.is_playing: # if not already playing the lock moving sound
                        renpy.sound.play("audio/lock_moving.mp3", channel="Lock_Move")

                    jiggle_cylinder = self._cylinder_rotate + renpy.random.randint(-2,2)
                    jiggle_tension = self._cylinder_rotate + renpy.random.randint(-3,3)
                    cylinder = Transform(child=self._lock_cylinder_image, subpixel=True, rotate=jiggle_cylinder)
                    tension = Transform(child=self._lock_tension_image, subpixel=True, rotate=jiggle_tension)

                    self.pick_can_rotate = False

                    global lockpicks
                    #if a timer here exceeds self.breakage, break a lock pick (play a sound and hide the image momentarily), reset its position, decrement number of lockpicks
                    global set_timers
                    global timers
                    if not set_timers:
                        timers = at
                        set_timers = True

                    if set_timers:
                        if at > timers+self._break_time:
                            # play the sound of failure
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

            else: #release, go back to the starting position
                if self._cylinder_rotate > 15:
                    renpy.sound.play("audio/lock_moving_back.mp3", channel="Lock_Click")
                self._pick_can_rotate = True
                self._cylinder_rotate -= (5*st)/(at+1)

                if self._cylinder_rotate < self._cylinder_min:
                    self._cylinder_rotate = self._cylinder_min
                    renpy.sound.stop(channel="Lock_Click")
                    #global set_timers
                    #global timers
                    #set_timers = False
                    #timers = 0
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
            self._name = name # name can be used to compare if you have the right keys for the right chest
            self._status = status # closed or opened, for image display and tell if you can try to open it again
            self._keys = keys # if you got the keys of the chest, then you can open it without picking
            self._lock = lock # what lock you're using
            self._reward = [] # a list of reward
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

    class Item():
        def __init__(self, name, info):
            self._name = name 
            self._info = info 

        @property
        def name(self):
            return self._name 
        
        @property
        def info(self):
            return self._info
    
    class Key():
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
        # sin is the best solution because it can calculate the angle without errors on 90 degree
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
                            difficulty_display = "hard"
                        elif chest.lock._difficulty in range(5, 15):
                            difficulty_display = "medium"
                        elif chest.lock._difficulty in range(15, 30):
                            difficulty_display = "easy"
                        elif chest.lock._difficulty >= 30:
                            difficulty_display = "invalid"
                    text "Difficulty: {}".format(difficulty_display)
                        
                    textbutton "Open" action If(
                        chest.status == "closed",
                        true = If(
                            chest.keys,
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
            textbutton "Close" action [Hide("loot"), Jump("start")]
        else:
            text "This chest is empty"
            timer 3.0 action [Hide("loot"), Jump("start")]

screen inventory_icon():
    textbutton "Inventory" action [ShowMenu("inventory"), Hide("chest_display"), Hide("inventory_icon")]

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

default chest_1 = Chest("Chest 1", lock = Lock(10))
default chest_2 = Chest("Chest 2", lock = Lock(15))
default chest_3 = Chest("Chest 3", lock = Lock(20))
default chest_4 = Chest("Chest 4", lock = Lock(25))
default chest_5 = Chest("Chest 5", lock = Lock(29))
# should only go from 1 to 29, if it's above 29 then you can click anywhere to unlock, which i don't know why
default current_chest = None

default inventory = []

label start:
    $ chest_5.reward = [apple, ramen]
    $ chest_list = [chest_1, chest_2, chest_3, chest_4, chest_5]
    show screen inventory_icon
    call screen chest_display(chest_list)
    return
