''' Handle the configuration file '''

import os
import configparser
import string

DEFAULT_SAVE_LOCATION = os.path.join(os.getenv('APPDATA'), 'Window Fill')
DEFAULT_SAVE_NAME = 'config.ini'
DEFAULT_SAVE_FILE = os.path.join(DEFAULT_SAVE_LOCATION, DEFAULT_SAVE_NAME)

default_settings = {
    'hotkey': {
        'use control': 'yes',
        'use shift': 'yes',
        'use alt': 'no',
        'use keyboard letter': 'Q'
    }
}

class Settings:
    def __init__(self, config_location=DEFAULT_SAVE_LOCATION):
        '''Load the configuration file'''
        self.config = configparser.ConfigParser()

        if not os.path.exists(DEFAULT_SAVE_LOCATION):
            os.makedirs(DEFAULT_SAVE_LOCATION)
        
        try:
            with open(DEFAULT_SAVE_FILE, 'r') as f:
                self.config.read_file(f, DEFAULT_SAVE_NAME)
        except FileNotFoundError:
            self.config.read_dict(default_settings)
            with open(DEFAULT_SAVE_FILE, 'w') as f:
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
        
        keyboard_letter = self.config.get('hotkey', 'use keyboard letter')
        if keyboard_letter in string.ascii_letters:
            hotkey.append(keyboard_letter)
        
        return hotkey
