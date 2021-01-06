import math
import os
import subprocess
from pathlib import Path

from config_manager import ConfigManager
from plugins.launchers.game_launcher import GameLauncher


class RetroArchLauncher(GameLauncher):

    def get_platform_description(self):
        if self.game_data['platform'] == 'Arcade':
            return 'arcade machines'
        elif self.game_data['platform'] in self.consoles:
            return 'the ' + self.game_data['platform'] + ' console'
        elif self.game_data['platform'] in self.handhelds:
            return 'the ' + self.game_data['platform'] + ' handheld'
        else:
            return super(RetroArchLauncher, self).get_platform_description()

    def launch_game(self):
        game_config = self.game_data['target']
        if game_config.find('.') > 0:
            game_config = game_config[:game_config.rfind('.')]

        game_config = game_config + '.cfg'
        if os.path.isfile(game_config):
            with open(game_config) as f:
                for line in f:
                    conf_entry = line.split('=')
                    if len(conf_entry) > 1:
                        self.launch_config[conf_entry[0].strip()] = conf_entry[1].strip()

        mapping_config = '/tmp/retroarch-mappings.cfg'
        if os.path.isfile(mapping_config):
            with open(mapping_config) as f:
                for line in f:
                    conf_entry = line.split('=')
                    if len(conf_entry) > 1:
                        self.launch_config[conf_entry[0].strip()] = conf_entry[1].strip()

        config_file = open('/tmp/game-launcher.cfg', 'w')
        for key in sorted(self.launch_config.keys()):
            if key not in ['core', 'video_shader', 'savefile_directory', 'savestate_directory']:
                config_file.write(key + ' = ' + self.launch_config[key] + os.linesep)
        config_file.close()
        config_files = '/tmp/game-launcher.cfg'

        if self.game_data['platform'] == 'Arcade':
            *_ignore, target = self.game_data['target'].rpartition('/')
            target = 'roms/' + target
        elif self.game_data['core'] == 'scummvm_libretro.so':
            target = 'game'
        else:
            target = self.game_data['target']

        parameters = [
            self.get_executable(),
            target,
            '--libretro',
            self.game_data['core'],
            '--appendconfig',
            config_files]
        subprocess.Popen(parameters, cwd=self.game_data['working_dir']).wait()

    def configure_env(self):
        super().configure_env()

        core_path = self.get_config()['General'].get('Config location') + '/config/' + self.get_corename()
        if not os.path.isdir(core_path):
            os.mkdir(core_path)

        for l in ['states', 'saves']:
            if os.path.islink(self.get_config()['General'].get('Config location') + '/' + l):
                os.unlink(self.get_config()['General'].get('Config location') + '/' + l)
            Path(self.get_config()['General'].get('Config location') + '/' + l). \
                symlink_to(self.game_data['game_root'])

        game_name = self.game_data['target']
        if game_name.rfind('/') > 0:
            game_name = game_name[game_name.rfind('/') + 1:]
        if game_name.find('.') > 0:
            game_name = game_name[:game_name.rfind('.')]

        for e in (['cgp', 'glslp']):
            if os.path.isfile(core_path + '/' + game_name + '.' + e):
                os.remove(core_path + '/' + game_name + '.' + e)

        if self.get_retroarch_property('video_shader_enable', 'false') == 'true':
            video_shader = self.get_retroarch_property('video_shader')
            if video_shader != '':
                *_ignore, extension = video_shader.rpartition('.')

                shader_file = open(core_path + '/' + game_name + '.' + extension, 'w')
                shader_file.write('#reference "' + video_shader + '"')
                shader_file.close()

        if self.game_data['platform'] == 'Arcade': # used by mame2010
            Path(self.game_data['game_root'] + '/nvram').symlink_to(self.game_data['game_root'])
            Path(self.game_data['game_root'] + '/roms').symlink_to(self.game_data['game_root'])
            Path(self.game_data['game_root'] + '/cfg').symlink_to(self.game_data['game_root'])
        if self.game_data['core'].endswith('dosbox_libretro.so'):
            self.write_game_opt(game_name)
        if self.game_data['core'].endswith('scummvm_libretro.so'):
            if os.path.islink(self.get_config()['ScummVM'].get('Config location')):
                os.unlink(self.get_config()['ScummVM'].get('Config location'))

            if os.path.exists(self.get_config()['ScummVM'].get('Config location')):
                raise Exception('The configuration location \'' + self.get_config()['ScummVM'].get(
                    'Config location') + '\' exists.')

            Path(self.get_config()['ScummVM'].get('Config location')).symlink_to(self.game_data['game_root'])

    def revert_env(self):
        super().revert_env()
        if self.game_data['platform'] == 'Arcade': # used by mame2010
            os.unlink(os.path.join(self.game_data['game_root'], 'nvram'))
            os.unlink(os.path.join(self.game_data['game_root'], 'roms'))
            os.unlink(os.path.join(self.game_data['game_root'], 'cfg'))
        if self.game_data['core'].endswith('scummvm_libretro.so'):
            os.unlink(self.get_config()['ScummVM'].get('Config location'))

    def set_launcher_data(self, descriptor):
        self.game_data['core'] = self.get_retroarch_property('core')

        if self.game_data.get('core') is None:
            self.game_data['core'] = self.get_config()[self.game_data['platform']]['Core']

        core_file = os.path.join(self.get_config()['Launcher']['Cores Location'], self.game_data['core'] + '.so')
        if not os.path.isfile(core_file):
            raise Exception('Unknown core: ' + self.game_data['core'])

        self.game_data['core'] = core_file

    def verify_version(self, config_file):
        super().verify_version(config_file)

        config = ConfigManager.get_instance().load_config(config_file, save_config=False)

        _ignore, version = config_file.split('_', 1)

        if config['Launcher'].get('Cores Location') is None:
            raise Exception('The property \'Cores Location\' was not found for ' + self.name + ' version ' + version)

        if not os.path.exists(config['Launcher']['Cores Location']):
            raise Exception('The cores location path \'' + config['Launcher']['Cores Location'] + '\' specified in ' + self.name +
                            ' version ' + version + ' does not exist.')

    def get_retroarch_property(self, name, value = ''):
        game_config = self.game_data['target']
        if game_config.find('.') > 0:
            game_config = game_config[:game_config.rfind('.')]
        game_config = game_config + '.cfg'

        if os.path.isfile(game_config):
            with open(game_config) as f:
                for line in f:
                    entries = line.split("=")
                    if entries[0].strip().lower() == name.lower():
                        return entries[1].replace('"', '').strip()

        config = self.get_config()
        if config is not None and config.has_section(self.game_data['platform']):
            platform_config = config[self.game_data['platform']]
            for key in platform_config.keys():
                if key.lower() == name.lower():
                    return platform_config[key].replace('"', '').strip()

        with open(self.get_config()['General'].get('Config location') + '/retroarch.cfg') as f:
            for line in f:
                entries = line.split("=")
                if entries[0].strip().lower() == name.lower():
                    return entries[1].replace('"', '').strip()

        return value

    def get_corename(self):
        core = self.get_retroarch_property('core')

        coreinfo = ConfigManager.get_instance().get_config('coreinfo')
        if coreinfo is None:
            coreinfo = ConfigManager.get_instance().load_config('cores', extension='info', skip_inst_dir=True)

        if coreinfo is not None:
            if core is not None and coreinfo.has_section(core):
                return coreinfo[core]['corename'].replace('"', '')

        config = self.get_config()
        if config is not None and config.has_section(self.game_data['platform']):
            info_file = config['Launcher']['cores location'] + '/' + core + '.info'

            with open(info_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('corename'):
                        *_ignore, corename = line.rpartition('=')
                        corename = corename.replace('"', '')
                        return corename.strip()

        return ''

    def write_game_opt(self, game_name):
        dosbox_cpu_core = 'auto'
        dosbox_cpu_cycles = 1
        dosbox_cpu_cycles_multiplier = 1000
        dosbox_cpu_type = 'auto'
        dosbox_disney = 'false'
        dosbox_machine_type = 'svga_s3'
        dosbox_pcspeaker = 'false'
        dosbox_sblaster_base = '220'
        dosbox_sblaster_dma = '1'
        dosbox_sblaster_hdma = '7'
        dosbox_sblaster_irq = '5'
        dosbox_sblaster_opl_emu = 'default'
        dosbox_sblaster_opl_mode = 'auto'
        dosbox_sblaster_type = 'sb16'
        dosbox_scaler = 'none'
        dosbox_tandy = 'auto'

        if self.game_data['target'].endswith('.conf'):
            with open(self.game_data['target']) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('machine'):
                        dosbox_machine_type = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('scaler'):
                        dosbox_scaler = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('core'):
                        dosbox_cpu_core = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('cycles'):
                        dosbox_cpu_cycles_multiplier = 1000

                        cpu_cycles = int(line[line.rfind('=') + 1:].replace('"', ''))
                        if cpu_cycles < 9000:
                            dosbox_cpu_cycles_multiplier = 1000
                        elif cpu_cycles < 90000:
                            dosbox_cpu_cycles_multiplier = 10000
                        elif cpu_cycles < 900000:
                            dosbox_cpu_cycles_multiplier = 100000

                        dosbox_cpu_cycles = math.ceil(cpu_cycles / dosbox_cpu_cycles_multiplier)
                    if line.startswith('cputype'):
                        dosbox_cpu_type = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('sbtype'):
                        dosbox_sblaster_type = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('sbbase'):
                        dosbox_sblaster_base = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('irq'):
                        dosbox_sblaster_irq = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('dma'):
                        dosbox_sblaster_dma = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('hdma'):
                        dosbox_sblaster_hdma = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('oplmode'):
                        dosbox_sblaster_opl_mode = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('oplemu'):
                        dosbox_sblaster_opl_emu = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('pcspeaker'):
                        dosbox_pcspeaker = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('tandy') and not line.startswith('tandyrate'):
                        dosbox_tandy = line[line.rfind('=') + 1:].replace('"', '')
                    if line.startswith('disney'):
                        dosbox_disney = line[line.rfind('=') + 1:].replace('"', '')

        core_path = self.get_config()['General'].get('Config location') + '/config/' + self.get_corename()
        game_opt_file = open(self.get_config()['General'].get('Config location') + '/config/' + self.get_corename() +
                             '/' + game_name + '.opt', 'w')
        game_opt_file.write('dosbox_adv_options = "true"' + os.linesep)
        game_opt_file.write('dosbox_cpu_core = "' + dosbox_cpu_core + '"' + os.linesep)
        game_opt_file.write('dosbox_cpu_cycles = "' + str(dosbox_cpu_cycles) + '"' + os.linesep)
        game_opt_file.write('dosbox_cpu_cycles_fine = "1"' + os.linesep)
        game_opt_file.write('dosbox_cpu_cycles_mode = "fixed"' + os.linesep)
        game_opt_file.write('dosbox_cpu_cycles_multiplier = "' + str(dosbox_cpu_cycles_multiplier) + '"' + os.linesep)
        game_opt_file.write('dosbox_cpu_cycles_multiplier_fine = "1"' + os.linesep)
        game_opt_file.write('dosbox_cpu_type = "' + dosbox_cpu_type + '"' + os.linesep)
        game_opt_file.write('dosbox_disney = "' + dosbox_disney + '"' + os.linesep)
        game_opt_file.write('dosbox_emulated_mouse = "enable"' + os.linesep)
        game_opt_file.write('dosbox_emulated_mouse_deadzone = "5%"' + os.linesep)
        game_opt_file.write('dosbox_machine_type = "' + dosbox_machine_type + '"' + os.linesep)
        game_opt_file.write('dosbox_pcspeaker = "' + dosbox_pcspeaker + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_base = "' + dosbox_sblaster_base + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_dma = "' + dosbox_sblaster_dma + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_hdma = "' + dosbox_sblaster_hdma + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_irq = "' + dosbox_sblaster_irq + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_opl_emu = "' + dosbox_sblaster_opl_emu + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_opl_mode = "' + dosbox_sblaster_opl_mode + '"' + os.linesep)
        game_opt_file.write('dosbox_sblaster_type = "' + dosbox_sblaster_type + '"' + os.linesep)
        game_opt_file.write('dosbox_scaler = "' + dosbox_scaler + '"' + os.linesep)
        game_opt_file.write('dosbox_tandy = "' + dosbox_tandy + '"' + os.linesep)
        game_opt_file.write('dosbox_use_options = "true"' + os.linesep)
        game_opt_file.close()

    name = 'RetroArch'

    # TODO remove this. It can be derived from the cores saved in the RetroArch.cfg file.
    supported_implementations = {
        'Arcade',
        'DOS',
        'Master System',
        'Mega Drive',
        'NES',
        'SNES',
        'Game Boy Advance',
        'N64',
        'ScummVM'
    }

    required_properties = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    optional_properties = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}

    launch_config = {}

    consoles = {
        'Master System',
        'Mega Drive',
        'Nintendo Entertainment System',
        'SNES',
        'N64'
    }

    handhelds = {'Game Boy Advance'}
