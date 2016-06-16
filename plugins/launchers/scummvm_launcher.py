import subprocess

from plugins.launchers.game_launcher import GameLauncher


class ScummVMLauncher(GameLauncher):

    def launch_game(self):
        subprocess.Popen(['scummvm', self.game_data.target], cwd=self.game_data.working_dir).wait()

    def set_target(self, descriptor):
        self.game_data.target = descriptor['Target']

    def set_working_dir(self, descriptor):
        self.game_data.working_dir = self.game_data.game_root

    name = 'ScummVM'
    supported_implementations = {'DOS', 'Windows'}
    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}
