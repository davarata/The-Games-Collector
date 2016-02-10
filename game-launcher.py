import argparse
import configparser
from dosbox_launcher import DOSBoxLauncher
import glob
import icon_creator
import os
import shutil
import subprocess
import sys
from gi.repository import Gtk, Gdk
from retroarch_launcher import RetroArchLauncher
from scummvm_launcher import ScummVMLauncher
from wine_launcher import WINELauncher

# TODO choose between game_data and game

class Struct():
    pass


# TODO Change: This needs to change to allow a custom icon (which might not be the same name as the
# ID) to be added to the file installed
def add_descriptor(game_desc_file):
    shutil.copyfile(game_desc_file,
                    os.environ.get('HOME') + '/.config/application-launcher/' + game_desc_file.rpartition('/')[2])


def add_game(game_desc_file, icon_file):
    if not os.path.isfile(game_desc_file):
        print('Descriptor file ' + game_desc_file + ' does not exist.')
        sys.exit(1)

    if not game_desc_file.endswith('.game'):
        print('Wrong extension type')

    game_descriptor = configparser.ConfigParser(strict=False)
    game_descriptor.read(game_desc_file)
    # TODO Reconsider adding the ID here. Don't like it.
    game_descriptor.set('Game', 'ID', game_desc_file[game_desc_file.rfind('/') + 1: len(game_desc_file) - 5])

    # TODO Consider moving this somewhere else so that it will only be done once
    config = configparser.ConfigParser()
    config.read(os.environ.get('HOME') + '/.config/application-launcher/game-launcher.cfg')

    launcher = init_launcher(game_descriptor, config)

    add_descriptor(game_desc_file)
    add_menu_entry(launcher, game_descriptor['Game'])
    if icon_file is not None:
        icon_creator.add_icon(icon_file, config)


# affected by launcher-specific details, such as platform names
# change the game['Platform'] + ' console' into launcher.get_type...
def add_menu_entry(launcher, game_properties):
    genre = game_properties['Genre'].replace('[', '').replace(']', '').replace(',', ' ').capitalize()
    if game_properties.get('Specialization') is not None and len(game_properties['Specialization']) > 0:
        if game_properties['Specialization'] == 'Collection':
            comment = 'Collection of ' + genre.lower() + ' games'
        if game_properties['Specialization'] == 'Expansion':
            comment = 'Expansion for the ' + genre.lower() + ' game'
    else:
        comment = genre + ' game'
    comment += ' by ' + game_properties['Developer'] + ' for ' + launcher.get_platform_description

    if game_properties.get('Included') is not None and len(game_properties['Included']) > 0:
        comment += '. '
        *included_games, last_included_game = [i.strip() for i in game_properties['Included'].split(',')]
        if len(included_games) == 0:
            comment += last_included_game + ' included'
        else:
            comment += ', '.join(included_games) + ' and ' + last_included_game + ' included'

    reordered_genres = []
    for genre in game_properties['Genre'].split(','):
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
    menu_entry.set('Desktop Entry', 'Name', game_properties['Title'])
    menu_entry.set('Desktop Entry', 'Comment', comment)
    if game_properties.get('Icon') is not None and len(game_properties['Icon']) > 0:
        menu_entry.set('Desktop Entry', 'Icon', game_properties['Icon'])
    else:
        menu_entry.set('Desktop Entry', 'Icon', game_properties['ID'])
    menu_entry.set('Desktop Entry', 'Exec', 'game-launcher launch ' + game_properties['ID'])
    menu_entry.set('Desktop Entry', 'Terminal', 'false')
    menu_entry.set('Desktop Entry', 'Categories', 'Game;' + ';'.join(genres))

    menu_entry.write(
        open(launcher.launcher_config['General']['Menu Destination'] + '/' + game_properties['ID'] + '.desktop', 'w'),
        False)


def change_resolution(game_data):
    if game_data.resolution is not None:
        subprocess.call(['/usr/bin/xrandr', '-s', game_data.resolution])


