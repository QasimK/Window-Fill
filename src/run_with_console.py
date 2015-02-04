import logging

import settings
import windowinfo
import hotkey


def move(x, y):
    windowinfo.fill_foreground_window()

if __name__ == '__main__':
    config = settings.Settings()
    config.setup_default_logging()
    user_hotkey = config.get_hotkey()
    
    if hotkey.register_hotkey(user_hotkey, move):
        while True:
            try:
                hotkey.process_next_message()
            except Exception as e:
                logging.critical(str(e))

        if not hotkey.unregister_hotkey(keys=user_hotkey):
            logging.error("Unable to unregister hotkey")
    else:
        logging.critical("Unable to register hotkey")
    
    logging.shutdown()
