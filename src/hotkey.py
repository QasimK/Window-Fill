"""
Register global hotkeys.

Win32 reference:
Register hotkey
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms646309%28v=vs.85%29.aspx
Unregister hotkey
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms646327%28v=vs.85%29.aspx
GetMessage
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms644936%28v=vs.85%29.aspx
Message structure & Hotkey Message
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms644958%28v=vs.85%29.aspx
    https://msdn.microsoft.com/en-us/library/windows/desktop/ms646279%28v=vs.85%29.aspx
"""

#TODO: Turn prints into logging
#TODO: Proper exceptions

import ctypes  # @UnusedImport
import ctypes.wintypes

RegisterHotKey = ctypes.windll.user32.RegisterHotKey
UnregisterHotKey = ctypes.windll.user32.UnregisterHotKey
GetMessage = ctypes.windll.user32.GetMessageW

#Mouse events are not supported
KEY_MAP = {
    #"MOUSE_LEFT": 0x01,
    #"MOUSE_RIGHT": 0x02,
    "A": 0x41,
    "Q": 0x51
}

_registered_hotkeys = []

def register_hotkey(keys, func):
    """Return hid if func has been registered, otherwise return 0.
    
    By registering func(x, y) with keys, the function will be called with the
    mouse cursor position (x, y) at the time the keys are pressed.
        
    eg. create_hotkey(("MOD_CONTROL", "MOD_SHIFT", "Q"), func)
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
    
    keys = [key.upper() for key in keys]
    modifiers = 0
    for modifier_name, win_value in MODIFIER_VALUES.items():
        if modifier_name in keys:
            keys.remove(modifier_name)
            modifiers |= win_value
    
    #Must have exactly one keys left
    if len(keys) != 1:
        return False
    key = keys[0].upper()
    
    success = RegisterHotKey(None, hid, modifiers, KEY_MAP[key])
    if success:
        _registered_hotkeys.append(new_reg)
    return success
    

def unregister_hotkey(hid=None, keys=None, func=None):
    """Return if hotkeys identified by optional hid, keys, or func are removed"""
    
    if hid is None and keys is None and func is None:
        return False
    
    #TODO: unregister by hid or func
    remove_positions = []
    for pos, (hid, stored_keys, func) in enumerate(_registered_hotkeys):
        if stored_keys == tuple(sorted(keys)):
            success = UnregisterHotKey(None, hid)
            if success:
                remove_positions.append(pos)
    
    if remove_positions:
        for pos in remove_positions:
            del _registered_hotkeys[pos]
        return True
    else:
        return False

def process_messages_wait_once():
    """Wait for the next message and process it"""
    msg = ctypes.wintypes.MSG()
    success = GetMessage(ctypes.pointer(msg), None, 0, 0)
    
    if success <= 0:
        if success == 0:
            print("Exit")
        if success == -1:
            print("Fatal error")
        return success
    
    for hid, keys, func in _registered_hotkeys:  # @UnusedVariable
        if hid == msg.wParam:
            func(msg.pt.x, msg.pt.y)
            return True
    else:
        print("No hotkey registered to this")
        return False


if __name__ == '__main__':
    def do_rand(x, y):
        print("Whoop", x, y)
    
    register_hotkey(("MOD_CONTROL", "MOD_SHIFT", "Q"), do_rand)
    process_messages_wait_once()
    print("unreg", unregister_hotkey(keys=("MOD_CONTROL", "MOD_SHIFT", "Q")))
    process_messages_wait_once()
