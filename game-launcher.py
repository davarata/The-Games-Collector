import argparse
import configparser
import glob
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from gi.repository import Gtk, Gdk


class Struct():
    pass


class LauncherData():
    pass


def load_globals():
    global descriptor_data

    wine = LauncherData()
    wine.required = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    wine.optional = {'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution', 'specialization'}

    dosbox = LauncherData()
    dosbox.required = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    dosbox.optional = {'disk image', 'icon', 'id', 'included', 'launcher', 'optical disk', 'resolution', 'soundfont', 'specialization', 'antimicro profile'}

    retroarch = LauncherData()
    retroarch.required = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    retroarch.optional = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization', 'antimicro profile'}

    scummvm = LauncherData()
    scummvm.required = {'developer', 'game root', 'genre', 'platform', 'target', 'title'}
    scummvm.optional = {'icon', 'id', 'included', 'launcher', 'resolution', 'specialization'}

    descriptor_data = {'DOSBox': dosbox, 'RetroArch': retroarch, 'ScummVM': scummvm, 'Wine': wine}

    global retroarch_cores
    retroarch_cores = {'Arcade': 'mame078_libretro',
                       'DOS': 'dosbox_libretro',
                       'Mega Drive': 'picodrive_libretro',  #
                       'NES': 'fceumm_libretro',
                       'SNES': 'snes9x_libretro',
                       'Game Boy Advance': 'vba_next_libretro',
                       'N64': 'mupen64plus_libretro'}

    global consoles
    consoles = {'Mega Drive',
                'Nintendo Entertainment System',
                'SNES',
                'Nintendo 64'}

    global handhelds
    handhelds = {'Game Boy Advance'}

    global missing_property
    missing_property = 'The \'{}\' property is required by the {}'

    global platforms
    platforms = {'DOS': ['DOSBox', 'RetroArch', 'ScummVM'],
                 'Windows': ['Wine'],
                 'Arcade': ['RetroArch'],
                 'Mega Drive': ['RetroArch'],
                 'NES': ['RetroArch'],
                 'SNES': ['RetroArch'],
                 'Game Boy Advance': ['RetroArch'],
                 'N64': ['RetroArch']}

    global virtual_target_platforms
    virtual_target_platforms = {'ScummVM'}


def add_launcher_conf(game, descriptor, games_location):
    # game.platform = descriptor['Platform']
    # game.launcher = descriptor['Launcher']

    game.game_root = os.path.join(games_location, descriptor['Game Root'])
    if not os.path.isdir(game.game_root):
        print('The game root could not be found in the games location.')
        sys.exit(1)

    if game.launcher in virtual_target_platforms:
        game.target = descriptor['Target']
        game.working_dir = game.game_root
    else:
        if game.launcher == 'Wine':
            game.target = os.path.join(game.game_root, 'drive_c', descriptor['Target'])
        else:
            game.target = os.path.join(game.game_root, descriptor['Target'])

        if game.launcher != 'ScummVM' and not os.path.isfile(game.target):
            print('The target \'{}\' could not be found.'.format(game.target))
            sys.exit(1)
        game.working_dir = game.target[:game.target.rfind(os.path.sep)]

    if descriptor.get('Resolution') is None:
        game.resolution = None
    else:
        game.resolution = descriptor['Resolution']
        # TODO sort out WIDTHxHEIGHT (alt)
        # if game.resolution not in {'640x480', '800x600', '1024x768', '1152x864', '1280x1024'}:
        #     print('Unknown resolution: \'{}\'.'.format(game.resolution))

    if descriptor.get('Optical Disk') is None:
        game.optical_disk = None
    else:
        game.optical_disk = descriptor['Optical Disk']

    # This is a quick-fix hack to play keyboard games using game pad now
    if descriptor.get('AntiMicro Profile') is None:
        game.antimicro_profile = None
    else:
        game.antimicro_profile = os.path.join(game.game_root, descriptor['AntiMicro Profile'])


def add_menu_conf(game, descriptor):
    game.title = descriptor['Title']

    # TODO add check for genres
    game.genre = descriptor['Genre']

    game.developer = descriptor['Developer']

    if descriptor.get('Specialization') is None:
        game.specialization = None
    else:
        game.specialization = descriptor['Specialization']

    if descriptor.get('Included') is None:
        game.included = None
    else:
        descriptor.included = descriptor['Included']

    if descriptor.get('Icon') is None:
        game.icon = None
    else:
        game.icon = descriptor['Icon']


