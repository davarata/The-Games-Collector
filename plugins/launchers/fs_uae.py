import os
import subprocess

from pathlib import Path

from config_manager import ConfigManager
from plugins.launchers.game_launcher import GameLauncher


class FSUAELauncher(GameLauncher):

    def launch_game(self):
        command = [self.get_executable()]
        command.extend(self.build_parameters())
        print(' '.join(command))
        subprocess.Popen(command).wait()

    def set_launcher_data(self, descriptor):
        # TODO verify model
        self.game_data['model'] = descriptor['Game']['Model']

        self.build_floppy_drive_params(descriptor)

        self.game_data['kickstart_location'] = self.get_config()['Launcher']['Kickstart Location']

        self.game_data['shader_location'] = self.get_config()['Launcher']['Shader Location']

        self.game_data['save_state_location'] = os.path.join(self.game_data['game_root'], 'Default')

    def build_parameters(self):
        parameters = [
            '--kickstarts_dir=' + self.game_data['kickstart_location'],
            '--amiga_model=' + self.game_data['model'],
            '--keep_aspect=1',
            '--fullscreen=1',
            '--save_states_dir=' + self.game_data['game_root'],
            '--load_state=1',
            '--floppy_drive_speed=0',
            # '--joystick_port_0=nothing',
            # '--joystick_port_0_mode=nothing',
            '--shader=' + os.path.join(self.game_data['shader_location'], 'scanline-4x.shader')
        ]
        parameters.extend(self.floppy_drive_params)

        return parameters

    def set_target(self, descriptor):
        pass

    def build_floppy_drive_params(self, descriptor):
        disks = [disk.strip() for disk in descriptor['Game']['Target'].split(',')]
        floppy_drive_params = []
        for i in range(0, len(disks)):
            floppy_drive = os.path.join(self.game_data['game_root'], disks[i])
            if not os.path.exists(floppy_drive):
                raise Exception('The floppy disk image \'{}\' could not be found.'.format(floppy_drive))

            floppy_drive_params.append('--floppy_drive_' + str(i) + '=' + floppy_drive)
            floppy_drive_params.append('--floppy_drive_' + str(i) + '_sounds=off')

        self.floppy_drive_params = floppy_drive_params

    def configure_env(self):
        if os.path.islink(self.game_data['save_state_location']):
            os.unlink(self.game_data['save_state_location'])
        Path(self.game_data['save_state_location']).symlink_to(self.game_data['game_root'])

    def revert_env(self):
        if os.path.islink(self.game_data['save_state_location']):
            os.unlink(self.game_data['save_state_location'])

    def set_working_dir(self, descriptor):
        pass

    def verify(self):
        self.verify_config(self.name, None)

    def verify_version(self, config_file):
        _ignore, version = config_file.split('_', 1)
        self.verify_config(config_file, version)

    def verify_config(self, config_file, version):
        config = ConfigManager.get_instance().load_config(config_file, save_config=False)

        self.verify_location_property(config['Launcher'], 'Kickstart Location', version)
        self.verify_location_property(config['Launcher'], 'Shader location', version)

    def verify_location_property(self, config, property, version):
        version_str = ''
        if config.get(property) is None:
            if version is not None:
                version_str = ' for version ' + version
            raise Exception('The property \'' + property + '\' was not found' + version_str)

        if not os.path.exists(config[property]):
            if version is not None:
                version_str = 'specified in version ' + version + ' '
            raise Exception('The ' + property.lower() + ' location ' + version_str + 'does not exist.')

    floppy_drive_params = []
    name = 'FS-UAE'
    supported_implementations = {'Amiga'}
    required_properties = {'developer', 'game root', 'genre', 'model', 'platform', 'target', 'title'}
    optional_properties = {
        'icon',
        'id',
        'included',
        'resolution',
        'specialization'
    }

    # amiga_models = {
    #     'A500',
    #     'A500+',
    #     'A600',
    #     'A1000',
    #     'A1200',
    #     'A1200/020',
    #     'A3000',
    #     'A4000/040',
    #     'CD32',
    #     'CDTV'
    # }
