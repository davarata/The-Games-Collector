import glob
import os
import subprocess
import sys
import time

from plugins.launchers.game_launcher import GameLauncher


class DOSBoxLauncher(GameLauncher):

    def launch_game(self):
        if self.game_data.soundfont is not None:
            file = open('/tmp/timidity.cfg', 'w')
            file.write('soundfont "' + self.game_data.soundfont + '"\n')
            file.close()

            self.timidity = subprocess.Popen(['timidity', '-iA', '-c', '/tmp/timidity.cfg'])
            time.sleep(1)

        subprocess.Popen(['dosbox', '-conf', self.game_data.target]).wait()

    def revert_env(self):
        if self.game_data.soundfont is not None:
            self.timidity.kill()

    def set_launcher_data(self, descriptor):
        game_properties = descriptor['Game']

        if game_properties.get('Disk Image') is None:
            self.game_data.disk_image = None
        else:
            self.game_data.disk_image = game_properties['Disk Image']

            files = glob.glob(os.path.join(
                self.launcher_config['General']['Games Location'],
                game_properties['Game Root'],
                self.game_data.disk_image + '.*'))
            if len(files) == 0:
                print('The disk image files could not be found.')
                sys.exit(1)

        if game_properties.get('SoundFont') is None:
            self.game_data.soundfont = None
        else:
            self.game_data.soundfont = os.path.join(self.launcher_config['DOS']['SoundFont Location'],
                                                    game_properties['SoundFont'] + '.sf2')
            if not os.path.isfile(self.game_data.soundfont):
                print('The sound font could not be found.')
                sys.exit(1)

    name = 'DOSBox'
    timidity = None
    supported_implementations = {'DOS'}
    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'disk image', 'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution',
                           'soundfont', 'specialization'}
