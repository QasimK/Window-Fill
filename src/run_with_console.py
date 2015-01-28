import logging

import hotkey
import windowinfo

DEBUG = False
HOTKEY = ["MOD_CONTROL", "MOD_SHIFT", "Q"]

if DEBUG:
    log_file = "logging.log"
else:
    log_file = None

def move(x, y):
    windowinfo.fill_foreground_window()

if __name__ == '__main__':
    logging.basicConfig(filename="logging.log", filemode='w',
                        level=logging.DEBUG)
    
    if hotkey.register_hotkey(HOTKEY, move):
        while True:
            try:
                hotkey.process_messages_wait_once()
            except Exception as e:
                logging.critical(str(e))

        if not hotkey.unregister_hotkey(keys=HOTKEY):
            logging.critical("Unable to unregister hotkey")
    else:
        logging.critical("Unable to register hotkey")
