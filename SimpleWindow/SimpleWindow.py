from ctypes import Structure, c_int32, c_int16, c_int, windll, sizeof, byref
import win32gui, win32con
import ctypes
import numpy
import glfw
import cv2
import os

class BITMAPINFO(Structure):
    _fields_ = [
        ("biSize", c_int32),
        ("biWidth", c_int32),
        ("biHeight", c_int32),
        ("biPlanes", c_int16),
        ("biBitCount", c_int16),
        ("biCompression", c_int32),
        ("biSizeImage", c_int32),
        ("biXPelsPerMeter", c_int32),
        ("biYPelsPerMeter", c_int32),
        ("biClrUsed", c_int32),
        ("biClrImportant", c_int32)
    ]

    def __init__(self, width, height, planes=1, bpp=24):
        self.biSize = sizeof(self)
        self.biWidth = width
        self.biHeight = height
        self.biPlanes = planes
        self.biBitCount = bpp
        self.biCompression = 0
        self.biSizeImage = width * height * (bpp // 8)
        self.biXPelsPerMeter = 0
        self.biYPelsPerMeter = 0
        self.biClrUsed = 0
        self.biClrImportant = 0


WINDOWS = {}


def Initialize(Name="", Size=(None, None), Position=(None, None), TitleBarColor=(0, 0, 0), Resizable=True, TopMost=False, Undestroyable=False, Icon=""):
    """
    Initialize a window with the specified parameters. The window will not be shown until Show() is called.

    Parameters
    ----------
    Name : str
        The name identifier for the window.
    Size : tuple of (int, int)
        The size (width, height) of the window. If None, default values will be used.
    Position : tuple of (int, int)
        The position (x, y) of the window on the screen. If None, defaults will be used.
    TitleBarColor : tuple of (int, int, int)
        The RGB color of the window's title bar.
    Resizable : bool
        If True, the window can be resized.
    TopMost : bool
        If True, the window will stay on top of other windows.
    Undestroyable : bool
        If True, the window will be recreated if closed.
    Icon : str
        Path to the icon file for the window. Must be a .ico file.

    Returns
    -------
    None
    """
    WINDOWS[Name] = {"Size": Size, "Position": Position, "TitleBarColor": TitleBarColor, "Resizable": Resizable, "TopMost": TopMost, "Undestroyable": Undestroyable, "Icon": Icon, "Created": False, "Window": None}


def CreateWindow(Name=""):
    """
    Creates a window based on the parameters specified in Initialize().

    This function is not meant to be called manually. It is called internally by Show().

    Parameters
    ----------
    Name : str
        The name of the window to create.

    Returns
    -------
    None
    """
    Size = WINDOWS[Name]["Size"]
    Position = WINDOWS[Name]["Position"]
    TitleBarColor = WINDOWS[Name]["TitleBarColor"]
    Resizable = WINDOWS[Name]["Resizable"]
    TopMost = WINDOWS[Name]["TopMost"]
    Icon = WINDOWS[Name]["Icon"]

    glfw.init()

    if Size[0] is None:
        Size = 150, Size[1]
    if Size[1] is None:
        Size = Size[0], 50

    if Position[0] is None:
        Position = 0, Position[1]
    if Position[1] is None:
        Position = Position[0], 0

    WINDOWS[Name]["Size"] = Size
    WINDOWS[Name]["Position"] = Position

    Window = glfw.create_window(Size[0], Size[1], Name, None, None)
    glfw.make_context_current(Window)

    if Resizable is False:
        glfw.set_window_attrib(Window, glfw.RESIZABLE, glfw.FALSE)

    if TopMost:
        glfw.set_window_attrib(Window, glfw.FLOATING, glfw.TRUE)

    glfw.set_window_pos(Window, Position[0], Position[1])

    Frame = numpy.zeros((Size[1], Size[0], 3), dtype=numpy.uint8)
    Frame[:] = TitleBarColor
    WindowHeight, WindowWidth, Channels = Frame.shape

    HWND = win32gui.FindWindow(None, Name)
    windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((TitleBarColor[0] << 16) | (TitleBarColor[1] << 8) | TitleBarColor[2])), sizeof(c_int))
    Icon = Icon.replace("\\", "/")
    if os.path.exists(Icon) and Icon.endswith(".ico"):
        IconHandle = win32gui.LoadImage(None, Icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, IconHandle)
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, IconHandle)

    WINDOWS[Name]["Created"] = True
    WINDOWS[Name]["Window"] = Window


def GetWindowSize(Name=""):
    """
    Retrieve the size of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    tuple of (int, int)
        The current width and height of the window.
    """
    if WINDOWS[Name]["Created"]:
        HWND = win32gui.FindWindow(None, Name)
        if HWND is None:
            Close(Name)
            return WINDOWS[Name]["Size"]
        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
        return BottomRight[0] - TopLeft[0], BottomRight[1] - TopLeft[1]
    return WINDOWS[Name]["Size"]


