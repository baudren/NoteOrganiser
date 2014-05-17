import sys
import widgets
import wx


class NoteOrganiser(wx.Frame):

    def __init__(self, parent, system_id,  title):
        wx.Frame.__init__(self, parent=parent, id=system_id,
                          title=title)
        self.initUI()

    def initUI(self):

        self.init_menu()
        self.init_panels()

        self.Show(True)

    def init_menu(self):

        # Create the menu bar
        menubar = wx.MenuBar()

        # file menu
        fileMenu = wx.Menu()
        ## Quit
        quit = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, quit)
        ## Add the file menu to the menu bar
        menubar.Append(fileMenu, '&File')

        # info menu
        infoMenu = wx.Menu()
        ## About
        about = infoMenu.Append(wx.ID_ABOUT, 'About',
                               'Information on the application')
        self.Bind(wx.EVT_MENU, self.OnAbout, about)
        ## Add the info menu to the menu bar
        menubar.Append(infoMenu, '&Info')

        # Add the menu bar to the application
        self.SetMenuBar(menubar)

    def init_panels(self):
        pass

    def OnQuit(self, e):
        self.Close()

    def OnAbout(self, e):
        self.Close()


def main(args):
    if len(args) < 2:
        print "You should specify a configuration file"
        return

    conf_file = args[1]
    print conf_file
    app = wx.App()
    NoteOrganiser(None, wx.ID_ANY, 'Note Organiser')
    app.MainLoop()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
