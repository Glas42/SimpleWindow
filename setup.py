from setuptools import setup, find_packages

setup(
    name="SimpleWindow",
    version="0.1",
    description="A package to easily create windows in Python using PyOpenGL, GLFW, OpenCV-Python, NumPy, pywin32 and ctypes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Glas42",
    license="GPL-3.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pyopengl",
        "glfw",
        "opencv-python",
        "numpy",
        "pywin32",
    ],
)
