from ctypes import windll, byref, sizeof, c_int
import win32gui, win32con
import OpenGL.GL as gl
import numpy
import glfw
import cv2
import os


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
    WINDOWS[Name] = {"Size": Size, "Position": Position, "TitleBarColor": TitleBarColor, "Resizable": Resizable, "TopMost": TopMost, "Undestroyable": Undestroyable, "Icon": Icon, "Created": False, "Window": None, "Texture": None}


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

    Texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, Texture)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, WindowWidth, WindowHeight, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, Frame)

    gl.glEnable(gl.GL_TEXTURE_2D)

    WINDOWS[Name]["Created"] = True
    WINDOWS[Name]["Window"] = Window
    WINDOWS[Name]["Texture"] = Texture


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
        WINDOWS[Name]["Resizable"] = Resizable == True
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
        WINDOWS[Name]["TopMost"] = TopMost == True
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
    return {"Open": WINDOWS[Name]["Created"], "HWND": HWND, "Foreground": win32gui.GetForegroundWindow() == HWND, "Iconic": int(win32gui.IsIconic(HWND)) == 0}


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
            Initialize(Name=Name, Size=WINDOWS[Name]["Size"], Position=WINDOWS[Name]["Position"], TitleBarColor=WINDOWS[Name]["TitleBarColor"], Resizable=WINDOWS[Name]["Resizable"], TopMost=WINDOWS[Name]["TopMost"], Icon=WINDOWS[Name]["Icon"])
        else:
            WINDOWS[Name]["Created"] = None
            return

    glfw.make_context_current(WINDOWS[Name]["Window"])

    if Frame is not None:
        Frame = cv2.flip(Frame, 0)
        Frame = cv2.resize(Frame, (gl.glGetTexLevelParameteriv(gl.GL_TEXTURE_2D, 0, gl.GL_TEXTURE_WIDTH), gl.glGetTexLevelParameteriv(gl.GL_TEXTURE_2D, 0, gl.GL_TEXTURE_HEIGHT)))
        gl.glBindTexture(gl.GL_TEXTURE_2D, WINDOWS[Name]["Texture"])
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, Frame.shape[1], Frame.shape[0], 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, Frame)

    gl.glBegin(gl.GL_QUADS)
    gl.glTexCoord2f(0, 0)
    gl.glVertex2f(-1, -1)
    gl.glTexCoord2f(1, 0)
    gl.glVertex2f(1, -1)
    gl.glTexCoord2f(1, 1)
    gl.glVertex2f(1, 1)
    gl.glTexCoord2f(0, 1)
    gl.glVertex2f(-1, 1)
    gl.glEnd()

    glfw.swap_buffers(WINDOWS[Name]["Window"])
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
    gl.glDeleteTextures([WINDOWS[Name]["Texture"]])
    glfw.terminate()
    WINDOWS[Name]["Created"] = False