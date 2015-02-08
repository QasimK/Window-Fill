"""
Register global hotkeys.

Win32 reference:
Register hotkey
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms646309%28v=vs.85%29.aspx
Unregister hotkey
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms646327%28v=vs.85%29.aspx
_GetMessage
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms644936%28v=vs.85%29.aspx
Message structure & Hotkey Message
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms644958%28v=vs.85%29.aspx
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms646279%28v=vs.85%29.aspx
"""

#TODO: Proper exceptions

import ctypes  # @UnusedImport
import ctypes.wintypes
import string
import logging

_RegisterHotKey = ctypes.windll.user32.RegisterHotKey
_UnregisterHotKey = ctypes.windll.user32.UnregisterHotKey
_GetMessage = ctypes.windll.user32.GetMessageW

#Mouse events are not supported with _RegisterHotKey
KEY_MAP = { letter: 0x41+i for i, letter in enumerate(string.ascii_uppercase) }

_registered_hotkeys = [] #[(HID, Hotkey tuple, function), ...]


class HotkeyException(Exception):
    pass


class FailedToRegisterHotkey(HotkeyException):
    pass


def get_total_registrations():
    """Return number of registered hotkeys"""
    return len(_registered_hotkeys)


def register_hotkey(keys, func):
    """Return the HID (identifier) of the newly registered hotkey
    
    By registering func(x, y) with keys, the function will be called with the
    mouse cursor position (x, y) at the time the keys are pressed.
    
    eg. register_hotkey(("MOD_CONTROL", "MOD_SHIFT", "Q"), lambda x, y: print())
    The keys must be a single key in KEY_MAP and optional modifiers.
    The possible modifiers are MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN, and
    MOD_NOREPEAT."""
    
    MODIFIER_VALUES = {
        "MOD_ALT": 0x0001,
        "MOD_CONTROL": 0x0002,
        "MOD_SHIFT": 0x0004,
        "MOD_WIN": 0x0008,
        "MOD_NOREPEAT": 0x4000
    }
    
    hid = len(_registered_hotkeys)
    new_reg = (hid, tuple(sorted(keys)), func)
    
    processed_keys = [key.upper() for key in keys]
    modifiers = 0
    for modifier_name, win_value in MODIFIER_VALUES.items():
        if modifier_name in processed_keys:
            processed_keys.remove(modifier_name)
            modifiers |= win_value
    
    #Must have exactly one keys left
    if len(processed_keys) != 1:
        raise FailedToRegisterHotkey("Invalid hotkey {}".format(keys))
    key = processed_keys[0].upper()
    
    if _RegisterHotKey(None, hid, modifiers, KEY_MAP[key]):
        logging.debug('Hotkey registered: {}'.format(new_reg))
        _registered_hotkeys.append(new_reg)
    else:
        logging.warning('Hotkey failed to register: {}'.format(new_reg))
        raise FailedToRegisterHotkey()
    return hid
    

def unregister_hotkey(hid=None, keys=None, func=None):
    """Return the number of hotkeys removed
    
    Hotkeys can be identified by a hid, a tuple of keys or a function."""
    
    if hid is None and keys is None and func is None:
        return 0
    
    if keys is not None:
        keys = tuple(sorted(keys))
    
    def registered(hotkey):
        """Return if hotkey was NOT removed"""
        stored_hid, stored_keys, stored_func = hotkey
        if((hid is not None and stored_hid == hid) or
           (keys is not None and stored_keys == keys) or
           (func is not None and stored_func == func)):
            if _UnregisterHotKey(None, stored_hid):
                logging.debug('Hotkey unregistered: {}'.format(*hotkey))
                return False
            else:
                logging.error('Failed to registered hotkey: {}'.format(*hotkey))
        
        return True
        
    
    global _registered_hotkeys
    original_length = len(_registered_hotkeys)
    _registered_hotkeys = [hk for hk in _registered_hotkeys if registered(hk)]
    
    return original_length - len(_registered_hotkeys)
    

def unregister_all_hotkeys():
    """Return if all hotkeys were successfully unregistered"""
    
    def registered(hotkey):
        """Return if hotkey was NOT removed"""
        stored_hid, stored_keys, stored_func = hotkey  # @UnusedVariable
        if _UnregisterHotKey(None, stored_hid):
            logging.debug('Hotkey unregistered: {}'.format(*hotkey))
            return False
        else:
            return True
    
    global _registered_hotkeys
    _registered_hotkeys = [hk for hk in _registered_hotkeys if registered(hk)]
    
    if len(_registered_hotkeys):
        return False
    else:
        return True


def process_next_message():
    """Return if next message was processed successfully (wait for message)"""
    msg = ctypes.wintypes.MSG()
    success = _GetMessage(ctypes.pointer(msg), None, 0, 0) # Waiting here
    
    if success <= 0:
        if success == 0:
            logging.info("Windows message to exit.")
        if success == -1:
            logging.error("Windows fatal message.")
        return success
    
    for hid, keys, func in _registered_hotkeys:  # @UnusedVariable
        if hid == msg.wParam:
            func(msg.pt.x, msg.pt.y)
            return True
    else:
        logging.warn('No hotkey registered for windows message, hid: {}'.format(
                     msg.wParam))
        return False