def add_dosbox_conf(game, descriptor, config):
    if game.launcher != 'DOSBox':
        return

    if descriptor.get('Disk Image') is None:
        game.disk_image = None
    else:
        game.disk_image = descriptor['Disk Image']
        files = glob.glob(os.path.join(config['DOS']['Disk Images Location'], game.disk_image + '.*'))
        if len(files) == 0:
            print('The disk image files could not be found.')
            sys.exit(1)

    if descriptor.get('SoundFont') is None:
        game.soundfont = None
    else:
        game.soundfont = os.path.join(config['DOS']['SoundFont Location'], descriptor['SoundFont'] + '.sf2')
        if not os.path.isfile(game.soundfont):
            print('The sound font could not be found.')
            sys.exit(1)


def add_retroarch_conf(game, config):
    if game.launcher != 'RetroArch':
        return

    if game.launcher_params is None or len(game.launcher_params) == 0:
        game.core = retroarch_cores[game.platform]
    elif len(game.launcher_params) == 1:
        game.core = game.launcher_params[0]
    else:
        print('More than one parameter found for RetroArch launcher: ' + ' '.join(game.launcher_params))
        sys.exit(1)

    if game.core not in retroarch_cores.values():
        print('Unknown core: ' + game.core)

    game.core = os.path.join(config['RetroArch']['Cores Location'], game.core + '.so')


# TODO finish!
def add_wine_conf(game, config):
    if len(game.launcher_params) == 1:
        game.core = game.launcher_params[0]


def check_expected_properties(game, descriptor):
    if descriptor.get('Platform') is None or len(descriptor['Platform']) == 0:
        print('The \'Platform\' property is required.')
        sys.exit(1)

    game.platform = descriptor['Platform']
    if game.platform not in platforms.keys():
        print('Unknown platform: ' + game.platform)
        sys.exit(1)

    # This section should actually go in add_launcher_conf, but launcher_desc requires it here...
    if descriptor.get('Launcher') is None or len(descriptor['Launcher']) == 0:
        game.launcher = platforms[game.platform][0]
        game.launcher_params = None
        launcher_desc = game.launcher + ' platform.'
    else:
        game.launcher, *game.launcher_params = [p.strip() for p in descriptor['Launcher'].split(',')]
        if game.launcher not in platforms[game.platform]:
            print(game.platform + ' games cannot be launched with ' + game.launcher)

        launcher_desc = game.launcher + ' launcher.'

    properties = set(descriptor)
    required = descriptor_data[game.launcher].required
    optional = descriptor_data[game.launcher].optional

    missing = required.difference(properties)
    if len(missing) > 0:
        for property in missing:
            print(missing_property.format(property, launcher_desc))
            sys.exit(1)

    unneeded = properties.difference(required, optional)
    if len(unneeded) > 0:
        for property in unneeded:
            print('The \'' + property + '\' property is not used by the ' + launcher_desc)
            sys.exit(1)

    for property in required:
        if len(descriptor.get(property)) == 0:
            print(missing_property.format(property, launcher_desc))
            sys.exit(1)

    for property in properties:
        if len(descriptor.get(property)) == 0:
            print('The property \'${}\' is empty.'.format(property))
            sys.exit(1)


def verify_descriptor(descriptor, config):
    game_descriptor = descriptor['Game']

    game = Struct()

    check_expected_properties(game, game_descriptor)

    add_launcher_conf(game, game_descriptor, config['General']['Games Location'])

    add_menu_conf(game, game_descriptor)

    add_dosbox_conf(game, game_descriptor, config)

    add_retroarch_conf(game, config)

    return game


def launch_dosbox_game(game):
    if game.soundfont is not None:
        file = open('/tmp/timidity.cfg', 'w')
        file.write('soundfont "' + game.soundfont + '"\n')
        file.close()

        timidity = subprocess.Popen(['timidity', '-iA', '-c', '/tmp/timidity.cfg'])
        time.sleep(1)

    # This is a quick-fix hack to play keyboard games using game pad now
    if game.antimicro_profile is not None:
        antimicro = subprocess.Popen(['antimicro', '--hidden', '--profile', game.antimicro_profile])

    dosbox = subprocess.Popen(['dosbox', '-conf', game.target])
    dosbox.wait()

    # This is a quick-fix hack to play keyboard games using game pad now
    if game.antimicro_profile is not None:
        antimicro.kill()

    if game.soundfont is not None:
        timidity.kill()


def replace_tokens(line, game_data):
    if line.strip().startswith('#'):
        modified_line = line.partition(' ')[2].strip()
        if modified_line.startswith('@game-launcher[\'') and modified_line.endswith('\']'):
            modified_line = modified_line[16:-2]
            modified_line = modified_line.replace('${game_root}', '"' + game_data.game_root + '"')
            return modified_line + '\n'
        else:
            return line
    else:
        return line


