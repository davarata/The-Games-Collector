import configparser
import os

import utils
from plugins.mappers.input_mapper import InputMapper


class RetroArchMapper(InputMapper):

    def __init__(self):
        definitions_file = utils.get_config_file('RetroArch.mapper')
        self.definitions = configparser.ConfigParser()
        self.definitions.read(definitions_file)

    def activate(self):
        launch_config = {}

        key_key = 'input_player{0}_{1}'
        button_key = 'input_player{0}_{1}_btn'
        axis_key = 'input_player{0}_{1}_axis'

        for mapping in self.input_mappings:
            trigger_id, trigger_type = mapping.physical.split(' ')
            trigger_type = trigger_type[1:-1]

            key = 'nul'
            button = 'nul'
            axis = 'nul'

            if trigger_type == 'button':
                button = trigger_id
            elif trigger_type == 'axis':
                axis = trigger_id
            else:
                key = trigger_id

            # TODO Add support for two players.
            launch_config[key_key.format('1', mapping.virtual)] = '"' + key + '"'
            launch_config[button_key.format('1', mapping.virtual)] = '"' + button + '"'
            launch_config[axis_key.format('1', mapping.virtual)] = '"' + axis + '"'

        mappings_file = open('/tmp/retroarch-mappings.cfg', 'w')
        for key in sorted(launch_config.keys()):
            mappings_file.write(key + ' = ' + launch_config[key] + os.linesep)
        mappings_file.close()

    name = 'RetroArch'
    supported_implementations = {
        'Arcade:Xbox360',
        'GameBoyAdvance:Xbox360',
        'MasterSystem:Xbox360',
        'MegaDrive:Xbox360',
        'N64:Xbox360',
        'SNES:Xbox360',
    }
