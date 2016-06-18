import os
import subprocess
import sys
from pathlib import Path

from plugins.launchers.game_launcher import GameLauncher


class RetroArchLauncher(GameLauncher):

    def get_platform_description(self):
        if self.game_data['platform'] == 'Arcade':
            return 'arcade machines'
        elif self.game_data['platform'] in self.consoles:
            return 'the ' + self.game_data['platform'] + ' console'
        elif self.game_data['platform'] in self.handhelds:
            return 'the ' + self.game_data['platform'] + ' handheld'
        else:
            return super(RetroArchLauncher, self).get_platform_description()

    def launch_game(self):
        platform_config = os.path.join(self.game_data['platform_config'], self.game_data['platform'] + '.cfg')
        if os.path.isfile(platform_config):
            with open(platform_config) as f:
                for line in f:
                    conf_entry = self.replace_tokens(line).split('=')
                    if len(conf_entry) > 1:
                        self.launch_config[conf_entry[0].strip()] = conf_entry[1].strip()

        game_config = self.game_data['target'][:self.game_data['target'].rfind('.')] + '.cfg'
        if os.path.isfile(game_config):
            with open(game_config) as f:
                for line in f:
                    conf_entry = self.replace_tokens(line).split('=')
                    if len(conf_entry) > 1:
                        self.launch_config[conf_entry[0].strip()] = conf_entry[1].strip()

        mapping_config = '/tmp/retroarch-mappings.cfg'
        if os.path.isfile(mapping_config):
            with open(mapping_config) as f:
                for line in f:
                    conf_entry = self.replace_tokens(line).split('=')
                    if len(conf_entry) > 1:
                        self.launch_config[conf_entry[0].strip()] = conf_entry[1].strip()

        config_file = open('/tmp/game-launcher.cfg', 'w')
        for key in sorted(self.launch_config.keys()):
            config_file.write(key + ' = ' + self.launch_config[key] + os.linesep)
        config_file.close()
        config_files = '/tmp/game-launcher.cfg'

        parameters = [
            'retroarch',
            self.game_data['target'],
            '--libretro',
            self.game_data['core'],
            '--appendconfig',
            config_files]
        subprocess.Popen(parameters, cwd=self.game_data['working_dir']).wait()

    # TODO rename this method
    def replace_tokens(self, line):
        if line.strip().startswith('#'):
            modified_line = line.partition(' ')[2].strip()
            if modified_line.startswith('@game-launcher[\'') and modified_line.endswith('\']'):
                modified_line = modified_line[16:-2]
                modified_line = modified_line.replace('${game_root}', '"' + self.game_data['game_root'] + '"')
                return modified_line + '\n'
            else:
                return line
        else:
            return line

    def configure_env(self):
        if self.game_data['platform'] == 'Arcade':
            Path(self.launcher_config['General']['Games Location'] + '/nvram').symlink_to(self.game_data['game_root'])

    def revert_env(self):
        if self.game_data['platform'] == 'Arcade':
            os.unlink(os.path.join(self.launcher_config['General']['Games Location'], 'nvram'))

    def set_launcher_data(self, descriptor):
        if self.launcher_params is None or len(self.launcher_params) == 0:
            self.game_data['core'] = self.retroarch_cores[self.game_data['platform']]
        elif len(self.launcher_params) == 1:
            self.game_data['core'] = self.launcher_params[0]
        else:
            print('More than one parameter found for RetroArch launcher: ' + ' '.join(self.launcher_params))
            sys.exit(1)

        if self.game_data['core'] not in self.retroarch_cores.values():
            print('Unknown core: ' + self.game_data['core'])

        self.game_data['core'] = os.path.join(self.launcher_config['RetroArch']['Cores Location'],
                                              self.game_data['core'] + '.so')

    name = 'RetroArch'
    supported_implementations = {
        'Arcade',
        'DOS',
        'Master System',
        'Mega Drive',
        'NES',
        'SNES',
        'Game Boy Advance',
        'N64'
    }

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}

    launch_config = {}

    retroarch_cores = {
        'Arcade': 'mame078_libretro',
        'DOS': 'dosbox_libretro',
        'Master System': 'picodrive_libretro',
        'Mega Drive': 'picodrive_libretro',  #
        'NES': 'fceumm_libretro',
        'SNES': 'snes9x_libretro',
        'Game Boy Advance': 'vba_next_libretro',
        'N64': 'mupen64plus_libretro'
    }

    consoles = {
        'Master System',
        'Mega Drive',
        'Nintendo Entertainment System',
        'SNES',
        'N64'
    }

    handhelds = {'Game Boy Advance'}