def launch_retroarch_game(game):
    launch_config = {}

    platform_config = os.path.join(game.platform_config, game.platform + '.cfg')
    if os.path.isfile(platform_config):
        with open(platform_config) as f:
            for line in f:
                conf_entry = replace_tokens(line, game).split('=')
                if len(conf_entry) > 1:
                    launch_config[conf_entry[0].strip()] = conf_entry[1]

    game_config = game.target[:game.target.rfind('.')] + '.cfg'
    if os.path.isfile(game_config):
        with open(game_config) as f:
            for line in f:
                conf_entry = replace_tokens(line, game).split('=')
                if len(conf_entry) > 1:
                    launch_config[conf_entry[0].strip()] = conf_entry[1]

    config_file = open('/tmp/game-launcher.cfg', 'w')
    for key in launch_config.keys():
        config_file.write(key + ' = ' + launch_config[key])
    config_file.close()

    if game.platform == 'Arcade':
        nvram = Path(game.games_location + '/nvram')
        nvram.symlink_to(game.game_root)

    # This is a quick-fix hack to speed up playing keyboard games using game pad
    if game.antimicro_profile is not None:
        antimicro = subprocess.Popen(['antimicro', '--hidden', '--profile', game.antimicro_profile])

    proc_params = ['retroarch', game.target, '--libretro', game.core, '--appendconfig', '/tmp/game-launcher.cfg']
    print(" ".join(proc_params))
    retroarch = subprocess.Popen(proc_params, cwd=game.working_dir)
    retroarch.wait()

    # This is a quick-fix hack to speed up playing keyboard games using game pad
    if game.antimicro_profile is not None:
        antimicro.kill()

    if game.platform == 'Arcade':
        os.unlink(os.path.join(game.games_location, 'nvram'))


def launch_wine_game(game):
    wine_env = os.environ.copy()
    wine_env['WINEDEBUG'] = '-all'
    wine_env['WINEPREFIX'] = game.game_root

    cmd = ['wine', game.target]

    if game.launcher_params is not None and 'SINGLE_CPU' in game.launcher_params:
        cmd = ['schedtool', '-a', '0x2', '-e'] + cmd
    print(' '.join(cmd))
    wine = subprocess.Popen(cmd, cwd=game.working_dir, env=wine_env)
    wine.wait()


def launch_scummvm_game(game):
    scummvm = subprocess.Popen(['scummvm', game.target], cwd=game.working_dir)
    scummvm.wait()


def launch_game(id):
    game_descriptor = configparser.ConfigParser()
    game_descriptor.read('/home/rebit/.config/game-launcher/' + id + '.game')
    game = game_descriptor['Game']

    config = configparser.ConfigParser()
    config.read('/home/rebit/.config/game-launcher/game-launcher.cfg')

    game_data = verify_descriptor(game_descriptor, config)

    if game_data.optical_disk is not None:
        message = '\nPlease insert the optical disk with the label \'' + game['Optical Disk'].rpartition('/')[2] + '\''

        # temp hack. Add icon to game_data
        game_data.icon = id
        game_dialog = get_game_dialog(game_data, config, message)

        missing = not os.path.isdir(game_data.optical_disk)
        while missing:
            game_dialog.show_all()
            response = game_dialog.run()

            if response == -4:
                game_dialog.destroy()
                sys.exit(1)

            missing = not os.path.isdir(game_data.optical_disk)

        game_dialog.destroy()

    if game_data.resolution is not None:
        subprocess.call(['/usr/bin/xrandr', '-s', game_data.resolution])

    game_data.games_location = config['General']['Games Location']
    if game_data.launcher == 'DOSBox':
        launch_dosbox_game(game_data)
    elif game_data.launcher == 'RetroArch':
        game_data.platform_config = config['General']['Platform Config']
        launch_retroarch_game(game_data)
    elif game_data.launcher == 'Wine':
        launch_wine_game(game_data)
    elif game_data.launcher == 'ScummVM':
        launch_scummvm_game(game_data)


def add_icon(icon_file, config):
    if not os.path.isfile(icon_file):
        print('Icon file ' + icon_file + ' does not exist.')
        sys.exit(1)

    if not icon_file.endswith('.svg'):
        print('Wrong extension type.')

    icon_conf = config['Icons']
    name = icon_file[icon_file.rfind('/') + 1: len(icon_file) - 4]
    for size in icon_conf['Icon Sizes'].split(','):
        icon_location = icon_conf['Icons Location'] + '/' + icon_conf['Icon Path Pattern'].replace('__size__', size)
        subprocess.call(['inkscape', '-w=' + size, '-h=' + size, icon_file, '-e', icon_location + '/' + name + '.png'])


def add_descriptor(game_desc_file):
    shutil.copyfile(game_desc_file, '/home/rebit/.config/game-launcher/' + game_desc_file.rpartition('/')[2])


