import logging

import hotkey
import windowinfo
import settings

DEBUG = False

if DEBUG:
    log_file = "logging.log"
else:
    log_file = None

def move(x, y):
    windowinfo.fill_foreground_window()

if __name__ == '__main__':
    config = settings.Settings()
    user_hotkey = config.get_hotkey()
    
    logging.basicConfig(filename="logging.log", filemode='w',
                        level=logging.DEBUG)
    
    if hotkey.register_hotkey(user_hotkey, move):
        while True:
            try:
                hotkey.process_messages_wait_once()
            except Exception as e:
                logging.critical(str(e))

        if not hotkey.unregister_hotkey(keys=user_hotkey):
            logging.critical("Unable to unregister hotkey")
    else:
        logging.critical("Unable to register hotkey")
