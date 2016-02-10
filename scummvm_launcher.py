import subprocess
from generic_launcher import GenericLauncher


class ScummVMLauncher(GenericLauncher):

    def get_name(self):
        return 'ScummVM'

    def launch_game(self):
        scummvm = subprocess.Popen(['scummvm', self.game_data.target], cwd=self.game_data.working_dir)
        scummvm.wait()

    def set_target(self, descriptor):
        self.game_data.target = descriptor['Target']

    def set_working_dir(self, descriptor):
        self.game_data.working_dir = self.game_data.game_root

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}
