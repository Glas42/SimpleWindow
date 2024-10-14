from ctypes import Structure, c_int32, c_int16, c_int, windll, sizeof, byref
import win32gui, win32con
import ctypes
import numpy
import glfw
import cv2
import os


glfw.init()

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
RED = "\033[31m"
NORMAL = "\033[0m"


# MARK: Initialize()
def Initialize(Name="", Size=(None, None), Position=(None, None), TitleBarColor=(0, 0, 0), Resizable=True, TopMost=False, Foreground=True, Minimized=False, Undestroyable=False, Icon="", NoWarnings=False):
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
    Foreground : bool
        If True, the window will be set to the foreground.
    Minimized : bool
        If True, the window will be minimized.
    Undestroyable : bool
        If True, the window will be recreated if closed.
    Icon : str
        Path to the icon file for the window. Must be a .ico file.
    NoWarnings : bool
        If True, no warnings will be printed.

    Returns
    -------
    bool
        True if the window was successfully initialized, False otherwise.
    """
    HWND = win32gui.FindWindow(None, Name)
    if HWND != 0:
        if NoWarnings != True:
            print(RED + f"The window '{Name}' already exists, not creating a new window. ({Name}: {HWND})" + NORMAL)
        return False

    WINDOWS[Name] = {"Size": Size,
                     "Position": Position,
                     "TitleBarColor": TitleBarColor,
                     "Resizable": Resizable,
                     "TopMost": TopMost,
                     "Foreground": Foreground,
                     "Minimized": Minimized,
                     "Undestroyable": Undestroyable,
                     "Icon": Icon,
                     "NoWarnings": NoWarnings,
                     "Open": False,
                     "Window": None}

    return True


# MARK: CreateWindow()
def CreateWindow(Name=""):
    """
    Creates a window based on the parameters specified in Initialize().
    This function is not meant to be called manually. It is called internally by Show() or SetOpen().

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
    Foreground = WINDOWS[Name]["Foreground"]
    Minimized = WINDOWS[Name]["Minimized"]
    Icon = WINDOWS[Name]["Icon"]

    if Size[0] == None:
        Size = 150, Size[1]
    if Size[1] == None:
        Size = Size[0], 50

    if Position[0] == None:
        Position = 0, Position[1]
    if Position[1] == None:
        Position = Position[0], 0

    WINDOWS[Name]["Size"] = Size
    WINDOWS[Name]["Position"] = Position

    Window = glfw.create_window(Size[0], Size[1], Name, None, None)
    glfw.make_context_current(Window)

    if Resizable == False:
        glfw.set_window_attrib(Window, glfw.RESIZABLE, glfw.FALSE)

    if TopMost:
        glfw.set_window_attrib(Window, glfw.FLOATING, glfw.TRUE)

    glfw.set_window_pos(Window, Position[0], Position[1])

    HWND = win32gui.FindWindow(None, Name)
    windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((TitleBarColor[0] << 16) | (TitleBarColor[1] << 8) | TitleBarColor[2])), sizeof(c_int))
    Icon = Icon.replace("\\", "/")
    if os.path.exists(Icon) and Icon.endswith(".ico"):
        IconHandle = win32gui.LoadImage(None, Icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, IconHandle)
        win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, IconHandle)

    WINDOWS[Name]["Open"] = True
    WINDOWS[Name]["Window"] = Window

    if Foreground:
        SetForeground(Name=Name, State=True)

    if Minimized:
        SetMinimized(Name=Name, State=True)


# MARK: Close()
def Close(Name=""):
    """
    Close the specified window.

    Parameters
    ----------
    Name : str
        The name of the window to close.

    Returns
    -------
    None
    """
    try:
        glfw.destroy_window(WINDOWS[Name]["Window"])
    except:
        pass
    WINDOWS[Name]["Open"] = False


