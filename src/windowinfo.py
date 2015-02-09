'''
Provides: fill_foreground_window()
'''

import ctypes  # @UnusedImport
import ctypes.wintypes
import math
import logging

logging = logging.getLogger(__name__)

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool,
                                     ctypes.POINTER(ctypes.c_int),
                                     ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowRect = ctypes.windll.user32.GetWindowRect
GetDesktopWindow = ctypes.windll.user32.GetDesktopWindow
IsIconic = ctypes.windll.user32.IsIconic #Is Minimised?
IsZoomed = ctypes.windll.user32.IsZoomed #Is Maximised?
GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
MoveWindow = ctypes.windll.user32.MoveWindow
GetCursorPos = ctypes.windll.user32.GetCursorPos


def get_list_of_windows():
    """Return hwnds of all windows"""
    hwnds = []
    def foreach_window(hwnd, lParam):
        hwnds.append(hwnd)
        return True
    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return hwnds

def get_active_windows():
    """Return a list of visible and non-minimised Window objects
    
    The window must have a title.
    Also it excludes "Program Manager" which fills up entire desktop.
    Also excludes special run_once.bat file.
    """
    active_windows = [Window.create_from_hwnd(hwnd) for hwnd
                      in get_list_of_windows()
                      if not IsIconic(hwnd) and IsWindowVisible(hwnd)]
    wins_with_titles = [win for win in active_windows
                        if win.title != '' and win.title != 'Program Manager'
                        and not win.title.startswith('Window Fill.exe')]
    return wins_with_titles

def get_desktop_size():
    """Get the full desktop resolution"""
    rect = ctypes.wintypes.RECT()
    GetWindowRect(GetDesktopWindow(), ctypes.pointer(rect))
    return (rect.right, rect.bottom)

def get_usable_size():
    """Return the usable screen resolution (ie. exclude task bar)"""
    s = get_desktop_size()
    #TODO: Make it not a hack
    return s[0], s[1] - 40 #Hack bottom task bar removable

def get_window_title(hwnd):
    """Return the title of a window"""
    length = GetWindowTextLength(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length+1)
    return buff.value

def get_window_rect(hwnd):
    """Return the window rectangle (left, top, right, bottom)"""
    rect = ctypes.wintypes.RECT()
    GetWindowRect(hwnd, ctypes.pointer(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)

def get_foreground_window():
    """Return the foreground window"""
    return Window.create_from_hwnd(GetForegroundWindow())

def get_mouse_pos():
    class CURSORINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint),
                    ('flags', ctypes.c_uint),
                    ('hCursor', ctypes.c_void_p),
                    ('ptScreenPos', ctypes.wintypes.POINT)]
    
    GetCursorInfo = ctypes.windll.user32.GetCursorInfo
    GetCursorInfo.argtypes = [ctypes.POINTER(CURSORINFO)]
    
    # Initialize the output structure
    info = CURSORINFO()
    info.cbSize = ctypes.sizeof(info)
    
    if GetCursorInfo(ctypes.byref(info)):
        if info.flags & 0x00000001:
            #The cursor is showing
            return (info.ptScreenPos.x, info.ptScreenPos.y)
        else:
            logging.error("Cursor is not showing")
    else:
        # Error occurred (invalid structure size?)
        logging.error("Invalid structure size??")


