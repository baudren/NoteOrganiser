import sys
import widgets
import wx


class NoteOrganiser(wx.App):

    def __init__(self, boolean, configuration_file, status):
        wx.App.__init__(self, boolean)
        self.configuration_file = configuration_file
        self.status = status
        self.welcome_frame = widgets.WelcomeFrame(None)
        self.welcome()

    def welcome(self):
        self.welcome_frame.Show()

    def MainLoop(self):
        pass


def main(args):
    assert len(args) > 1, "You choose specify a configuration file"
    conf_file = args[1]
    app = NoteOrganiser(False, conf_file, 'welcome')
    app.MainLoop()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
