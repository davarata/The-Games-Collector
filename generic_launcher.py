import os
import sys


class GenericLauncher:

    def configure_env(self):
        pass

    def get_name(self):
        pass

    def get_platform_description(self):
        return self.game_data.platform

    def launch_game(self):
        pass

    def revert_env(self):
        pass

    def set_game_root(self, game_properties):
        self.game_data.game_root = os.path.join(self.launcher_config['General']['Games Location'],
                                                game_properties['Game Root'])
        if not os.path.isdir(self.game_data.game_root):
            # TODO rewrite error message
            print('The game root could not be found in the games location.')
            sys.exit(1)

    # TODO get a better name
    def set_launcher_data(self, descriptor):
        pass

    def set_target(self, descriptor):
        self.game_data.target = os.path.join(self.game_data.game_root, descriptor['Target'])

        if not os.path.isfile(self.game_data.target):
            print('The target \'{}\' could not be found.'.format(self.game_data.target))
            sys.exit(1)

    def set_working_dir(self, descriptor):
        self.game_data.working_dir = self.game_data.target[:self.game_data.target.rfind(os.path.sep)]

    game_data = None
    launcher_params = None
    launcher_config = None