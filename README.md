# Renpy-lockpick-minigame
## A lockpick minigame made by Renpy
## By Rice Studio 🍙 From VietNam

### About the Minigame
The original idea is from https://lemmasoft.renai.us/forums/viewtopic.php?f=51&t=58049 but it was laggy, the pick position doesn't match with the mouse postion and they used many redundant lines of code in it so i decided to fix it up a bit, changing the formular and some conditions. (They still rock, i just fix the buggy thing)

My code is free for both commercial and non-commercial project **BUT** the lisence and every properties like audios and images belongs to the person (JessicleCat) in the link above, i got nothing to do with that.

### Dev note
Because `config.overlay_screen.append("inventory_icon")` wasn't work for me so the screen code might be a bit clumsy with hiding and showing stuff, but i think you can fix that yourself. The key feature isn't being used and the inventory is just a list right now but i think it'll gonna be fun for you to make it yourself, beside, different people make different type of inventory class so i won't make one.

Ping me on [Zeil Learning discord server](https://discord.gg/BNEMkv3W) (sherlockervn10 or kaodachet) if you need help with understanding the code. This is my first time to public my github repository so sorry if it look messy.

I'll be happy if someone tells me how can i improve my code

### How to download
Your renpy version should be at least 7.4.9 if you don't want weird errors while implementing this

Find the only green button here and click on download zip, or you can open the `script.rpy` file and download audio and images separately

Copy the code to your `script.rpy` file, if you want it to be in another file, make sure you change `init python` to `init -1 python`. This will set the order of the minigame to go first

Place the images in the `images` folder and the audios to the `audio` folder

### How to use
So if you want to use this minigame to your project, delete the screens and variables, make your own.

- Warning: *DO NOT* delete these variable
```python
default lockpicks = 25
default timers = 0
default set_timers = 0
```

First of all you need to create a `Chest` object

```python
default chest_1 = Chest("Chest 1", lock = Lock(10))
```
The `10` in `Lock(10)` is the difficulty you want it to be, the smaller the number is, the harder it is. But remember, the number should *ONLY* be in the range from 1 to 29

Then add a screen that display your chest and do whatever you want there from positioning to the name bla bla (You might want to Ctrl F and search for every lines that have the screen name i made and change it to yours before deleting them)
```python
screen chest_display(chests): # parameter is not a must, you can have it or not
```
Then you might ask: "What if i want to display the chest as an image 🤔?"

Really simple use `imagebutton` to display it through the attribute `name`
```python
screen chest_display():
    imagebutton:
        auto "images/{}_%s.png".format(chest1.name)
        action If(
            chest.status == "closed", # Only allow open when it haven't been opened
            true = If(
                chest.keys, # Just saying if it's not None but in a fancy way
                true = [Hide("chest_display"), Show("loot", True, chest)],
                false = [SetVariable("current_chest", chest), Hide("chest_display"), ShowMenu("lock_picking", chest.lock)]),
            false = Notify("Chest is opened"))
        align (0.5, 0.5)
```
Make sure you have an image named `"Chest 1"` in your `images` folder (or whatever that match the chest's name)

And that's pretty much it, you can add your own inventory system or `Item` class and play around to add rewards to your inventory. Indepth of the minigame is explained detaily in the code's comment.

### Bugs
- The lockpick can be minus right now, can be fixed by something like
```python
if lockpicks <=0:
    lockpicks = 0
```
- Inventory button can be overlayed 

Good luck with making your own game.
