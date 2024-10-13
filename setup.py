from setuptools import setup, find_packages

setup(
    name="SimpleWindow",
    version="0.14",
    description="A package to easily create windows in Python using GLFW, OpenCV-Python, NumPy, pywin32 and ctypes.",
    long_description=open("README.md").read(),
    author="Glas42",
    license="GPL-3.0",
    packages=["SimpleWindow"],
    python_requires=">=3.9",
    install_requires=[
        "glfw",
        "opencv-python",
        "numpy",
        "pywin32",
    ],
)