# Games Table Edge Cup and Piece Holders

This is the source code for my table edge cup holders. See the Thingiverse post for photos and the final result: https://www.thingiverse.com/thing:4842445

It's all written in Python using SolidPython. This outputs OpenSCAD files, and can then be complied into .STL files for printing.

The main file to review and edit is `table-edge-cup-holder.py`.

The code has "evolved" over time (ie: it's a mess), but hopefully looking at the final product you can figure out what you need to change.

I have configured everything so that corners etc are all very smooth (`fn=300`) - this can lead to some _very_ long compile times using a lot of RAM (about 6GB per model). To render everything at once can take over an hour - so I would suggest just changing the parts you need and rendering them. You can modify the `main` function and comment out the parts you are not changing.

The included `threads.scad` is from https://www.dkprojects.net/openscad-threads/ .