def check_expected_properties(launcher, game_properties):
    # TODO
    # Each component should specify which properties they require, instead of all the properties
    # being specified in the launcher. When this script starts, the required and optional lists are created
    # from the individual scripts.
    # Avoid duplicate required entries:
    # list_of_required = list_of_required + list_of_required.difference(component.required)
    # Remove any required entries from the optional list:
    # list_of_optional = list_of_required.difference(list_of_optional)
    properties = set(game_properties)

    missing_properties = launcher.required_properties.difference(properties)
    if len(missing_properties) > 0:
        for property in unknown_properties:
            # TODO decide what to do about reusable strings
            print('The \'{}\' property is required by the {}'.format(property, launcher.get_name() + ' launcher.'))
            sys.exit(1)

    unknown_properties = properties.difference(launcher.required_properties, launcher.optional_properties)
    if len(unknown_properties) > 0:
        for property in unknown_properties:
            print('The \'' + property + '\' property is not used by the ' + launcher.get_name() + ' launcher.')
            sys.exit(1)

    for game_property in game_properties:
        if len(game_properties.get(game_property)) == 0:
            print('The property \'${}\' is empty.'.format(game_property))
            sys.exit(1)


def check_optical_disk(game_data, config, game):
    if game_data.optical_disk is not None:
        message = '\nPlease insert the optical disk with the label \'' + game['Optical Disk'].rpartition('/')[2] + '\''

        # temp hack. Add icon to game_data
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


# TODO Decide if I want to pass launcher or game_data
def configure_env(game_data):
    map_input(game_data)
    change_resolution(game_data)


def get_game_dialog(game_data, config, message):
    game_dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, message)
    game_dialog.set_title(game_data.title)

    game_image = Gtk.Image()
    if game_data.icon is not None and os.path.isfile(config['Icons']['Icon set root'] + '/64x64/apps/' + game_data.icon + '.png'):
        game_image.set_from_file(config['Icons']['Icon set root'] + '/64x64/apps/' + game_data.icon + '.png')
    game_dialog.set_image(game_image)

    return game_dialog


def get_launcher(platform, launcher_name):
    if launcher_name is None:
        if platform == 'DOS':
            launcher_name = 'DOSBox'
        elif platform == 'Windows':
            launcher_name = 'Wine'
        else:
            launcher_name = 'RetroArch'

    if launcher_name == 'DOSBox':
        return DOSBoxLauncher()
    elif launcher_name == 'ScummVM':
        return ScummVMLauncher()
    elif launcher_name == 'Wine':
        return WINELauncher()
    else:
        return RetroArchLauncher()


def get_mapping_token(string, separators):
    working_string = string
    remaining_string = ''

    index = 0
    while index != -1:
        for token in separators:
            index = working_string.find(token)
            if index >= 0:
                break

        if index == 0:
            remaining_string = working_string + remaining_string
            working_string = ''
        elif index > 0:
            remaining_string = working_string[index:] + remaining_string
            working_string = working_string[:index]

    return working_string, remaining_string


def init_launcher(descriptor, config):
    game_properties = descriptor['Game']

    game_data = Struct()

    if game_properties.get('Platform') is None or len(game_properties['Platform']) == 0:
        print('The \'Platform\' property is required.')
        sys.exit(1)
    game_data.platform = game_properties['Platform']
    # if platform not in platforms.keys():
    #     print('Unknown platform: ' + game_data.platform)
    #     sys.exit(1)

    launcher_name = None
    launcher_params = None
    if game_properties.get('Launcher') is not None and len(game_properties['Launcher']) > 0:
        launcher_name, *launcher_params = [p.strip() for p in game_properties['Launcher'].split(',')]
    launcher = get_launcher(game_data.platform, launcher_name)

    launcher.game_data = game_data
    launcher.launcher_params = launcher_params
    # TODO Decide what to call config: config / launcher_config / ?...
    launcher.launcher_config = config

    check_expected_properties(launcher, game_properties)

    launcher.set_game_root(game_properties)
    launcher.set_target(game_properties)
    launcher.set_working_dir(game_properties)

    set_id(game_data, game_properties)
    set_optical_disk(game_data, game_properties)
    set_resolution(game_data, game_properties)

    set_mappings(launcher, descriptor)

    launcher.set_launcher_data(descriptor)

    # TODO move set_game_menu_data(...)
    set_game_menu_data(game_data, game_properties)

    return launcher


