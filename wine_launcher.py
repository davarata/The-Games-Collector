import os
import subprocess
import sys
from generic_launcher import GenericLauncher


class WINELauncher(GenericLauncher):

    def get_name(self):
        return 'Wine'

    def set_target(self, descriptor):
        self.game_data.target = os.path.join(self.game_data.game_root, 'drive_c', descriptor['Target'])

        if not os.path.isfile(self.game_data.target):
            print('The target \'{}\' could not be found.'.format(self.game_data.target))
            sys.exit(1)

    def launch_game(self):
        print('Launching wine game')
        wine_env = os.environ.copy()
        wine_env['WINEDEBUG'] = '-all'
        wine_env['WINEPREFIX'] = self.game_data.game_root

        cmd = ['wine', self.game_data.target]

        if self.launcher_params is not None and 'SINGLE_CPU' in self.launcher_params:
            cmd = ['schedtool', '-a', '0x2', '-e'] + cmd
        wine = subprocess.Popen(cmd, cwd=self.game_data.working_dir, env=wine_env)
        wine.wait()

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution', 'specialization'}
