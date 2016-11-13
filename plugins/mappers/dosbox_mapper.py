import os

from config_manager import ConfigManager
from plugins.mappers.input_mapper import InputMapper


class DOSBoxMapper(InputMapper):

    def activate(self):
        default_mapping_data = {}

        with open(self.install_dir + '/mapper-0.74.map', 'r') as default_mappings:
            for line in default_mappings:
                key, *_ignore = line.split(' ')
                default_mapping_data[key] = line

        for mapping in self.input_mappings:
            default_mapping_data[mapping['virtual']] = mapping['virtual'] + ' "key ' + mapping['physical'] + '"' + os.linesep

        game_root = ConfigManager.get_instance().get_config('Game Config')['game_root']
        with open(game_root + '/mapper-0.74.map', 'w') as mappings_file:
            for line in default_mapping_data.values():
                mappings_file.write(line)

    def deactivate(self):
        # delete file
        pass

    name = 'DOSBox'
    supported_implementations = {'Keyboard:Keyboard'}
