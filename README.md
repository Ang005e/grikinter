grikinter. a small project made to play with python OOP, and make grids in tkinter cleaner to use.

# PURPOSE OF GRIKINTER
# tkinter's grid system is crap. Why, the HECK, would you make a grid system that is based on THE SIZE OF WIDGETS INSIDE IT??? WTF?? WHATS WRONG WITH YOU PEOPLE???????
# I made this library to provide a quick'n easy way to design and lay out grids, all the while without 
# having to worry about the application window resizing, or grid items shuffling themselves around in funky and unpredictable ways.
# This way, set ratios can very easily be created and maintained for screen layout.
# Essentially, make tkinter grid easier to use, more predictable, and much more controllable. 
# Grikinter allows you to:
# >> Position a grid item on initialisation (i.e. gk.GridButton(row, col, rowspan, colspan)).
# >> Easily set grids WITHIN certain widgets (i.e. GridLabelFrame.BuildGrid(rows, columns)).
# >> Control grid items within THOSE grids, seamlessly
# >> Customise sizing (i.e., change weight to make some rows/columns size faster than others)
# >> Seamlessly control text-wrap without pushing other grid items out of alignment


note: venv included in commit.
