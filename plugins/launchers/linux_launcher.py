import subprocess
import sys

from plugins.launchers.game_launcher import GameLauncher


class LinuxLauncher(GameLauncher):

    def launch_game(self):
        if self.game_data.executable_type == 'script':
            subprocess.Popen(['sh', self.game_data.target]).wait()
        else:
            subprocess.Popen([self.game_data.target]).wait()

    def set_launcher_data(self, descriptor):
        if self.launcher_params is None or len(self.launcher_params) == 0:
            return

        if len(self.launcher_params) > 1:
            print('More than one parameter found for Linux launcher: ' + ' '.join(self.launcher_params))
            sys.exit(1)

        if not self.launcher_params[0].startswith('target'):
            print('Unknown parameter: ' + ' ' + self.launcher_params[0])
            sys.exit(1)

        type_param = [p.strip() for p in self.launcher_params[0].split('=')]
        if len(type_param) != 2:
            print('Syntax error: ' + ' ' + self.launcher_params[0])
            sys.exit(1)
        if type_param[1] not in ['script']:
            print('Unknown target type: ' + type_param[1])
            sys.exit(1)

        self.game_data.executable_type = 'script'

    name = 'Linux'
    supported_implementations = {'Linux'}

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution', 'specialization'}
