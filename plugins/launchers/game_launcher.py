import os
import sys


# TODO remove any methods that simply get or set data. simply use variables.
from pathlib import Path

from config_manager import ConfigManager
from plugins.plugin_handler import Plugin


class GameLauncher(Plugin):

    def init(self, install_dir):
        self.install_dir = install_dir
        self.load_plugins('plugins.launchers', GameLauncher)
        ConfigManager.get_instance().set_config('Game Config', self.game_data)

    def set_game_root(self, game_properties):
        self.game_data['game_root'] = os.path.join(self.launcher_config['General']['Games Location'],
                                                   game_properties['Game Root'])
        if not os.path.isdir(self.game_data['game_root']):
            # TODO rewrite error message
            print('The game root could not be found in the games location.')
            sys.exit(1)

    def set_target(self, descriptor):
        self.game_data['target'] = os.path.join(self.game_data['game_root'], descriptor['Target'])

        if not os.path.isfile(self.game_data['target']):
            print('The target \'{}\' could not be found.'.format(self.game_data['target']))
            sys.exit(1)

    def set_working_dir(self, descriptor):
        self.game_data['working_dir'] = self.game_data['target'][:self.game_data['target'].rfind(os.path.sep)]

    # TODO get a better name
    def set_launcher_data(self, descriptor):
        pass

    def configure_env(self):
        if os.path.islink(self.get_config()['General'].get('Config location')):
            os.unlink(self.get_config()['General'].get('Config location'))

        if os.path.exists(self.get_config()['General'].get('Config location')):
            raise Exception('The configuration location \'' + self.get_config()['General'].get('Config location') +
                            '\' exists.')

        if self.version is None:
            return

        if not os.path.exists(self.get_config()['General'].get('Config location') + '_' + self.version):
            raise Exception('Path ' + self.get_config()['General'].get('Config location') + '_' + self.version +
                            ' does not exist.')

        Path(self.get_config()['General'].get('Config location')).\
            symlink_to(self.get_config()['General'].get('Config location') + '_' + self.version)

    def get_platform_description(self):
        return self.game_data['platform']

    def launch_game(self):
        pass

    # TODO rename to
    def revert_env(self):
        if os.path.islink(self.get_config()['General'].get('Config Location')):
            os.unlink(self.get_config()['General'].get('Config Location'))

    def verify_version(self, config_file):
        config = ConfigManager.get_instance().load_config(config_file, save_config=False)
        _ignore, version = config_file.split('_', 1)

        if config['Launcher'].get('Executable') is None:
            raise Exception('Executable property not found for ' + self.name + ' version ' + version)
        if not os.path.exists(config['Launcher']['Executable']):
            raise Exception('Executable \'' + config['Executable'] + '\' not found for ' +
                            self.name + ' version ' + version)

    def verify_versions(self):
        super().verify_versions()

        config = ConfigManager.get_instance().load_config(self.get_plugin_name(), save_config=False)

        if config is None:
            return

        if not config.has_section('General'):
            raise Exception('Configuration file for ' + self.name + ' does not contain a General section.')
        if config['General'].get('Config Location') is None:
            raise Exception('Config location property not found for ' + self.name + '.')

    def get_executable(self):
        return self.get_config()['Launcher']['Executable']

    name = None
    # TODO remove game_data. This should be referenced using ConfigManager
    game_data = {}
    launcher_params = None
    launcher_config = None
