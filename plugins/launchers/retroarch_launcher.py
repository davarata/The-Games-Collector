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
        config = self.get_config()
        if config is not None and config.has_section(self.game_data['platform']):
            platform_config = config[self.game_data['platform']]
            for key in platform_config:
                self.launch_config[key] = self.replace_tokens(platform_config[key])

        game_config = self.game_data['target'][:self.game_data['target'].rfind('.')] + '.cfg'
        if os.path.isfile(game_config):
            with open(game_config) as f:
                for line in f:
                    conf_entry = line.split('=')
                    if len(conf_entry) > 1:
                        self.launch_config[conf_entry[0].strip()] = conf_entry[1].strip()

        mapping_config = '/tmp/retroarch-mappings.cfg'
        if os.path.isfile(mapping_config):
            with open(mapping_config) as f:
                for line in f:
                    conf_entry = line.split('=')
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
    def replace_tokens(self, value):
        value = value.strip()
        if value.startswith('${') and value.endswith('}') and self.game_data.get(value[2:-1]) is not None:
            return self.game_data.get(value[2:-1])

        return value

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

        self.game_data['core'] = os.path.join(self.get_config_value('Cores Location', True),
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
