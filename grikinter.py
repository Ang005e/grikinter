import tkinter as tk


############  ############

# PURPOSE OF GRIKINTER
# tkinter's grid system is crap. Why, the HELL, would you make a grid system that is based on THE SIZE OF WIDGETS INSIDE IT??? WTF?? WHATS WRONG WITH YOU?????
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

############  ############


class GridWidget():

    _instances = [] # list of all GridWidget instances
    _hasText = [] # list of all widgets with text

    def __init__(self, startrow, startcolumn, rowspan=1, colspan=1, weight=None):
        
        self.root = self.winfo_toplevel()
        
        self.SetPosition(startrow, startcolumn, rowspan, colspan)
        self.BuildGrid(rowspan, colspan, weight)
        self.GetRootDimensions()

        GridWidget._instances.append(self)
        
        self.after_idle(self.CheckForText) # check the widget for text and mark it for text-wrap operations if needed

        if rowspan > 1 and colspan > 1:
            self.resize() # resize the grid to update positioning
        
    # BuildGrid and __padGrid have been seperated from __configureCells to improve program performance (certain context-based 
    # calculations, i.e. winfo.grid_size() and grid_propogate() are costly, and __padGrid is constantly used in resizing operations).

    # >> BuildGrid creates a grid WITHIN a widget. The position of a widget is set on initilisation (declaration) of the instance.
    # BuildGrid is overridden in the GridTk class so the root grid is measured and marked for resizing operations.
    def BuildGrid(self, rows=0, cols=0):
        self.grid_propagate(False)
        self.__configureCells(padx=None, pady=None, rows=rows, cols=cols, weight=1)

    # >> __padGrid is used solely for grid resizing and cementing operations.
    def __padGrid(self, padx, pady):  
        self.__configureCells(padx=padx, pady=pady, rows=0, cols=0, weight=None)

    # __configureCells configures ALL grid cells to size in a uniform manner, regardless of widget size, contents attempting to enlarge it, 
    # or other normally uncontrollable factors.
    def __configureCells(self, rows, cols, weight, padx, pady): 
        for col in range(cols):
            self.grid_columnconfigure(col, weight=weight, pad=padx)
        for row in range(rows):
            self.grid_rowconfigure(row, weight=weight, pad=pady)

    # SetPosition 
    def SetPosition(self, startrow, startcolumn, rowspan, colspan):
        self.grid(row=startrow, column=startcolumn, rowspan=rowspan, columnspan=colspan, sticky="nesw")

    def SetPositionRelative(self, sibling, x_offset, y_offset, span_x=1, span_y=1):
        info = sibling.grid_info()
        x = info.get('row', None)
        y = info.get('column', None)
        self.grid(row=x+x_offset, column=y+y_offset, rowspan=span_y, columnspan=span_x)

    def PopulateGrid(self, rowCount, colCount, startrow=0, colStart=0):
        multiplier = 0
        for row in range(rowCount):
            for col in range(colCount):
                multiplier += 1
                if multiplier > 17:
                    multiplier = 0
                colour = f'#{multiplier * 15:02x}{multiplier * 15:02x}00'
                elem = tk.Label(self, bg=colour)
                elem.grid(column=col+colStart, row=row+startrow, sticky="nesw")
    
    def GetRootDimensions(self):# get the cell size of root widget
            root = self.root
            #except AttributeError: return
            gridsize = root.griddimensions
            root.cellwidth = root.winfo_width() / gridsize[0]
            root.cellheight = root.winfo_height() / gridsize[1] 

    def resize(self): #resizing magic
        self.GetRootDimensions() # (widget can also be root)
        for instance in self._instances: # for each widget:
            if instance.grid_size()[0] > 0: # if it has a grid:
                instance.__padGrid(padx=self.root.cellwidth, pady=self.root.cellheight) # pad it out to prevent squishing

    def CheckForText(self):
        try:
            if self.cget("text") != ''  or self.cget("textvariable") != None:
                try: fontsize = self.cget("font").split()[1]
                except IndexError: return
                textlength = len(self.cget("text"))
                if textlength != 0:
                    GridWidget._hasText.append(self)
                    self.textlength = textlength
                    self.fontsize = int(fontsize)
        except tk.TclError:
            return # no text attribute

    def WrapText(self):
        width = self.winfo_width()
        fontsize = self.fontsize
        textlength = self.textlength
        if width < (fontsize*textlength)*2:
            height = self.winfo_height()
            if height > fontsize*3:
                self.config(wraplength=width)


class GridTk(tk.Tk, GridWidget):

    def __init__(self, title, width, height):

        tk.Tk.__init__(self)
        # GridWidget constructor is not called here as the function it provides in not needed for the root widget

        self.width = width
        self.height = height
        self.griddimensions = 0, 0
        self.root = self

        self.title(title)
        self.geometry(f"{self.width}x{self.height}")

        self.after_idle(self.root.bind_class, 'Tk', '<Expose>', lambda event: self.OnResize()) # bind resize event after load completes
        print(f"new parent form created: {title}. Size: {width}x{height}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(root_title={self.title}, root_width={self.width}, root_height={self.height})"
    

    def BuildGrid(self, rows=0, cols=0, weight=1):
        super().BuildGrid(rows, cols, weight)
        self.griddimensions = self.root.grid_size() # gets root grid dimensions

    def OnResize(self):

        self.root.resize() # resize each grid cell uniformly, even if empty

        for instance in GridWidget._hasText: 
            instance.WrapText() # gracefully manage text wrapping, including height calculations and overflow


# Used to contain grid items and maintain grid sizing relative to the window dimensions
class GridLabelframe(tk.LabelFrame, GridWidget):

    _lblFrameInstances = []

    def __init__(self, master, startrow, startcolumn, rowspan, colspan, weight=None, gridTest=False, **kwargs):
        super().__init__(master, **kwargs)
        GridLabelframe._lblFrameInstances.append(self)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, colspan, weight)
        if gridTest is True:
            self.PopulateGrid(rowspan, colspan)


class GridButton(tk.Button, GridWidget):
    def __init__(self, master, startrow, startcolumn, rowspan, columnspan, weight=None, **kwargs):
        super().__init__(master, **kwargs)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, columnspan, weight)

class GridLabel(tk.Label, GridWidget):
    def __init__(self, master, startrow, startcolumn, rowspan, columnspan, weight=None, **kwargs):
        super().__init__(master, **kwargs)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, columnspan, weight)

class GridEntry(tk.Entry, GridWidget):
    def __init__(self, master, startrow, startcolumn, rowspan, columnspan, weight=None, **kwargs):
        super().__init__(master, **kwargs)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, columnspan, weight)

class GridRadiobutton(tk.Radiobutton, GridWidget):
    def __init__(self, master, startrow, startcolumn, rowspan, columnspan, weight=None, **kwargs):
        super().__init__(master, **kwargs)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, columnspan, weight)

class GridListbox(tk.Listbox, GridWidget):
    def __init__(self, master, startrow, startcolumn, rowspan, columnspan, weight=None, **kwargs):
        super().__init__(master, **kwargs)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, columnspan, weight)

class GridOptionMenu(tk.OptionMenu, GridWidget):
    def __init__(self, master, startrow, startcolumn, rowspan, columnspan, weight=None, **kwargs):
        super().__init__(master, **kwargs)
        GridWidget.__init__(self, startrow, startcolumn, rowspan, columnspan, weight)