def SetWindowSize(Name="", Size=(None, None)):
    """
    Set the size of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    Size : tuple of (int, int)
        The new size (width, height) of the window.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Size"] is not Size and WINDOWS[Name]["Created"]:
        if Size[0] is None:
            Size = (WINDOWS[Name]["Size"][0], Size[1])
        if Size[1] is None:
            Size = (Size[0], WINDOWS[Name]["Size"][1])
        Size = max(150, round(Size[0])), max(50, round(Size[1]))
        WINDOWS[Name]["Size"] = Size
        glfw.set_window_size(WINDOWS[Name]["Window"], Size[0], Size[1])


def GetWindowPosition(Name=""):
    """
    Get the current position of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    tuple of (int, int)
        The (x, y) coordinates of the window's top-left corner.
    """
    if WINDOWS[Name]["Created"]:
        HWND = win32gui.FindWindow(None, Name)
        if HWND is None:
            Close(Name)
            return WINDOWS[Name]["Position"]
        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        return TopLeft[0], TopLeft[1]
    return WINDOWS[Name]["Position"]


def SetWindowPosition(Name="", Position=(None, None)):
    """
    Set the position of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    Position : tuple of (int, int)
        The new (x, y) position of the window.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Position"] is not Position and WINDOWS[Name]["Created"]:
        if Position[0] is None:
            Position = (WINDOWS[Name]["Position"][0], Position[1])
        if Position[1] is None:
            Position = (Position[0], WINDOWS[Name]["Position"][1])
        Position = round(Position[0]), round(Position[1])
        WINDOWS[Name]["Position"] = Position
        glfw.set_window_pos(WINDOWS[Name]["Window"], Position[0], Position[1])


def SetTitleBarColor(Name="", TitleBarColor=(0, 0, 0)):
    """
    Set the title bar color of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    TitleBarColor : tuple of (int, int, int)
        The RGB color to set for the title bar.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["TitleBarColor"] is not TitleBarColor and WINDOWS[Name]["Created"]:
        WINDOWS[Name]["TitleBarColor"] = TitleBarColor
        HWND = win32gui.FindWindow(None, Name)
        windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((max(0, min(255, round(TitleBarColor[0]))) << 16) | (max(0, min(255, round(TitleBarColor[1]))) << 8) | max(0, min(255, round(TitleBarColor[2]))))), sizeof(c_int))


def SetResizable(Name="", Resizable=True):
    """
    Set the resizable property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    Resizable : bool
        If True, the window will be resizable.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Resizable"] is not Resizable:
        WINDOWS[Name]["Resizable"] = Resizable is True
        Close(Name)
        Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Icon=WINDOWS[Name]["Icon"])


def SetTopMost(Name="", TopMost=True):
    """
    Set the window to always stay on top.

    Parameters
    ----------
    Name : str
        The name of the window.
    TopMost : bool
        If True, the window will be kept on top of others.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["TopMost"] is not TopMost:
        WINDOWS[Name]["TopMost"] = TopMost is True
        Close(Name)
        Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Icon=WINDOWS[Name]["Icon"])


def SetIcon(Name="", Icon=""):
    """
    Set the icon of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    Icon : str
        The path to the icon file (must be a .ico file).

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Icon"] is not Icon and WINDOWS[Name]["Created"]:
        WINDOWS[Name]["Icon"] = Icon
        HWND = win32gui.FindWindow(None, Name)
        Icon = Icon.replace("\\", "/")
        if os.path.exists(Icon) and Icon.endswith(".ico"):
            IconHandle = win32gui.LoadImage(None, Icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, IconHandle)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, IconHandle)


def GetWindowStatus(Name=""):
    """
    Get the status of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    dict
        A dictionary containing the window's status with the keys:
        - "Open": Indicates the window's state (True if open, False if closed by code, None if closed by the user).
        - "HWND": The window's handle (int).
        - "Foreground": Whether the window is in the foreground (bool).
        - "Iconic": Whether the window is minimized (bool).
    """
    HWND = win32gui.FindWindow(None, Name)
    return {"Open": WINDOWS[Name]["Created"], "HWND": HWND, "Foreground": win32gui.GetForegroundWindow() is HWND, "Iconic": int(win32gui.IsIconic(HWND)) == 0}


def Show(Name="", Frame=None):
    """
    Display the specified window and update its content with the given frame.

    Parameters
    ----------
    Name : str
        The name of the window.
    Frame : numpy.ndarray, optional
        The frame to be displayed in the window. If None, the window will not be updated.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Created"] is False:
        CreateWindow(Name=Name)
    elif WINDOWS[Name]["Created"] is None:
        return
    if glfw.window_should_close(WINDOWS[Name]["Window"]):
        if WINDOWS[Name]["Created"]:
            Close(Name)
        if WINDOWS[Name]["Undestroyable"]:
            Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Undestroyable=WINDOWS[Name]["Undestroyable"], Icon=WINDOWS[Name]["Icon"])
        else:
            WINDOWS[Name]["Created"] = None
            return

    if Frame is not None:
        HWND = win32gui.FindWindow(None, Name)
        if HWND == 0 or HWND is None:
            return
        if int(win32gui.IsIconic(HWND)) == 1:
            return

        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
        SIZE = BottomRight[0] - TopLeft[0], BottomRight[1] - TopLeft[1]

        HDC = win32gui.GetDC(HWND)

        Frame = numpy.flip(Frame, axis=0)
        Frame = cv2.resize(Frame, GetWindowSize(Name))
        Frame = numpy.ascontiguousarray(Frame)

        windll.gdi32.StretchDIBits(HDC, 0, 0, SIZE[0], SIZE[1], 0, 0, SIZE[0], SIZE[1], ctypes.c_void_p(Frame.ctypes.data), ctypes.byref(BITMAPINFO(Frame.shape[1], Frame.shape[0])), win32con.DIB_RGB_COLORS, win32con.SRCCOPY)

        win32gui.ReleaseDC(HWND, HDC)

    glfw.poll_events()


def Close(Name=""):
    """
    Close the window with the specified name and clean up resources.

    Parameters
    ----------
    Name : str
        The name of the window to close.

    Returns
    -------
    None
    """
    glfw.terminate()
    WINDOWS[Name]["Created"] = False