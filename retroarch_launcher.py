import os
import subprocess
from pathlib import Path
import sys
from generic_launcher import GenericLauncher


class RetroArchLauncher(GenericLauncher):

    def get_name(self):
        return 'RetroArch'

    def get_platform_description(self):
        if self.game_data.platform == 'Arcade':
            return 'arcade machines'
        elif self.game_data.platform in self.consoles:
            return 'the ' + self.game_data.platform + ' console'
        elif self.game_data.platform in self.handhelds:
            return 'the ' + self.game_data.platform + ' handheld'

    def launch_game(self):
        launch_config = {}

        platform_config = os.path.join(self.game_data.platform_config, self.game_data.platform + '.cfg')
        if os.path.isfile(platform_config):
            with open(platform_config) as f:
                for line in f:
                    conf_entry = self.replace_tokens(line, self.game_data).split('=')
                    if len(conf_entry) > 1:
                        launch_config[conf_entry[0].strip()] = conf_entry[1]

        game_config = self.game_data.target[:self.game_data.target.rfind('.')] + '.cfg'
        if os.path.isfile(game_config):
            with open(game_config) as f:
                for line in f:
                    conf_entry = self.replace_tokens(line, self.game_data).split('=')
                    if len(conf_entry) > 1:
                        launch_config[conf_entry[0].strip()] = conf_entry[1]

        config_file = open('/tmp/game-launcher.cfg', 'w')
        for key in launch_config.keys():
            config_file.write(key + ' = ' + launch_config[key])
        config_file.close()
        config_files = '/tmp/game-launcher.cfg'

        # TODO move these mappings to the rest - will eventually end up as part of a plug-in
        if (self.game_data.mappings is not None) and (self.game_data.mappings.get('RetroArch') is not None):
            self.write_retroarch_mappings(self.game_data.mappings['RetroArch'])
            config_files += ',/tmp/retroarch_mappings.cfg'

        if self.game_data.platform == 'Arcade':
            nvram = Path(self.launcher_config['General']['Games Location'] + '/nvram')
            nvram.symlink_to(self.game_data.game_root)

        proc_params = ['retroarch', self.game_data.target, '--libretro', self.game_data.core, '--appendconfig', config_files]
        print(" ".join(proc_params))
        retroarch = subprocess.Popen(proc_params, cwd=self.game_data.working_dir)
        retroarch.wait()

    def replace_tokens(self, line, game_data):
        if line.strip().startswith('#'):
            modified_line = line.partition(' ')[2].strip()
            if modified_line.startswith('@game-launcher[\'') and modified_line.endswith('\']'):
                modified_line = modified_line[16:-2]
                modified_line = modified_line.replace('${game_root}', '"' + game_data.game_root + '"')
                return modified_line + '\n'
            else:
                return line
        else:
            return line

    def revert_env(self):
        if self.game_data.platform == 'Arcade':
            os.unlink(os.path.join(self.launcher_config['General']['Games Location'], 'nvram'))

    def set_launcher_data(self, descriptor):
        if self.launcher_params is None or len(self.launcher_params) == 0:
            self.game_data.core = self.retroarch_cores[self.game_data.platform]
        elif len(self.launcher_params) == 1:
            self.game_data.core = self.launcher_params[0]
        else:
            print('More than one parameter found for RetroArch launcher: ' + ' '.join(self.launcher_params))
            sys.exit(1)

        if self.game_data.core not in self.retroarch_cores.values():
            print('Unknown core: ' + self.game_data.core)

        self.game_data.core = os.path.join(self.launcher_config['RetroArch']['Cores Location'],
                                           self.game_data.core + '.so')

    def write_retroarch_mappings(self, mappings):
        key_line = 'input_player{0}_{1} = "{2}"'
        button_line = 'input_player{0}_{1}_btn = "{2}"'
        axis_line = 'input_player{0}_{1}_axis = "{2}"'

        mappings_file = open('/tmp/retroarch_mappings.cfg', 'w')
        for mapping in mappings:
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

            mappings_file.write('# ' + mapping.description[1:-1] + os.linesep)
            mappings_file.write(key_line.format(mapping.player, mapping.virtual, key) + os.linesep)
            mappings_file.write(button_line.format(mapping.player, mapping.virtual, button) + os.linesep)
            mappings_file.write(axis_line.format(mapping.player, mapping.virtual, axis) + os.linesep)
            mappings_file.write(os.linesep)

        mappings_file.close()

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}

    retroarch_cores = {'Arcade': 'mame078_libretro',
                       'DOS': 'dosbox_libretro',
                       'Mega Drive': 'picodrive_libretro',  #
                       'NES': 'fceumm_libretro',
                       'SNES': 'snes9x_libretro',
                       'Game Boy Advance': 'vba_next_libretro',
                       'N64': 'mupen64plus_libretro'}

    consoles = {'Mega Drive',
                'Nintendo Entertainment System',
                'SNES',
                'Nintendo 64'}

    handhelds = {'Game Boy Advance'}
