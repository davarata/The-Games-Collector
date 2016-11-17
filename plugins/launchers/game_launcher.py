import os
import sys


# TODO remove any methods that simply get or set data. simply use variables.
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
        pass

    def get_platform_description(self):
        return self.game_data['platform']

    def launch_game(self):
        pass

    # TODO rename to
    def revert_env(self):
        pass

    name = None
    game_data = {}
    launcher_params = None
    launcher_config = None
