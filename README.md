# SimpleWindow

A package to easily create windows in Python using GLFW, OpenCV-Python, NumPy, pywin32 and ctypes.

## Installation

```
pip install SimpleWindow
```

## Usage

```python
import SimpleWindow
import numpy as np

# Initialize the window, the window wont be shown until Show() is called
SimpleWindow.Initialize(Name="Example Window", Size=(1280, 720), Position=(100, 100), TitleBarColor=(0, 0, 0), Resizable=True, TopMost=False, Undestroyable=False, Icon="")

# Create an image
Image = np.zeros((720, 1280, 3), dtype=np.uint8)

while True:
    # The window will be shown now since its the first call of Show() since the Initialize() call
    SimpleWindow.Show(Name="Example Window", Frame=Image)

    # Get the window status
    WindowState = SimpleWindow.GetWindowStatus(Name="Example Window")

    # If the value is False then the window was destroyed by the code, if the value is None then the window got destroyed by the user
    if WindowState["Open"] == False or WindowState["Open"] == None:
        break
```