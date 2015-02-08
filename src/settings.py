''' Handle the configuration file '''

import os
import logging
import configparser
import string

DEFAULT_APPDATA_LOCATION = os.path.join(os.getenv('APPDATA'), 'Window Fill')
DEFAULT_CONFIG_NAME = 'config.ini'
DEFAULT_LOG_NAME = 'log.txt'

default_settings = {
    'hotkey': {
        'use control': 'yes',
        'use shift': 'yes',
        'use alt': 'no',
        'keyboard letter': 'Q'
    },
    'development': {
        'enable logging': 'yes'
    }
}

class Settings:
    def __init__(self, appdata_location=DEFAULT_APPDATA_LOCATION):
        '''Load the configuration file'''
        self.appdata_location = appdata_location
        if not os.path.exists(appdata_location):
            os.makedirs(appdata_location)
        
        config_filename = os.path.join(appdata_location, DEFAULT_CONFIG_NAME)
        
        self.config = configparser.ConfigParser()
        # Ensure all settings will be available:
        self.config.read_dict(default_settings)
        
        try:
            with open(config_filename, 'r') as f:
                self.config.read_file(f, DEFAULT_CONFIG_NAME)
        except FileNotFoundError:
            pass
        
        # Write settings (did not exist / something may have been updated)
        with open(config_filename, 'w') as f:
            self.config.write(f)
    
    def get_hotkey(self):
        '''Return the hotkey as a list, eg. ['MOD_CONTROL', 'MOD_SHIFT', 'Q']'''
        hotkey = []
        if self.config.get('hotkey', 'use control') == 'yes':
            hotkey.append('MOD_CONTROL')
        if self.config.get('hotkey', 'use shift') == 'yes':
            hotkey.append('MOD_SHIFT')
        if self.config.get('hotkey', 'use alt') == 'yes':
            hotkey.append('MOD_SHIFT')
        
        keyboard_letter = self.config.get('hotkey', 'keyboard letter')
        if keyboard_letter in string.ascii_letters:
            hotkey.append(keyboard_letter)
        
        return hotkey
    
    def setup_logging(self, to_file=True, to_console=False):
        '''Setup logging behaviour to a file or to the console
        
        Log debug messages if in debug mode, otherwise just errors'''
        
        if self.config.get('development', 'enable logging') == 'yes':
            level = logging.DEBUG
        else:
            level = logging.ERROR
        
        if to_file:
            filename = os.path.join(self.appdata_location, DEFAULT_LOG_NAME)
            logging.basicConfig(filename=filename, filemode='w', level=level)
        elif to_console:
            logging.basicConfig(level=level)
