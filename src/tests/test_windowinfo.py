import unittest

import windowinfo as w

class TestWindowInfo(unittest.TestCase):

    def test_is_empty(self):
        win1 = w.Window.create_dummy("win1", (0, 0, 100, 100))
        
        self.assertTrue(w.is_empty([win1], (0, 0)))
        self.assertFalse(w.is_empty([win1], (50, 50)))
        self.assertTrue(w.is_empty([win1], (100, 100)))
        
        win2 = w.Window.create_dummy("win2", (50, 50, 150, 150))
        
        self.assertTrue(w.is_empty([win1, win2], (0, 0)))
        self.assertTrue(w.is_empty([win1, win2], (25, 125)))
        self.assertTrue(w.is_empty([win1, win2], (125, 25)))
        self.assertTrue(w.is_empty([win1, win2], (150, 150)))
        
        self.assertFalse(w.is_empty([win1, win2], (100, 100)))
        self.assertFalse(w.is_empty([win1, win2], (149, 149)))
    
    def test_fill_space(self):
        desktop_size = 800, 600
        win1 = w.Window.create_dummy("win1", (100, 100, 200, 200))
        
        self.assertEqual(w.fill_space([win1], desktop_size, (300, 150)),
                         (200, 0, desktop_size[0], desktop_size[1]))
        
        win2 = w.Window.create_dummy("win2", (300, 300, 400, 400))
        self.assertEqual(w.fill_space([win1, win2], desktop_size, (250, 250)),
                         (0, 200, desktop_size[0], 300))
    

if __name__ == "__main__":
    unittest.main()
