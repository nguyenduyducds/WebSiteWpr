
import sys
import os

def resource_path(relative_path):
    """
    Get absolute path to resource.
    Works for: dev (script), PyInstaller (--onefile), Nuitka (--onefile / --standalone)
    """
    # 1. PyInstaller onefile: temp unpacked dir
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    
    # 2. Nuitka onefile / standalone: same dir as the exe
    if getattr(sys, 'frozen', False) or '__compiled__' in dir(__builtins__):
        # Nuitka marks compiled code with __compiled__ in builtins
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        return os.path.join(base_path, relative_path)
    
    # 3. Running as normal Python script (dev mode)
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Go up one level (model/ -> project root)
    base_path = os.path.dirname(base_path)
    return os.path.join(base_path, relative_path)