def launch_game(id):
    game_descriptor = configparser.ConfigParser(strict=False)
    game_descriptor.read(os.environ.get('HOME') + '/.config/application-launcher/' + id + '.game')
    # TODO Reconsider adding the ID here. Don't like it.
    game_descriptor.set('Game', 'ID', id)

    # TODO Consider moving this somewhere else so that it will only be done once
    config = configparser.ConfigParser()
    config.read(os.environ.get('HOME') + '/.config/application-launcher/game-launcher.cfg')

    launcher = init_launcher(game_descriptor, config)

    check_optical_disk(launcher.game_data, config, game_descriptor['Game'])

    configure_env(launcher.game_data)
    launcher.configure_env()

    # TODO: Figure out what to do with the line below
    launcher.game_data.platform_config = config['General']['Platform Config']

    launcher.launch_game()

    launcher.revert_env()
    revert_env(launcher.game_data)


def map_input(game_data):
    if (game_data.mappings is not None) and (game_data.mappings.get('Xmodmap') is not None):
        write_xmodmap_mappings(game_data.mappings['Xmodmap'])
        subprocess.Popen(['xmodmap', '/tmp/xmodmap_new'])

    if (game_data.mappings is not None) and (game_data.mappings.get('Antimicro') is not None):
        write_antimicro_mappings(game_data.mappings['Antimicro'])
        # festive season hack! :-)
        # No more changes to the script for now. Fix next year!
        global antimicro
        antimicro = subprocess.Popen(['antimicro', '--hidden', '--profile', '/tmp/antimicro.gamecontroller.amgp'])


# TODO
# antimicro should be added to a stack containing commands to run and processes to kill
# (in reverse order). When setting up the environment, entries should be added to this
# stack, including the processes that should be killed. In the revert_env method, these
# commands will then be run and processes killed in the reverse order to which they were
# added
def revert_env(game_data):
    if (game_data.mappings is not None) and (game_data.mappings.get('Xmodmap') is not None):
        subprocess.Popen(['xmodmap', '/tmp/xmodmap_revert'])

    if (game_data.mappings is not None) and (game_data.mappings.get('Antimicro') is not None):
        # festive season hack! :-)
        # No more changes to the script for now. Fix next year!
        antimicro.kill()