def add_menu_entry(game, config):
    if game['Platform'] == 'DOS':
        platform = 'DOS'
    elif game['Platform'] == 'Windows':
        platform = 'Windows'
    elif game['Platform'] in retroarch_cores.keys():
        if game['Platform'] == 'Arcade':
            platform = 'arcade machines'
        elif game['Platform'] in consoles:
            platform = 'the ' + game['Platform'] + ' console'
        elif game['Platform'] in handhelds:
            platform = 'the ' + game['Platform'] + ' handheld'

    genre = game['Genre'].replace('[', '').replace(']', '').replace(',', ' ').capitalize()
    if game.get('Specialization') is not None and len(game['Specialization']) > 0:
        if game['Specialization'] == 'Collection':
            comment = 'Collection of ' + genre.lower() + ' games'
        if game['Specialization'] == 'Expansion':
            comment = 'Expansion for the ' + genre.lower() + ' game'
    else:
        comment = genre + ' game'
    comment += ' by ' + game['Developer'] + ' for ' + platform

    if game.get('Included') is not None and len(game['Included']) > 0:
        comment += '. '
        *included_games, last_included_game = [i.strip() for i in game['Included'].split(',')]
        if len(included_games) == 0:
            comment += last_included_game + ' included'
        else:
            comment += ', '.join(included_games) + ' and ' + last_included_game + ' included'

    reordered_genres = []
    for genre in game['Genre'].split(','):
        if genre.startswith('[') and genre.endswith(']'):
            reordered_genres.insert(0, genre.strip('[]'))
        else:
            reordered_genres.append(genre)
    genres = []
    for genre in reordered_genres:
        genres.append(''.join([word.capitalize() for word in genre.replace('-', ' ').split(' ')]))

    menu_entry = configparser.ConfigParser()
    menu_entry.optionxform = str
    menu_entry.add_section('Desktop Entry')
    menu_entry.set('Desktop Entry', 'Type', 'Application')
    menu_entry.set('Desktop Entry', 'Name', game['Title'])
    menu_entry.set('Desktop Entry', 'Comment', comment)
    if game.get('Icon') is not None and len(game['Icon']) > 0:
        menu_entry.set('Desktop Entry', 'Icon', game['Icon'])
    else:
        menu_entry.set('Desktop Entry', 'Icon', game['ID'])
    menu_entry.set('Desktop Entry', 'Exec', 'game-launcher launch ' + game['ID'])
    menu_entry.set('Desktop Entry', 'Terminal', 'false')
    menu_entry.set('Desktop Entry', 'Categories', 'Game;' + ';'.join(genres))

    menu_entry.write(open(config['General']['Menu Destination'] + '/' + game['ID'] + '.desktop', 'w'), False)


def add_game(game_desc_file, icon_file):
    if not os.path.isfile(game_desc_file):
        print('Descriptor file ' + game_desc_file + ' does not exist.')
        sys.exit(1)

    if not game_desc_file.endswith('.game'):
        print('Wrong extension type')

    game_descriptor = configparser.ConfigParser()
    game_descriptor.read(game_desc_file)
    game_id = game_desc_file[game_desc_file.rfind('/') + 1: len(game_desc_file) - 5]
    game_descriptor.set('Game', 'ID', game_id)
    game = game_descriptor['Game']

    config = configparser.ConfigParser()
    config.read('/home/rebit/.config/game-launcher/game-launcher.cfg')

    verify_descriptor(game_descriptor, config)

    add_descriptor(game_desc_file)
    add_menu_entry(game, config)
    if icon_file is not None:
        add_icon(icon_file, config)


def get_game_dialog(game_data, config, message):
    game_dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, message)
    game_dialog.set_title(game_data.title)

    game_image = Gtk.Image()
    game_image.set_from_file(config['Icons']['Icons Location'] + "/64x64/apps/" + game_data.icon + ".png")
    game_dialog.set_image(game_image)

    return game_dialog


def update_game(game_desc_file, icon_file):
    pass


load_globals()

parser = argparse.ArgumentParser()
sub_parsers = parser.add_subparsers()

add_parser = sub_parsers.add_parser('add')
add_parser.set_defaults(action='add')
add_parser.add_argument('--descriptor', required=True)
add_parser.add_argument('--icon')

update_parser = sub_parsers.add_parser('update')
update_parser.set_defaults(action='update')
update_parser.add_argument('--descriptor', nargs='?')
update_parser.add_argument('--icon', nargs='?')

launch_parser = sub_parsers.add_parser('launch')
launch_parser.set_defaults(action='launch')
launch_parser.add_argument('id')

args = parser.parse_args()

if args.action == 'add':
    add_game(args.descriptor, args.icon)
elif args.action == 'update':
    update_game(args.descriptor, args.icon)
elif args.action == 'launch':
    try:
        launch_game(args.id)
    finally:
        subprocess.call(['xrandr', '-s', '1280x1024'])
