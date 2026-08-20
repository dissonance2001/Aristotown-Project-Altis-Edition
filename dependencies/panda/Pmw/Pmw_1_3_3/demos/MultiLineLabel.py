from __future__ import absolute_import
title = 'Multi-line label demonstration'

# Import Pmw from this directory tree.
import sys
sys.path[:0] = ['../../..']

import string
import six.moves.tkinter
import Pmw

class Demo:
    def __init__(self, parent):

        frame = six.moves.tkinter.Frame(parent, background = '#eeeeee')
        frame.pack(fill = 'both', expand = 1, padx = 5, pady = 5)

        stickys = ('n', 's', 'e', 'w', 'ns', 'ew', 'ne', 'nw', 'se', 'sw',
                'nsw', 'nse', 'new', 'sew', 'nsew',)

        widgets = []
        row = 0
        column = 0

        # Choose one megawidget class to demonstrate:
        cls = Pmw.EntryField
        # cls = Pmw.Counter
        # cls = Pmw.ComboBox
        # cls = Pmw.LabeledWidget
        # cls = Pmw.MessageBar

        for sticky in stickys:
            dict = {}
            dict['sticky'] = sticky
            dict['labelpos'] = 'w'
            dict['label_text'] = '1\n' + sticky + ':\n3'
            if cls == Pmw.EntryField:
                dict['value'] = sticky
                dict['entry_width'] = 6
            if cls == Pmw.Counter or cls == Pmw.ComboBox:
                dict['entryfield_value'] = sticky
                dict['entry_width'] = 6
            widget = cls(*(frame,), **dict)
            if cls == Pmw.LabeledWidget:
                f = six.moves.tkinter.Button(widget.interior(), text = sticky)
                f.pack(fill = 'both', expand = 1)
            if cls == Pmw.MessageBar:
		widget.message('state', sticky)
	    widget.grid(column=column, row=row, sticky='ew', padx = 10, pady = 5)
	    frame.grid_columnconfigure(column, weight=1)
	    frame.grid_rowconfigure(row, weight=1)

            widgets.append(widget)

            if row < 4:
                row = row + 1
            else:
                row = 0
                column = column + 1

        Pmw.alignlabels(widgets, sticky = 'e')

######################################################################

# Create demo in root window for testing.
if __name__ == '__main__':
    root = six.moves.tkinter.Tk()
    Pmw.initialise(root)
    root.title(title)

    exitButton = six.moves.tkinter.Button(root, text = 'Exit', command = root.destroy)
    exitButton.pack(side = 'bottom')
    widget = Demo(root)
    root.mainloop()