# TODO Add a dry run of the actual mapping process for validation, since errors can only be
# detected when the actual mapping is done.
def set_mappings(launcher, game_descriptor):
    launcher.game_data.mappings = None

    if game_descriptor.has_section('Controls'):
        launcher.game_data.mappings = {}
    else:
        launcher.game_data.mappings = None
        return

    control_properties = game_descriptor['Controls']
    controllers = ['nes', 'snes', 'gameboyadvance', 'megadrive', 'arcade', 'xbox360']

    mappers = {}
    mapper = configparser.ConfigParser()
    mapper.read(os.environ.get('HOME') + '/.config/application-launcher/RetroArch.mapper')
    mappers['RetroArch'] = mapper

    mapper = configparser.ConfigParser()
    mapper.read(os.environ.get('HOME') + '/.config/application-launcher/Xmodmap.mapper')
    mappers['Xmodmap'] = mapper

    mapper = configparser.ConfigParser()
    mapper.read(os.environ.get('HOME') + '/.config/application-launcher/Antimicro.mapper')
    mappers['Antimicro'] = mapper

    known_physical_triggers = []
    for key in mappers.keys():
        mapper = mappers[key]
        for physical_trigger in mapper['Physical Devices']:
            if physical_trigger not in known_physical_triggers:
                known_physical_triggers.append(physical_trigger.lower())

    for virtual_trigger in control_properties:
        physical_triggers = []
        descriptions = []

        virtual_trigger_mapping = control_properties[virtual_trigger]

        if virtual_trigger_mapping.startswith('['):
            description = virtual_trigger_mapping[1:-1].strip()
        else:
            remaining_string = virtual_trigger_mapping
            while remaining_string != '':
                physical_trigger, remaining_string = get_mapping_token(remaining_string, [' ', '/', '['])

                physical_trigger = physical_trigger.strip().lower()
                remaining_string = remaining_string.strip()
                if remaining_string.startswith('/'):
                    remaining_string = remaining_string[1:].strip()

                if physical_trigger not in known_physical_triggers:
                    print('Physical trigger not found: \'' + physical_trigger + '\'')
                    exit()
                physical_triggers.append(physical_trigger)

                if remaining_string.startswith('['):
                    description, remaining_string = get_mapping_token(remaining_string, [']'])
                    descriptions.append(description[1:])

                    if remaining_string.startswith(']'):
                        remaining_string = remaining_string[1:].strip()

                if remaining_string.startswith('/'):
                    remaining_string = remaining_string[1:].strip()

        # for physical_trigger in physical_triggers:
        for index in range(len(physical_triggers)):
            physical_trigger = physical_triggers[index]
            virtual_device = virtual_trigger.split('.')[0]
            physical_device = physical_trigger.split('.')[0]

            mapping_type = None
            if virtual_device in controllers:
                mapping_type = launcher.get_name()
            else:
                if virtual_device == 'keyboard':
                    if physical_device in controllers:
                        mapping_type = 'Antimicro'
                    elif physical_device == 'keyboard':
                        mapping_type = 'Xmodmap'

            if launcher.game_data.mappings.get(mapping_type) is None:
                launcher.game_data.mappings[mapping_type] = []

            mapping = Struct()
            mapping.player = '1'
            mapping.virtual = mappers[mapping_type]['Virtual Devices'][virtual_trigger]
            mapping.physical = mappers[mapping_type]['Physical Devices'][physical_trigger]
            if len(descriptions) == 0:
                mapping.description = ''
            elif len(descriptions) == 1:
                mapping.description = descriptions[0]
            else:
                mapping.description = descriptions[index]

            launcher.game_data.mappings[mapping_type].append(mapping)


def set_game_menu_data(game_data, game_properties):
    game_data.title = game_properties['Title']

    # TODO add check for genres
    game_data.genre = game_properties['Genre']

    game_data.developer = game_properties['Developer']

    if game_properties.get('Specialization') is None:
        game_data.specialization = None
    else:
        game_data.specialization = game_properties['Specialization']

    if game_properties.get('Included') is None:
        game_data.included = None
    else:
        game_properties.included = game_properties['Included']

    if game_properties.get('Icon') is None:
        if game_data.id is not None:
            game_data.icon = game_data.id
        else:
            game_data.icon = None
    else:
        game_data.icon = game_properties['Icon']


def set_id(game_data, game_properties):
    if game_properties.get('ID') is None:
        game_data.id = None
    else:
        game_data.id = game_properties['ID']


def set_optical_disk(game_data, game_properties):
    if game_properties.get('Optical Disk') is None:
        game_data.optical_disk = None
    else:
        game_data.optical_disk = game_properties['Optical Disk']


def set_resolution(game_data, game_properties):
    if game_properties.get('Resolution') is None:
        game_data.resolution = None
    else:
        # TODO remove hard-coded resolutions
        game_data.resolution = game_properties['Resolution']
        if game_data.resolution not in {'640x480', '800x600', '1024x768', '1152x864', '1280x1024'}:
            print('Unknown resolution: \'{}\'.'.format(game_data.resolution))
            sys.exit(1)