class Window:
    def __init__(self, hwnd, title, rect, is_maximised):
        self.hwnd = hwnd
        self.title = title
        self.position = rect
        self.is_maximised = is_maximised
    
    @property
    def left(self):
        return self.position[0]
    
    @property
    def top(self):
        return self.position[1]
    
    @property
    def right(self):
        return self.position[2]
    
    @property
    def bottom(self):
        return self.position[3]
    
    def move_window(self, rect):
        """Move the window to the specified rectangle
        
        It will not move if the position is the same."""
        if self.hwnd is not None:
            if not self.is_maximised:
                if self.position != rect:
                    x, y = rect[0], rect[1]
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    MoveWindow(self.hwnd, x, y, width, height, True)
                else:
                    logging.info("Did not move window into the same position")
            else:
                logging.info("Did not move maximised window")
    
    def __eq__(self, other):
        return self.title == other.title and self.position == other.position
    
    def __str__(self):
        return "{} @ {}".format(self.title, self.position)
    
    @classmethod
    def create_from_hwnd(cls, hwnd):
        title = get_window_title(hwnd)
        position = get_window_rect(hwnd)
        is_maximised = IsZoomed(hwnd)
        
        return cls(hwnd, title, position, is_maximised)
    
    @classmethod
    def create_dummy(cls, title, rect, is_maximised=False):
        return cls(None, title, rect, is_maximised)


def is_empty(windows, position):
    """Return whether there is no window at position"""
    for window in windows:
        if(window.left < position[0] < window.right and
           window.top < position[1] < window.bottom):
            #Point is inside window
            return False
    return True


def fill_space(windows, desktop_size, position):
    """Specify (left, top, right, bottom) of a window to fill position (x, y)
    
    Windows should(!) exclude the window that you are moving.
    Requires position to be empty."""
    
    if not is_empty(windows, position):
        logging.warning("Attempted to move window into non-empty position")
        return None
    
    #Get left most on central horizontal line
    new_left = position[0]
    while is_empty(windows, (new_left - 1, position[1])) and new_left > 0:
        new_left -= 1
    
    new_right = position[0]
    while(is_empty(windows, (new_right + 1, position[1])) and 
          new_right < desktop_size[0]):
        new_right += 1
    
    #Try to move the new horizontal line up as much as possible
    new_top = position[1]
    def test_next_top(next_top):
        for x in range(new_left, new_right+1, 10):
            if not is_empty(windows, (x, next_top)):
                return False
        return True
    
    jumpby = 128
    while new_top > 0:
        if test_next_top(new_top - jumpby):
            new_top -= jumpby
            if new_top < 0:
                new_top = 0
        elif jumpby > 1:
            jumpby = math.floor(jumpby/2)
        else:
            break
    
    new_bottom = position[1]
    def test_next_bottom(next_bottom):
        for x in range(new_left, new_right+1, 10):
            if not is_empty(windows, (x, next_bottom)):
                return False
        return True
    
    jumpby = 128
    while new_bottom < desktop_size[1]:
        if test_next_bottom(new_bottom + jumpby):
            new_bottom += jumpby
            if new_bottom > desktop_size[1]:
                new_bottom = desktop_size[1]
        elif jumpby > 1:
            jumpby = math.floor(jumpby/2)
        else:
            break
    
    return (new_left, new_top, new_right, new_bottom)


def fill_foreground_window():
    """Fill the current foreground window to available space at mouse cursor."""
    
    logging.info("Start a window fill")
    
    mouse_pos = get_mouse_pos()
    logging.debug("Mouse position: {}".format(mouse_pos))
    
    wins = get_active_windows()
    
    desktop_size = get_usable_size()
    logging.debug("Usable desktop size: {}".format(desktop_size))
    
    fore = get_foreground_window()
    logging.debug("Foreground window: {}".format(str(fore)))
    
    real_size = get_desktop_size()
    if fore.position == (0, 0, real_size[0], real_size[1]):
        logging.info("Window is full-screen, we will not move it.")
    else:
        logging.debug("---Windows excluding foreground window:")
        wins = [win for win in wins if win != fore]
        for win in wins:
            logging.debug(str(win))
        
        new_size = fill_space(wins, desktop_size, mouse_pos)
        if new_size is not None:
            logging.info("Moving window to given rectangle: {}".format(new_size))
            fore.move_window(new_size)
        else:
            logging.warning("Unable to obtain rectangle to move window into.")
    
    logging.info("Finished window fill")
    logging.info("")
