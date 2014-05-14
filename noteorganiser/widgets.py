import wx


class ExampleFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        panel = wx.Panel(self)
        self.quote = wx.StaticText(panel, label="Your quote: ", pos=(20, 30))
        self.Show()


class WelcomeFrame(wx.Frame):
    """ The notebooks will be stored and displayed there """

    def __init__(self, parent):
        """ Create the basic layout """
        wx.Frame.__init__(self, parent)
        self.panel = wx.Panel(self)

    def initialise_notebooks(self, notebook_list):
        """ Create a small icon for every notebook in the list """
        pass


class NotebookCover(wx.Frame):
    """
    Display of the notebooks as a real notebook, with a method to open it
    """
    pass


if __name__ == "__main__":
    app = wx.App(False)
    ExampleFrame(None)
    app.MainLoop()
