import logging

import settings
import windowinfo
import hotkey

logging = logging.getLogger(__name__)


def move(x, y):
    windowinfo.fill_foreground_window()

if __name__ == '__main__':
    config = settings.Settings()
    config.setup_logging(to_file=True, to_console=True)
    user_hotkey = config.get_hotkey()
    
    try:
        hotkey.register_hotkey(user_hotkey, move)
    except hotkey.FailedToRegisterHotkey as e:
        logging.critical(e)
    else:
        while True:
            try:
                hotkey.process_next_message()
            except Exception as e:
                logging.critical(str(e))

        if not hotkey.unregister_hotkey(keys=user_hotkey):
            logging.error("Unable to unregister hotkey")
    
    logging.shutdown()