# MARK: SetSize()
def SetSize(Name="", Size=(None, None)):
    """
    Set the size of the specified window.
    It is possible to pass None as a value for width or height to keep the size in the dimension the same.

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
    if WINDOWS[Name]["Size"] != Size and WINDOWS[Name]["Open"]:
        if len(Size) != 2:
            if WINDOWS[Name]["NoWarnings"] != True:
                print(RED + "Size must be a tuple of (int, int)." + NORMAL)
            return
        if (type(Size[0]) != int and type(Size[1]) != type(None)) or (type(Size[1]) != int and type(Size[0]) != type(None)):
            if WINDOWS[Name]["NoWarnings"] != True:
                print(RED + "Size must be a tuple of (int, int)." + NORMAL)
            return
        if Size[0] == None:
            Size = (WINDOWS[Name]["Size"][0], Size[1])
        if Size[1] == None:
            Size = (Size[0], WINDOWS[Name]["Size"][1])
        Size = max(150, round(Size[0])), max(50, round(Size[1]))
        WINDOWS[Name]["Size"] = Size
        glfw.set_window_size(WINDOWS[Name]["Window"], Size[0], Size[1])


# MARK: GetSize()
def GetSize(Name=""):
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
    if WINDOWS[Name]["Open"]:
        HWND = win32gui.FindWindow(None, Name)
        if HWND == None:
            Close(Name=Name)
            return WINDOWS[Name]["Size"]
        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
        return BottomRight[0] - TopLeft[0], BottomRight[1] - TopLeft[1]
    return WINDOWS[Name]["Size"]


# MARK: SetPosition()
def SetPosition(Name="", Position=(None, None)):
    """
    Set the position of the specified window.
    It is possible to pass None as a value for x or y to keep the position in the axis the same.

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
    if WINDOWS[Name]["Position"] != Position and WINDOWS[Name]["Open"]:
        if len(Position) != 2:
            if WINDOWS[Name]["NoWarnings"] != True:
                print(RED + "Position must be a tuple of (int, int)." + NORMAL)
            return
        if (type(Position[0]) != int and type(Position[0]) != type(None)) or (type(Position[1]) != int and type(Position[1]) != type(None)):
            if WINDOWS[Name]["NoWarnings"] != True:
                print(RED + "Position must be a tuple of (int, int)." + NORMAL)
            return
        if Position[0] == None:
            Position = (WINDOWS[Name]["Position"][0], Position[1])
        if Position[1] == None:
            Position = (Position[0], WINDOWS[Name]["Position"][1])
        Position = round(Position[0]), round(Position[1])
        WINDOWS[Name]["Position"] = Position
        glfw.set_window_pos(WINDOWS[Name]["Window"], Position[0], Position[1])


# MARK: GetPosition()
def GetPosition(Name=""):
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
    if WINDOWS[Name]["Open"]:
        HWND = win32gui.FindWindow(None, Name)
        if HWND == None:
            Close(Name=Name)
            return WINDOWS[Name]["Position"]
        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        return TopLeft[0], TopLeft[1]
    return WINDOWS[Name]["Position"]


# MARK: SetTitleBarColor()
def SetTitleBarColor(Name="", Color=(0, 0, 0)):
    """
    Set the title bar color of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    Color : tuple of (int, int, int)
        The RGB color to set for the title bar.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["TitleBarColor"] != Color and WINDOWS[Name]["Open"]:
        if len(Color) != 3:
            if WINDOWS[Name]["NoWarnings"] != True:
                print(RED + "TitleBarColor must be a tuple of (int, int, int)." + NORMAL)
            return
        WINDOWS[Name]["TitleBarColor"] = Color
        HWND = win32gui.FindWindow(None, Name)
        windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int((max(0, min(255, round(Color[0]))) << 16) | (max(0, min(255, round(Color[1]))) << 8) | max(0, min(255, round(Color[2]))))), sizeof(c_int))


# MARK: GetTitleBarColor()
def GetTitleBarColor(Name=""):
    """
    Get the title bar color of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    tuple of (int, int, int)
        The RGB color of the title bar.
    """
    return WINDOWS[Name]["TitleBarColor"]


# MARK: SetResizable()
def SetResizable(Name="", State=True):
    """
    Set the resizable property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    State : bool
        If True, the window will be resizable.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Resizable"] != State:
        WINDOWS[Name]["Resizable"] = State == True
        glfw.set_window_attrib(WINDOWS[Name]["Window"], glfw.RESIZABLE, glfw.TRUE if WINDOWS[Name]["Resizable"] else glfw.FALSE)


