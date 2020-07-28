import subprocess

from plugins.launchers.game_launcher import GameLauncher


class VirtualBoxLauncher(GameLauncher):

    def set_target(self, descriptor):
        self.game_data['target'] = descriptor['Target']

    def launch_game(self):
        cmd = [self.get_executable(), '--startvm', self.game_data['target']]

        subprocess.Popen(cmd).wait()

    def set_game_root(self, game_properties):
        pass

    name = 'VirtualBox'
    supported_implementations = {'Windows'}
    required_properties = {'developer', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution', 'specialization'}
