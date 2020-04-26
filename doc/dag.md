# [DAG Module](/tools/python/nuketools/dag.py)
#### About
This is a python module containing a lot of efficiency and convenience tools for interacting with Nuke's **D**irected **A**cyclic **G**raph: utilities for modifying moving and connecting nodes. The thing we do all day as compositors.

#### Shortcuts
I used the meta key a lot in the default shortcuts because it's not mapped to any default shortcuts. The meta key is also known as the "Windows Key" and it's usually next to the alt key on most linux / windows systems. On OSX, the Command key is mapped to Nuke's ctrl, the Option key is alt, and the control key is mapped to meta. 

The shortcuts are all defined at the top of the module and are easy to customize.

**How can you make you're hand do that?!** I use my thumb to press the meta key, and then rotate my thumb right to toggle alt on or off. It's easy to press meta+alt with a thumb on both keys.

I also remap my ctrl key to capslock. It makes my hand hurt less. On linux: `setxkbmap -option ctrl:nocaps`

Here's some documentation on all the things this python module does.

## Properties Panels
![DAG: Properties Panels](/doc/images/dag.properties_panels.gif)

- Disable properties panel open on node creation.
- `a`: Open the properties panels of the selected node(s).
- `alt+a`: Close all properties panels.

I work with floating properties panels. I find it really annoying dealing with the Properties pane. Managing which panels are open and in what order they are in takes up valuable time. Often the Properties pane is full of crap I don't care about. Finding what I do care about is difficult.

So I work with floating properties panels. I can control exactly which panels I have open, and where they are positioned. They only open when I want them open (`a`), and I can easily clear the screen (`alt+a`).


## Move Nodes
![Move Nodes](/doc/images/dag.move_nodes.gif)
- `meta+alt+<arrow>`: Move selected nodes in <arrow> direction: large step
- `meta+alt+shift+<arrow>`: Move selected nodes in <arrow> direction: small step

Moving nodes with the mouse is fiddly and imprecise, especially for large sections of your nuke script. This function is probably the most useful 5 lines of code I've written. It's super simple: It moves the selected nodes in the direction you specify with a keyboard shortcut.


## Snap to Grid
![Snap to Grid](/doc/images/dag.snap_to_grid.gif)
- `alt+s`: Snap selected nodes to the grid. (I've remapped fullscreen to `ctrl+alt+shift+f`)

I have the snap threshold in the preferences relatively low so that nodes don't get "stuck" on the grid. Once I've made a complete mess I'll snap the nodes to the grid with this shortcut.


## Align Nodes
![Align Nodes](/doc/images/dag.align_vertical.gif)
- `ctrl+shift+<arrow>`: Align nodes to selected direction.

Another super useful one for the OCD among us. This tool aligns the selected nodes to the same vertical or horizontal position. For example `ctrl+shift+up` aligns all the nodes to the top-most node. Very useful for keeping things neat and orderly in contact-sheet situations.


## Paste to Selected
![Paste to Selected](/doc/images/dag.paste_to_selected.gif)
- `alt+v`: Paste a copy of clipboard to each selected node.

Super useful for duplicating a copy of something to many nodes.

## Swapper
![Swapper](/doc/images/dag.swap_nodes.gif)
- `shift+x`: Swap inputs or direction
You're probably familiar with the `shift+x` shortcut to swap the inputs of a merge node or other node with multiple inputs. I've extended this functionality to work with more than one selected node, and a variety of other useful nodes.
- Colorspace and OCIOColorspace: swap the input and output colorspaces.
- OCIOFileTransform: swap the direction.
- Any node with an invert or reverse knob: enable or disable it.

## Scale Nodes
![Scale Nodes](/doc/images/dag.scale.gif)
- `meta+=`: Scale up nodes horizontally from the right.
- `meta+-`: Scale down nodes horizontally from the right.
- `meta+shift+=`: Scale up nodes vertically from the bottom.
- `meta+shift+-`: Scale down nodes vertically from the bottom.

We've all been there. You got excited and built a whole setup to do something, only you didn't realize how much space you needed when you started. Now you have spider's nest of nodes with no room for the next thing you need to build. No problem! Make some space by scaling up the nodes.


## Mirror Nodes Horizontally
![Mirror Nodes Horizontally](/doc/images/dag.mirror_horizontal.gif)
- `meta+m`: Mirror nodes horizontally from the right.
- `meta+shift+m`: Mirror nodes horizontally from the left.

Picking up a script from someone who works top to bottom but has all their work flowing from right to left instead of the correct way around? And you're a little OCD about that kind of thing? No problem! Just mirror the nodes.


## Mirror Nodes Vertically
![Mirror Nodes Vertically](/doc/images/dag.mirror_vertical.gif)
- `ctrl+meta+alt+m`: Mirror nodes vertically from the top.
- `ctrl+alt+meta+shift+m`: Mirror nodes vertically from the bottom.

Picking up a script where someone was working from bottom to top and you're a little OCD about that kind of thing? (Or you're in a bad mood and want to make your script upside down before publishing?) No problem! Just mirror the nodes vertically and get things back to normal or completely fuck up someone's day.


