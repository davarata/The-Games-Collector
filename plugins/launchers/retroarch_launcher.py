import os
import subprocess
from pathlib import Path

from config_manager import ConfigManager
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

        game_config = self.game_data['target']
        if game_config.find('.') > 0:
            game_config = game_config[:game_config.rfind('.')]

        game_config = game_config + '.cfg'
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

        if self.game_data['platform'] == 'Arcade':
            *_ignore, target = self.game_data['target'].rpartition('/')
            target = 'roms/' + target
        elif self.game_data['core'] == 'scummvm_libretro.so':
            target = 'game'
        else:
            target = self.game_data['target']

        parameters = [
            self.get_executable(),
            target,
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
        super().configure_env()
        if self.game_data['platform'] == 'Arcade':
            Path(self.game_data['game_root'] + '/nvram').symlink_to(self.game_data['game_root'])
            Path(self.game_data['game_root'] + '/roms').symlink_to(self.game_data['game_root'])
            Path(self.game_data['game_root'] + '/cfg').symlink_to(self.game_data['game_root'])
        if self.game_data['core'].endswith('scummvm_libretro.so'):
            if os.path.islink(self.get_config()['ScummVM'].get('Config location')):
                os.unlink(self.get_config()['ScummVM'].get('Config location'))

            if os.path.exists(self.get_config()['ScummVM'].get('Config location')):
                raise Exception('The configuration location \'' + self.get_config()['ScummVM'].get(
                    'Config location') + '\' exists.')

            Path(self.get_config()['ScummVM'].get('Config location')).symlink_to(self.game_data['game_root'])

    def revert_env(self):
        super().revert_env()
        if self.game_data['platform'] == 'Arcade':
            os.unlink(os.path.join(self.game_data['game_root'], 'nvram'))
            os.unlink(os.path.join(self.game_data['game_root'], 'roms'))
            os.unlink(os.path.join(self.game_data['game_root'], 'cfg'))
        if self.game_data['core'].endswith('scummvm_libretro.so'):
            os.unlink(self.get_config()['ScummVM'].get('Config location'))

    def set_launcher_data(self, descriptor):
        if self.launcher_params is not None:
            for param in self.launcher_params:
                if param.startswith('core'):
                    self.game_data['core'] = param.split('=')[1].strip()

        if self.game_data.get('core') is None:
            self.game_data['core'] = self.get_config()[self.game_data['platform']]['Core']

        found_core = False
        for implementation in self.supported_implementations:
            core = self.get_config()[implementation].get('Core')
            if core is not None and core == self.game_data['core']:
                found_core = True

        if not found_core:
            raise Exception('Unknown core: ' + self.game_data['core'])

        self.game_data['core'] = os.path.join(self.get_config()['Launcher']['Cores Location'],
                                              self.game_data['core'] + '.so')

    def verify_version(self, config_file):
        super().verify_version(config_file)

        config = ConfigManager.get_instance().load_config(config_file, save_config=False)

        _ignore, version = config_file.split('_', 1)

        if config['Launcher'].get('Cores Location') is None:
            raise Exception('The property \'Cores Location\' was not found for ' + self.name + ' version ' + version)

        if not os.path.exists(config['Launcher']['Cores Location']):
            raise Exception('The cores location path \'' + config['Launcher']['Cores Location'] + '\' specified in ' + self.name +
                            ' version ' + version + ' does not exist.')

    name = 'RetroArch'

    # TODO remove this. It can be derived from the cores saved in the RetroArch.cfg file.
    supported_implementations = {
        'Arcade',
        'DOS',
        'Master System',
        'Mega Drive',
        'NES',
        'SNES',
        'Game Boy Advance',
        'N64',
        'ScummVM'
    }

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}

    launch_config = {}

    consoles = {
        'Master System',
        'Mega Drive',
        'Nintendo Entertainment System',
        'SNES',
        'N64'
    }

    handhelds = {'Game Boy Advance'}
