try:
    import fltk
except ImportError:
    raise ImportError(
        "You must install fltk, and its Python bindings to use this software")
import sys


def theCancelButtonCallback(ptr):
    sys.exit(0)

if __name__ == "__main__":
    window = fltk.Fl_Window(100,100,200,90)
    window.label(sys.argv[0])
    button = fltk.Fl_Button(9,20,180,50)
    button.label("Hello World")
    button.callback(theCancelButtonCallback)
    window.end()
    window.show(len(sys.argv), sys.argv)
    fltk.Fl.run()
