Pyside
======




Deleting all items in a layout
------------------------------
# layout, widget, clear

*05/09/2014*

When refreshing a widget/frame/layout, and want to erase all previous things on
the frame, it is good to have a high level layout, set initially, to which you
add things. You will then be deleting layouts and widgets out of this global
layout, with the following two methods:

~~~ python
    def clearUI(self):
        while self.layout().count():
            item = self.layout().takeAt(0)
            if isinstance(item, QtGui.QLayout):
                self.clearLayout(item)
                item.deleteLater()
            else:
                try:
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                except AttributeError:
                    pass

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
~~~

There are perharps more efficient ways to go, but this one works well. To
refresh a page, simply call `self.clearUI(); self.initUI()`.


Disabling buttons
-----------------
# button, disable, scroll

*08/09/2014*

When disabling a QPushButton, with `button.setDisabled(True)`, any scrolling
behaviour associated with it will not work any more. You should use
`button.setFlat(True)` to obtain the desired behaviour.