def update_game(game_desc_file, icon_file):
    pass


def validate_all():
    config = configparser.ConfigParser()
    config.read(os.environ.get('HOME') + '/.config/application-launcher/game-launcher.cfg')

    files = glob.glob(os.environ.get('HOME') + '/.config/application-launcher/*.game')
    for file in files:
        game_descriptor = configparser.ConfigParser(strict=False)
        game_descriptor.read(file)

        try:
            init_launcher(game_descriptor, config)
        except:
            print(file)
            raise


def write_antimicro_mappings(mappings):
    # button, trigger, stickbutton, dpadbutton
    entry_xml = \
        '<{0} index="{1}">' + os.linesep + \
        ' <slots>' + os.linesep + \
        '  <slot>' + os.linesep + \
        '   <code>{2}</code>' + os.linesep + \
        '   <mode>keyboard</mode>' + os.linesep + \
        '  </slot>' + os.linesep + \
        ' </slots>' + os.linesep + \
        '</{0}>'

    sets = {}
    for mapping in mappings:
        parameters = mapping.physical.split(',')
        trigger_value = parameters[0]
        trigger_type = parameters[1]
        if len(parameters) == 3:
            index = parameters[2]
        else:
            index = '1'

        if trigger_type == 'button':
            set_id = 'button'
        else:
            set_id = trigger_type + ' ' + index
            trigger_type += 'button'

        if sets.get(set_id) is None:
            sets[set_id] = []

        sets[set_id].append('<!-- ' + mapping.description + ' -->' + os.linesep +
            entry_xml.format(trigger_type, trigger_value, mapping.virtual))

    mappings_file = open('/tmp/antimicro.gamecontroller.amgp', 'w')
    mappings_file.write('<?xml version="1.0" encoding="UTF-8"?>' + os.linesep)
    mappings_file.write('<gamecontroller configversion="16" appversion="2.12">' + os.linesep)
    mappings_file.write('  <sets>' + os.linesep)
    mappings_file.write('    <set index="1">' + os.linesep)
    indentation = '      '
    for set_id in sets.keys():
        if set_id is not 'button':
            name, index = set_id.split(' ')
            mappings_file.write(indentation + '<' + name + ' index="' + index + '">' + os.linesep)
            indentation += '  '
            for set_entry in sets[set_id]:
                set_entry = set_entry.replace(os.linesep, os.linesep + indentation)
                mappings_file.write(indentation + set_entry + os.linesep)
            indentation = indentation[:-2]
            mappings_file.write(indentation + '</' + name + '>' + os.linesep)
        else:
            for set_entry in sets[set_id]:
                set_entry = set_entry.replace(os.linesep, os.linesep + indentation)
                mappings_file.write(indentation + set_entry + os.linesep)

    mappings_file.write('    </set>' + os.linesep)
    mappings_file.write('  </sets>' + os.linesep)
    mappings_file.write('</gamecontroller>' + os.linesep)

    mappings_file.close()


def write_xmodmap_mappings(mappings):
    output = subprocess.check_output(['xmodmap', '-pke'], universal_newlines=True)

    mappings_file = open('/tmp/xmodmap_revert', 'w')
    for line in output.split(os.linesep):
        config_line = [column for column in line.split(' ') if column.strip() != '']
        for mapping in mappings:
            if (len(config_line) > 3) and (config_line[3].lower() == mapping.physical.lower()):
                mappings_file.write(line + os.linesep)
    mappings_file.close()

    mappings_file = open('/tmp/xmodmap_new', 'w')
    for mapping in mappings:
        mappings_file.write('! ' + mapping.description + os.linesep)
        mappings_file.write('keysym ' + mapping.physical + ' = ' + mapping.virtual + os.linesep)
        mappings_file.write(os.linesep)
    mappings_file.close()


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

launch_parser = sub_parsers.add_parser('validate-all')
launch_parser.set_defaults(action='validate-all')


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
elif args.action == 'validate-all':
    validate_all()
