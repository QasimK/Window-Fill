import unittest

import hotkey

class TestWindowInfo(unittest.TestCase):
    """Registered hotkeys are per-thread, so a failure in a unit-test
    will probably result in later unit-tests failing"""
    
    def test_get_number_of_registrations(self):
        self.assertEqual(hotkey.get_total_registrations(), 0)
    
    def test_register_unregister(self):
        key_combo = ["mod_control", "mod_SHIFT", "x"]
        func = lambda: print("CSX")
        
        self.assertEqual(hotkey.get_total_registrations(), 0)
        
        #HID unregister
        hid = hotkey.register_hotkey(key_combo, func)
        self.assertEqual(hotkey.get_total_registrations(), 1)
        self.assertFalse(hotkey.unregister_hotkey(hid=hid + 1))
        self.assertTrue(hotkey.unregister_hotkey(hid=hid))
        self.assertEqual(hotkey.get_total_registrations(), 0)
        
        #hotkey unregister
        hid = hotkey.register_hotkey(key_combo, func)
        self.assertIsNotNone(hid)
        self.assertEqual(hotkey.get_total_registrations(), 1)
        self.assertFalse(hotkey.unregister_hotkey(keys=["invalid", "combo"]))
        self.assertTrue(hotkey.unregister_hotkey(keys=key_combo))
        self.assertEqual(hotkey.get_total_registrations(), 0)
        
        #func unregister
        hid = hotkey.register_hotkey(key_combo, func)
        self.assertIsNotNone(hid)
        self.assertEqual(hotkey.get_total_registrations(), 1)
        self.assertFalse(hotkey.unregister_hotkey(func=lambda: print("CSX")))
        self.assertTrue(hotkey.unregister_hotkey(func=func))
        self.assertEqual(hotkey.get_total_registrations(), 0)
    
    def test_unregister_multiple(self):
        """Test unregistering multiple hotkeys by the same hotkey/function"""
        func1 = lambda x: x+1
        func2 = lambda x: x+1
        
        #Unregister by function
        self.assertEqual(hotkey.get_total_registrations(), 0)
        self.assertTrue(hotkey.register_hotkey(["Q"], func1))
        self.assertTrue(hotkey.register_hotkey(["W"], func1))
        self.assertTrue(hotkey.register_hotkey(["E"], func2))
        self.assertEqual(hotkey.get_total_registrations(), 3)
        self.assertTrue(hotkey.unregister_hotkey(func=func1))
        self.assertEqual(hotkey.get_total_registrations(), 1)
        
        #Unregister by keys
        self.assertTrue(hotkey.register_hotkey(["E"], func1))
        self.assertEqual(hotkey.get_total_registrations(), 2)
        self.assertTrue(hotkey.unregister_hotkey(keys=["E"]))
        self.assertEqual(hotkey.get_total_registrations(), 0)
    
    def test_unregister_all(self):
        self.assertEqual(hotkey.get_total_registrations(), 0)
        self.assertTrue(hotkey.register_hotkey(["Q"], lambda: print()))
        self.assertTrue(hotkey.register_hotkey(["W"], lambda x: x+1))
        self.assertTrue(hotkey.register_hotkey(["E"], lambda x: x+1))
        self.assertEqual(hotkey.get_total_registrations(), 3)
        hotkey.unregister_all_hotkeys()
        self.assertEqual(hotkey.get_total_registrations(), 0)
    
    """
    def test_interactive(self):
        '''Testing:'''
        return 0
        def do_whoop(x, y):
            print("Whoop", x, y)
        
        hotkey = ("MOD_CONTROL", "MOD_SHIFT", "Q")
        print("Register hotkey. Press ctrl-shift-q.")
        hotkey.register_hotkey(hotkey, do_whoop)
        hotkey.process_next_message()
        print("Unregister hotkey:", hotkey.unregister_hotkey(keys=hotkey))
        print("Press hotkey again.")
        hotkey.process_next_message()
    """

if __name__ == "__main__":
    unittest.main()
