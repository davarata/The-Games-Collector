import configparser
import os
import subprocess

import utils
from plugins.mappers.input_mapper import InputMapper


class XmodmapMapper(InputMapper):

    def __init__(self):
        definitions_file = utils.get_config_file('Xmodmap.mapper')
        self.definitions = configparser.ConfigParser()
        self.definitions.read(definitions_file)

    def activate(self):
        output = subprocess.check_output(['xmodmap', '-pke'], universal_newlines=True)

        mappings_file = open('/tmp/xmodmap_revert', 'w')
        for line in output.split(os.linesep):
            config_line = [column for column in line.split(' ') if column.strip() != '']
            for mapping in self.input_mappings:
                if (len(config_line) > 3) and (config_line[3].lower() == mapping['physical'].lower()):
                    mappings_file.write(line + os.linesep)
        mappings_file.close()

        mappings_file = open('/tmp/xmodmap_new', 'w')
        for mapping in self.input_mappings:
            mappings_file.write('! ' + mapping['description'] + os.linesep)
            mappings_file.write('keysym ' + mapping['physical'] + ' = ' + mapping['virtual'] + os.linesep)
            mappings_file.write(os.linesep)
        mappings_file.close()

        subprocess.Popen(['xmodmap', '/tmp/xmodmap_new'])

    def deactivate(self):
        subprocess.Popen(['xmodmap', '/tmp/xmodmap_revert'])

    name = 'Xmodmap'
    supported_implementations = {'Keyboard:Keyboard'}