# MARK: GetResizable()
def GetResizable(Name=""):
    """
    Get the resizable property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    bool
        True if the window is resizable, False otherwise.
    """
    return WINDOWS[Name]["Resizable"]


# MARK: SetTopMost()
def SetTopMost(Name="", State=True):
    """
    Set the window to always stay on top.

    Parameters
    ----------
    Name : str
        The name of the window.
    State : bool
        If True, the window will be kept on top of others.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["TopMost"] != State:
        WINDOWS[Name]["TopMost"] = State == True
        glfw.set_window_attrib(WINDOWS[Name]["Window"], glfw.FLOATING, glfw.TRUE if WINDOWS[Name]["TopMost"] else glfw.FALSE)


# MARK: GetTopMost()
def GetTopMost(Name=""):
    """
    Get the TopMost property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    bool
        True if the window is always on top, False otherwise.
    """
    return WINDOWS[Name]["TopMost"]


# MARK: SetForeground()
def SetForeground(Name="", State=True):
    """
    Set the window to the foreground.
    The TopMost property will be ignored when moving to the background, but not when moving to the foreground.

    Parameters
    ----------
    Name : str
        The name of the window.
    State : bool
        True to set the window to the foreground, False to set it to the background.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Open"] == True:
        WINDOWS[Name]["Foreground"] = State == True
        HWND = win32gui.FindWindow(None, Name)
        if State == True:
            win32gui.SetWindowPos(HWND, win32con.HWND_TOPMOST if WINDOWS[Name]["TopMost"] == True else win32con.HWND_TOP, GetSize(Name=Name)[0], GetSize(Name=Name)[1], 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        elif State == False:
            win32gui.SetWindowPos(HWND, win32con.HWND_BOTTOM, GetSize(Name=Name)[0], GetSize(Name=Name)[1], 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


# MARK: GetForeground()
def GetForeground(Name=""):
    """
    Get the window's foreground state.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    bool
        True if the window is in the foreground, False otherwise.
    """
    if WINDOWS[Name]["Open"] == True:
        HWND = win32gui.FindWindow(None, Name)
        return HWND == win32gui.GetForegroundWindow()
    return False


# MARK: SetMinimized()
def SetMinimized(Name="", State=False):
    """
    Set the minimized property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    State : bool
        True to minimize the window, False to restore it.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Open"]:
        WINDOWS[Name]["Minimized"] = State == True
        HWND = win32gui.FindWindow(None, Name)
        win32gui.ShowWindow(HWND, win32con.SW_MINIMIZE if State else win32con.SW_RESTORE)


# MARK: GetMinimized()
def GetMinimized(Name=""):
    """
    Get the minimized property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    bool
        True if the window is minimized, False otherwise.
    """
    if WINDOWS[Name]["Open"]:
        HWND = win32gui.FindWindow(None, Name)
        return int(win32gui.IsIconic(HWND)) == 1


# MARK: SetUndestroyable()
def SetUndestroyable(Name="", State=True):
    """
    Set the undestroyable property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    State : bool
        True if the window should be undestroyable, False otherwise.

    Returns
    -------
    None
    """
    if WINDOWS[Name]["Undestroyable"] != State:
        WINDOWS[Name]["Undestroyable"] = State == True


# MARK: GetUndestroyable()
def GetUndestroyable(Name=""):
    """
    Get the undestroyable property of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    bool
        True if the window is undestroyable, False otherwise.
    """
    return WINDOWS[Name]["Undestroyable"] == True


# MARK: SetIcon()
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
    if WINDOWS[Name]["Icon"] != Icon and WINDOWS[Name]["Open"]:
        if type(Icon) != str:
            if WINDOWS[Name]["NoWarnings"] != True:
                print(RED + "Icon must be an absolute path as a string." + NORMAL)
            return
        WINDOWS[Name]["Icon"] = Icon
        HWND = win32gui.FindWindow(None, Name)
        Icon = Icon.replace("\\", "/")
        if os.path.exists(Icon) and Icon.endswith(".ico"):
            IconHandle = win32gui.LoadImage(None, Icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_SMALL, IconHandle)
            win32gui.SendMessage(HWND, win32con.WM_SETICON, win32con.ICON_BIG, IconHandle)


# MARK: GetIcon()
def GetIcon(Name=""):
    """
    Get the icon of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    str
        The path to the icon file (must be a .ico file).
    """
    return WINDOWS[Name]["Icon"]


# MARK: SetOpen()
def SetOpen(Name="", State=True):
    """
    Open or close the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.
    State : bool
        True to open the window, False to close it.

    Returns
    -------
    None
    """
    if State == True and WINDOWS[Name]["Open"] != True:
        CreateWindow(Name=Name)
    elif State == False and WINDOWS[Name]["Open"] == True:
        Close(Name=Name)


# MARK: GetOpen()
def GetOpen(Name=""):
    """
    Check if the specified window is open.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    bool
        True if the window is open, False if closed by code, None if closed by the user.
    """
    return WINDOWS[Name]["Open"]


# MARK: GetHandle()
def GetHandle(Name=""):
    """
    Get the handle of the specified window.

    Parameters
    ----------
    Name : str
        The name of the window.

    Returns
    -------
    int
        The window's handle.
    """
    return win32gui.FindWindow(None, Name)


# MARK: Show()
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
    if WINDOWS[Name]["Open"] == False:
        CreateWindow(Name=Name)
    elif WINDOWS[Name]["Open"] == None and WINDOWS[Name]["Undestroyable"] == False:
        return
    if glfw.window_should_close(WINDOWS[Name]["Window"]):
        if WINDOWS[Name]["Open"] == True:
            Close(Name=Name)
        if WINDOWS[Name]["Undestroyable"] == True:
            Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Undestroyable=WINDOWS[Name]["Undestroyable"], Icon=WINDOWS[Name]["Icon"])
        else:
            WINDOWS[Name]["Open"] = None
            return

    if Frame is not None:
        HWND = win32gui.FindWindow(None, Name)
        if HWND == 0 or HWND == None:
            return
        if int(win32gui.IsIconic(HWND)) == 1:
            glfw.poll_events()
            return

        RECT = win32gui.GetClientRect(HWND)
        TopLeft = win32gui.ClientToScreen(HWND, (RECT[0], RECT[1]))
        BottomRight = win32gui.ClientToScreen(HWND, (RECT[2], RECT[3]))
        SIZE = BottomRight[0] - TopLeft[0], BottomRight[1] - TopLeft[1]

        HDC = win32gui.GetDC(HWND)

        Frame = numpy.flip(Frame, axis=0)
        Frame = cv2.resize(Frame, GetSize(Name=Name))
        Frame = numpy.ascontiguousarray(Frame)

        windll.gdi32.StretchDIBits(HDC, 0, 0, SIZE[0], SIZE[1], 0, 0, SIZE[0], SIZE[1], ctypes.c_void_p(Frame.ctypes.data), ctypes.byref(BITMAPINFO(Frame.shape[1], Frame.shape[0])), win32con.DIB_RGB_COLORS, win32con.SRCCOPY)

        win32gui.ReleaseDC(HWND, HDC)

    glfw.poll_events()