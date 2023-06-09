import sys
import os
import gettext
from tkinter import messagebox


class Error:
    def __init__(self):
        if getattr(sys, "frozen", False):
            application_path_temp = sys._MEIPASS
        else:
            application_path_temp = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), ".."
            )
        self.message_types = []
        self.message_types.append("Error")
        self.message_types.append("Warning")
        self.message_types.append("Message")
        self.message_types.append("Confirm")
        self.message_quit = "Application will quit."
        self.message_stop = "Detection will stop."

    def display_messagebox(self, t, m):
        m = self._(m)
        match t:
            case 0:
                messagebox.showerror(title=self.message_types[t], message=m)
            case 1:
                messagebox.showwarning(title=self.message_types[t], message=m)
            case 2:
                messagebox.showinfo(title=self.message_types[t], message=m)
            case 3:
                messagebox.askokcancel(title=self.message_types[t], message=m)

    def display_messagebox_stop(self, t, m):
        m = self._(m)
        match t:
            case 0:
                messagebox.showerror(
                    title=self.message_types[t], message=m + "\n" + self.message_stop
                )
            case 1:
                messagebox.showwarning(
                    title=self.message_types[t], message=m + "\n" + self.message_stop
                )
            case 2:
                messagebox.showinfo(
                    title=self.message_types[t], message=m + "\n" + self.message_stop
                )
            case 3:
                messagebox.askokcancel(
                    title=self.message_types[t], message=m + "\n" + self.message_stop
                )

    def display_messagebox_quit(self, t, m):
        match t:
            case 0:
                messagebox.showerror(
                    title=self.message_types[t], message=m + "\n" + self.message_quit
                )
            case 1:
                messagebox.showwarning(
                    title=self.message_types[t], message=m + "\n" + self.message_quit
                )
            case 2:
                messagebox.showinfo(
                    title=self.message_types[t], message=m + "\n" + self.message_quit
                )
            case 3:
                messagebox.askokcancel(
                    title=self.message_types[t], message=m + "\n" + self.message_quit
                )
        sys.exit()


class CameraEmptyFrame(Exception):
    def __init__(self):
        type = 1
        message = "Camera frame is empty."
        Error.display_messagebox(Error(), type, message)


class VideoCaptureError(Exception):
    def __init__(self):
        type = 0
        message = "Unable to capture frame.\nPlease check camera connection."
        Error.display_messagebox_quit(Error(), type, message)


class PermissionDenied(Exception):
    def __init__(self):
        type = 1
        message = "Permission denied\nchange save directory"
        Error.display_messagebox(Error(), type, message)


class TomlDecodeError(Exception):
    def __init__(self):
        type = 0
        message = "Config file decoding error"
        Error.display_messagebox_quit(Error(), type, message)


class UnknownTheme(Exception):
    def __init__(self):
        type = 1
        message = "Unknown theme\nswitching to default theme"
        Error.display_messagebox(Error(), type, message)


class NoConfig(Exception):
    def __init__(self):
        type = 0
        message = "No config file"
        Error.display_messagebox_quit(Error(), type, message)


class ConfigWrongFormat(Exception):
    def __init__(self):
        type = 0
        message = "Wrong format of config file"
        Error.display_messagebox_quit(Error(), type, message)