## Select Same Vertical Position
![Select Same Vertical Position](/doc/images/dag.select_same_vertical_position.gif)
- `meta+alt+shift+v`: Select all nodes in order from left to right that are in the same vertical position.
- `ctrl+alt+meta+shift+v`: Select all nodes in order from top to bottom that are in the same horizontal position.

You need to make a contact sheet of 100 shots. You have them all ligned up, in the right order from left to right and now you need to connect a contact sheet node to each one. Fortunately you know about the builtin commands **Connect**  and **Connect Backwards**:
- `y`: Connect the first selected node to the other selected nodes in order.
- `shift+y`: Connect the last selected node to each of the other selected nodes in order.

But if you have 100 nodes it's a pain to select each one and make sure you don't mess up the selection order. That's where this tool comes in. 

You can select any node that is aligned vertically press the shortcut and all nodes with the same vertical position will be added to the selection in order from left to right. Now your contactsheet node will connect up in the correct order.


## Connect to Closest
![Connect to Closest](/doc/images/dag.connect_to_closest.gif)
- `meta+shift+y`: Connect selected nodes to closest.
- `meta+shift+alt+y`: Connect closest node to selected.

Again a super simple script but this one has saved my ass a few times. It connects many selected nodes to the node in closest proximity. You can connect the input or the output. Very useful for creting contact sheets of many shots or doing balancegrades.


## Select Upstream
![Select Upstream](/doc/images/dag.select_upstream.gif)
- `alt+meta+shift+u`: Select upstream nodes of selected node(s). 

Sometimes it's useful to see what nodes are dependencies of a specific point in the node graph. That is, at a specific position in the node graph, what nodes are required to compute that location? This includes expression links and hidden input nodes.


## Select Unused Nodes
![Select Unused Nodes](/doc/images/dag.select_unused.gif)
- `ctrl+alt+meta+shift+u`: Select all unused nodes.

Given a selection of one or more nodes, select all nodes that are not part of the tree. This can be useful to clean up a script. If you select the final write node and run this, you can easily see what nodes are not contributing to the final output.

## Select Downstream Nodes
![Select Downstream Nodes](/doc/images/dag.select_downstream2.gif)
- `alt+meta+shift+p`: Select all downstream nodes of selected node(s).

This can be useful to select all nodes that are dependent on the selected nodes. 
![Select Downstream Nodes 2](/doc/images/dag.select_downstream.gif)
It can also be used to see what is downstream of a specific point in a node graph.


## Location Bookmarks
![Location Bookmarks](/doc/images/dag.bookmarks.gif)
- `ctrl+shift+[1-5]` - Set a location bookmark in the nodegraph.
- `ctrl+[1-5]` - Jump to a bookmarked nodegraph location.

If you have a giant node graph it can be useful to set up location bookmarks so that you can quickly jump between different locations in your script. 

This tool is actually just setting up shortcuts for the built-in `nukescripts.bookmarks` function. You can use the `j` shortcut key to search for bookmarks, but I find keyboard shortcuts to be more efficient.

