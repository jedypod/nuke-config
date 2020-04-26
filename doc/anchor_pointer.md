## Anchor / Pointer
![Anchor / Pointer](/doc/images/dag.anchor_pointer.gif)
- `alt+t`: Create anchor pointer set

#### Context is Key
There are certain circumstances where you need access to one input to a Nuke script in many places.

Maybe you read in a plate, create a denoise, and need to access this denoise precomp in a few different places in your script. One for paint work, one for extraction work, one for a regrain at the end of your comp.

Maybe you have a set of 4 different rotos for different part of your plate, and you are working on an extraction. You need to have access to one roto in 10 different parts of your extraction comp.

One way of working is to duplicate that source multiple times in the script. This is not a procedural way of working and is **bad**. For read nodes it is less efficient, and creates a situation where you have many copies of the same thing in the script that you need to manage. For example if you version up one of your nodes, did you remember to version up the others? Or do you now have 1 that is the right version and two other copies that are an older version? This can get out of hand.

For Rotos especially, duplicating copies around the script is very inneficient, and can quickly slow a script to a crawl. 

#### Do One Thing in One Place
The first and most important rule of efficient comping is **DO ONE THING IN ONE PLACE**.

#### Inspiration
I built the Anchor Pointer system inspired by Adrian Pueyo and Alexey Kuchinski's [Stamps](http://www.nukepedia.com/gizmos/other/stamps) tool. After using it for a while I found it to be too over-engineered and heavy. I wanted something way lighter, simpler, and more efficient. 

I struggled for a while to find a way of automatically reconnecting nodes with hidden inputs when pasting. 

Previously I had been using the [hidden_input_handler.py](https://gist.github.com/jedypod/29187fa8c82bbbf4bf5e), which overrides the built-in cut/copy/paste functions to achieve this. This always bothered me since it's pretty extreme overriding default functions in this way. 

#### A Saga of knobChanged callbacks
Of course there is the obvious solution, which relies on a python knobChanged callback in the node to reconnect itself to it's target. 

Over the years I have optimistically used this approach for many things and every time it ends up in pain and suffering. With production sized Nuke scripts, knobChanged callbacks are always dangerous, especially for nodes that have many copies of each other. 

KnobChanged callbacks cause slow scripts. 

There are workarounds you can use like putting the knobChanged callback on a node inside of a group, so that the callback only fires when the knob in question is changed, instead of every time the node's selection state or node graph position changes. It's still dangerous though.

#### Is there another way?
The onCreate callback might be another option. This only fires when the node is initially created, or is re-created like when you cut and paste the node. Unfortunately there is a bug in Nuke which prevents the 0th input from connecting in an onCreate callback. 

After a whole lot of experimentation I found an interesting hack. There's a special knob `autolabel`. You can put a single line python expression in there to override how the node is displayed in the node graph. Stamps uses this to set the name of the anchor and stamp node to the tag of that set. 

It turns out if you put a python expression in there that executes some code but doesn't return a string, it will still execute. And it executes after the node is created, so you have the ability to control the input connections. And the cool thing is it only executes once when drawing the node in the dag. I've done a couple tests with several hundred copies of a pointer and once they have all loaded it doesn't slow down the script. This is not the case with Stamps.

#### How do you use it?
- `alt+t`: Create an anchor/pointer set on the selected node(s). If there is one selected node, you'll be given a prompt to enter the title. A title will be auto-calculated for you, but you can change it to suite your needs. The pointer and anchor will both be colored the same as your anchor node as well so it's easy to distinguish Roto nodes from Cameras from Reads for example.

![Anchor Node UI](/doc/images/screenshot_anchor_ui.png)

The anchor node is very simple. It's a `NoOp` with a single knob which specifies the title.

![Pointer Node UI](/doc/images/screenshot_pointer_ui.png)

The pointer node connects to the anchor node. It has a few knobs:
- `target`: The name of the node it is anchored to.
- `connect`: Reconnects the input of the pointer to it's anchor. This script is run automatically.
- `zoom`: Zooms the DAG to the anchor node.
- `set target`: Set's the target of this pointer to a different node.

#### Caution
![Anchor Warning Message](/doc/images/screenshot_anchor_warning.png)

If there are more than 5 nodes upstream of the node you are trying to anchor, a warning message will be displayed. 

Generally speaking, you should only anchor an input to your script. A read node, a camera, a geometry, a roto, etc. 

If you are trying to anchor to some location in the middle of your script, you are not working procedurally and you are probably making a horrible mistake which is going to cause paint and suffering to someone. Either you in the near future, or someone else who is taking over your script, or some poor stereo conversion artist who has to figure out your mess later down the line. 

Be cautious!
