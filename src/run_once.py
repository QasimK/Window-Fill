import logging

import windowinfo

DEBUG = False

if DEBUG:
    log_file = "logging.log"
else:
    log_file = None

if __name__ == '__main__':
    logging.basicConfig(filename=log_file, filemode='w',
                        level=logging.DEBUG)
    
    try:
        windowinfo.fill_foreground_window()
    except Exception as e:
        logging.critical(str(e))
