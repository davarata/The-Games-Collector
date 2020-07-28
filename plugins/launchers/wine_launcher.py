import os
import subprocess
import sys

import time

from plugins.launchers.game_launcher import GameLauncher


class WINELauncher(GameLauncher):

    def set_target(self, descriptor):
        self.game_data['target'] = os.path.join(self.game_data['game_root'], 'drive_c', descriptor['Target'])

        if not os.path.isfile(self.game_data['target']):
            print('The target \'{}\' could not be found.'.format(self.game_data['target']))
            sys.exit(1)

    def launch_game(self):
        wine_env = os.environ.copy()
        wine_env['WINEDEBUG'] = '-all'
        wine_env['WINEPREFIX'] = self.game_data['game_root']
        wine_env['WINEARCH'] = "win32"
#        wine_env['DISPLAY'] = ':0.0'

        cmd = [self.get_executable(), self.game_data['target']]

        if self.launcher_params is not None and 'single_cpu' in self.launcher_params:
            cmd = ['schedtool', '-a', '0x2', '-e'] + cmd

        wine = subprocess.Popen(cmd, cwd=self.game_data['working_dir'], env=wine_env)
        self.wait(wine)

    def wait(self, process):
        if self.launcher_params is not None and 'use_alternate_wait' in self.launcher_params:
            time.sleep(4)

            path, *ignore = self.game_data['target'].rpartition('/')

            for pid in [pid for pid in os.listdir('/proc') if pid.isdigit()]:
                try:
                    if path == os.path.realpath('/proc/' + pid + '/cwd'):
                        while os.path.exists('/proc/' + pid):
                            time.sleep(1)
                        return
                except IOError:
                    continue
        else:
            process.wait()

    def configure_env(self):
        # Wine does not handle configuration like the rest of the launchers, so do not try to mess with the
        # configuration locations
        pass

    name = 'Wine'
    supported_implementations = {'Windows'}
    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution', 'specialization'}
    original_target = None
