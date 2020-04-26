# [DAG Module](/tools/python/nuketools/dag.py)
#### About
This is a python module containing a lot of efficiency and convenience tools for interacting with Nuke's **D**irected **A**cyclic **G**raph: utilities for modifying moving and connecting nodes. The thing we do all day as compositors.

#### Shortcuts
I used the meta key a lot in the default shortcuts because it's not mapped to any default shortcuts. The meta key is also known as the "Windows Key" and it's usually next to the alt key on most linux / windows systems. On OSX, the Command key is mapped to Nuke's ctrl, the Option key is alt, and the control key is mapped to meta. 

The shortcuts are all defined at the top of the module and are easy to customize.

**How can you make you're hand do that?!** I use my thumb to press the meta key, and then rotate my thumb right to toggle alt on or off. It's easy to press meta+alt with a thumb on both keys.

I also remap my ctrl key to capslock. It makes my hand hurt less. On linux: `setxkbmap -option ctrl:nocaps`

Okay, here's some documentation on all the things this python module does.

## Properties Panels
![DAG: Properties Panels](/doc/images/dag.properties_panels.gif)

- Disable properties panel open on node creation.
- `a`: Open the properties panels of the selected node(s).
- `alt+a`: Close all properties panels.

I work with floating properties panels. I find it really annoying dealing with the Properties pane. Managing which panels are open and in what order they are in takes up valuable time. Often the Properties pane is full of crap I don't care about. Finding what I do care about is difficult.

So I work with floating properties panels. I can control exactly which panels I have open, and where they are positioned. They only open when I want them open (`a`), and I can easily clear the screen (`alt+a`).


## Move Nodes
![Move Nodes](/doc/images/dag.move_nodes.gif)

- `meta+alt+<arrow>`: move selected nodes in <arrow> direction: large step
- `meta+alt+shift+<arrow>`: move selected nodes in <arrow> direction: small step

Moving nodes with the mouse is fiddly and imprecise, especially for large sections of your nuke script. This function is probably the most useful 5 lines of code I've written. It's super simple: It moves the selected nodes in the direction you specify with a keyboard shortcut.

