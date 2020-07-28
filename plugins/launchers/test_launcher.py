import glob
import os
import subprocess
import sys
import time

from plugins.launchers.game_launcher import GameLauncher


class TestLauncher(GameLauncher):

    def launch_game(self):
        subprocess.Popen(self.get_executable())

    name = 'TestLauncher'
    supported_implementations = {
        'Test'
    }
    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {
        'id',
        'included',
        'launcher',
        'resolution',
        'specialization'
    }
