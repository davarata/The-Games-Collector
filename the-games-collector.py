import argparse
import configparser
import glob
import os
import shutil
import sys

from gi.repository import Gtk

import icon_creator
from plugins.display.display_handler import DisplayHandler
from plugins.launchers.game_launcher import GameLauncher

# TODO choose between game_data and game
# TODO remove launcher-specific configuration from the main launcher config
from plugins.mappers.input_mapper import InputMapper


# TODO Change: This needs to change to allow a custom icon (which might not be the same name as the
# ID) to be added to the file installed
from config_manager import ConfigManager


def add_descriptor(game_desc_file):
    shutil.copyfile(game_desc_file,
                    os.environ.get('HOME') + '/.config/the-games-collector/' + game_desc_file.rpartition('/')[2])


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
    config = ConfigManager.get_instance().load_config('game-launcher', skip_inst_dir=True)

    launcher = init_launcher(game_descriptor, config)

    if launcher.game_data.get('core') is not None and launcher.game_data['core'].endswith('scummvm_libretro.so'):
        add_scummvm_libretro_game(launcher, game_desc_file)
    else:
        add_descriptor(game_desc_file)
    add_menu_entry(launcher, game_descriptor['Game'])
    if icon_file is not None:
        icon_creator.add_icon(icon_file, config)


def ask_question(question):
    reply = input(question + ' [y/n]? ')
    while not reply.lower() in {'y', 'n'}:
        reply = input(question + ' [y/n]? ')
    return reply


def add_scummvm_libretro_game(launcher, game_desc_file):
    try:
        launcher.configure_env()

        use_exising_scummvm_ini = False
        game_scummvm_ini_path = launcher.game_data['game_root'] + '/scummvm.ini'
        if os.path.isfile(game_scummvm_ini_path):
            use_exising_scummvm_ini =\
                ask_question('Use exising ScummVM configuration file (' + game_scummvm_ini_path + ')') == 'y'

        if use_exising_scummvm_ini:
            game_scummvm_ini = read_scummvm_ini_file(game_scummvm_ini_path)
            if len(game_scummvm_ini.sections()) > 2:
                raise Exception('The ' + game_scummvm_ini_path +
                                ' ScummVM ini file contains more than one game section.')
            elif len(game_scummvm_ini.sections()) == 2:
                if 'scummvm' in game_scummvm_ini.sections():
                    write_scummvm_ini_file(game_scummvm_ini, game_scummvm_ini_path, write_game_ini=True)
                else:
                    raise Exception('The ' + game_scummvm_ini_path +
                                    ' ScummVM ini file contains more than one game section.')
            else:
                if 'scummvm' in game_scummvm_ini.sections():
                    raise Exception('The ' + game_scummvm_ini_path + ' ScummVM ini file contains no game sections.')
        else:
            scummvm_ini_path = launcher.get_config()['General'].get('Config location') + '/system/scummvm.ini'
            scummvm_ini =  read_scummvm_ini_file(scummvm_ini_path)

            scummvm_ini['scummvm']['browser_lastpath'] = launcher.launcher_config['General']['Games Location']
            write_scummvm_ini_file(scummvm_ini, scummvm_ini_path)

            launcher.game_data['target'] = None
            launcher.launch_game()

            scummvm_ini =  read_scummvm_ini_file(scummvm_ini_path)

            write_scummvm_ini_file(scummvm_ini, scummvm_ini_path)
            write_scummvm_ini_file(scummvm_ini, game_scummvm_ini_path, write_game_ini=True)

        game_scummvm_ini = read_scummvm_ini_file(game_scummvm_ini_path)
        game_id = game_scummvm_ini.sections()[0]
        scummvm_retroarch_file = open(launcher.game_data['game_root'] + '/' + game_id + '.scummvm', 'w')
        scummvm_retroarch_file.write(game_id + os.linesep)
        scummvm_retroarch_file.close()

        descriptor = []
        in_game_section = False
        insert_index = 0
        index = 0
        with open(game_desc_file) as f:
            for line in f:
                if line.strip().startswith('['):
                    in_game_section = line.strip() == '[Game]'
                if line.strip().lower().startswith('target'):
                    continue
                if in_game_section and line.strip() != '':
                    insert_index = index + 1
                    descriptor.append(line)
                    index = index + 1

        descriptor.insert(insert_index, 'Target=' + game_id + '.scummvm' + os.linesep)
        descriptor_file = open(
            os.environ.get('HOME') + '/.config/the-games-collector/' + game_desc_file.rpartition('/')[2], 'w')
        for entry in descriptor:
            descriptor_file.write(entry)
        descriptor_file.close()
    finally:
        revert_env(launcher)


def read_scummvm_ini_file(scummvm_ini_path):
    scummvm_ini = configparser.ConfigParser()
    scummvm_ini.read(scummvm_ini_path)
    return scummvm_ini


def write_scummvm_ini_file(scummvm_ini, scummvm_ini_path, write_game_ini = False):
    if write_game_ini:
        for section in scummvm_ini.sections():
            if section != 'scummvm':
                game_scummvm_ini_file = open(scummvm_ini_path, 'w')
                game_scummvm_ini_file.write('[' + section + ']' + os.linesep)
                for key in scummvm_ini[section].keys():
                    game_scummvm_ini_file.write(key + '=' + scummvm_ini[section][key] + os.linesep)
                game_scummvm_ini_file.close()
    else:
        if scummvm_ini.has_section('scummvm'):
            scummvm_ini_file = open(scummvm_ini_path, 'w')
            scummvm_ini_file.write('[scummvm]' + os.linesep)
            for key in scummvm_ini['scummvm'].keys():
                scummvm_ini_file.write(key + '=' + scummvm_ini['scummvm'][key] + os.linesep)
            scummvm_ini_file.close()


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
    comment += ' by ' + game_properties['Developer'] + ' for ' + launcher.get_platform_description()

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
    menu_entry.set('Desktop Entry', 'Exec', 'game-launcher play ' + game_properties['ID'])
    menu_entry.set('Desktop Entry', 'Terminal', 'false')
    menu_entry.set('Desktop Entry', 'Categories', 'Game;' + ';'.join(genres))

    menu_entry.write(
        open(launcher.launcher_config['General']['Menu Destination'] + '/' + game_properties['ID'] + '.desktop', 'w'),
        False)


def change_resolution(game_data):
    if game_data['resolution'] is not None:
        display_handler.get_implementation(ignore_versions=True).change_resolution(game_data['resolution'])


def is_adding_scummvm_game(launcher):
    return (launcher.name == 'RetroArch') and (launcher.get_core() == 'scummvm_libretro')


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
        for property in missing_properties:
            if property == 'target' and is_adding_scummvm_game(launcher):
                continue
            # TODO decide what to do about reusable strings
            print('The \'{}\' property is required by the {}'.format(property, launcher.name + ' launcher.'))
            sys.exit(1)

    unknown_properties = properties.difference(launcher.required_properties, launcher.optional_properties)
    if len(unknown_properties) > 0:
        for property in unknown_properties:
            print('The \'' + property + '\' property is not used by the ' + launcher.name + ' launcher.')
            sys.exit(1)

    for game_property in game_properties:
        if len(game_properties.get(game_property)) == 0:
            print('The property \'${}\' is empty.'.format(game_property))
            sys.exit(1)


# TODO rename to check_media. This might be moved to another script
# TODO also, stop using hard-coded values (specified in the descriptor)
def check_optical_disk(game_data, config, game):
    if game_data['optical_disk'] is not None:
        message = '\nPlease insert the optical disk with the label \'' + game['Optical Disk'].rpartition('/')[2] + '\''

        # temp hack. Add icon to game_data
        game_dialog = get_game_dialog(game_data, config, message)

        missing = not os.path.isdir(game_data['optical_disk'])
        while missing:
            game_dialog.show_all()
            response = game_dialog.run()

            if response == -4:
                game_dialog.destroy()
                sys.exit(1)

            missing = not os.path.isdir(game_data['optical_disk'])

        game_dialog.destroy()


# TODO Decide if I want to pass launcher or game_data
def configure_env(launcher):
    display_handler.get_implementation(ignore_versions=True).save_resolution()
    change_resolution(launcher.game_data)
    launcher.configure_env()


# TODO move this to another script and make the gui implementation use plugins?
def get_game_dialog(game_data, config, message):
    game_dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, message)
    game_dialog.set_title(game_data['title'])

    game_image = Gtk.Image()
    if game_data['icon'] is not None and os.path.isfile(config['Icons']['Icon set root'] + '/64x64/apps/' + game_data['icon'] + '.png'):
        game_image.set_from_file(config['Icons']['Icon set root'] + '/64x64/apps/' + game_data['icon'] + '.png')
    game_dialog.set_image(game_image)

    return game_dialog


def init_launcher(descriptor, config):
    game_properties = descriptor['Game']

    if game_properties.get('Platform') is None or len(game_properties['Platform']) == 0:
        print('The \'Platform\' property is required.')
        sys.exit(1)

    launcher_name = None
    launcher_params = {}
    if game_properties.get('Launcher') is not None and len(game_properties['Launcher']) > 0:
        launcher_name, *params = [p.strip() for p in game_properties['Launcher'].split(',')]
        for launcher_param in [p.lower() for p in params]:
            key, value = launcher_param.strip().split('=')
            launcher_params[key.strip()] = value.strip()

    version = None
    if launcher_params.get('version') is not None:
        version = launcher_params['version']

    launcher = game_launcher.get_implementation(game_properties['Platform'], launcher_name, version=version)

    launcher.game_data['platform'] = game_properties['Platform']
    launcher.launcher_params = launcher_params
    # TODO Decide what to call config: config / launcher_config / ?...
    launcher.launcher_config = config

    check_expected_properties(launcher, game_properties)

    launcher.set_game_root(game_properties)
    if game_properties.get('target') != None:
        launcher.set_target(game_properties)
        launcher.set_working_dir(game_properties)

    set_id(launcher.game_data, game_properties)
    set_optical_disk(launcher.game_data, game_properties)
    set_resolution(launcher.game_data, game_properties)

    launcher.set_launcher_data(descriptor)

    # TODO move set_game_menu_data(...)
    set_game_menu_data(launcher.game_data, game_properties)

    return launcher


def launch_game(id):
    if ConfigManager.get_instance().find_config_file(id, extension='game', skip_inst_dir=False) is None:
        raise Exception('Game ' + id + ' not found.')

    game_descriptor = ConfigManager.get_instance().load_config(id, extension='game', skip_inst_dir=True)
    # TODO Reconsider adding the ID here. Don't like it.
    game_descriptor.set('Game', 'ID', id)

    # TODO Consider moving this somewhere else so that it will only be done once
    # TODO this config file contains launcher specific config...
    # TODO the name game-launcher should be changed to the-games-collector.
    # Also, this is the file that should be replaced by another file (for testing). This config file should contain
    # the information that indicates where the user directories are (or you should be able to override them from here)
    # This should make it possible to remove the test-specific parameters.
    config = ConfigManager.get_instance().load_config('game-launcher', skip_inst_dir=True)

    launcher = init_launcher(game_descriptor, config)

    used_mappers = None
    if game_descriptor.has_section('Controls'):
        used_mappers = get_used_mappers(game_descriptor['Controls'])

    check_optical_disk(launcher.game_data, config, game_descriptor['Game'])

    activate_input_mappers(used_mappers)
    try:
        configure_env(launcher)

    # # TODO: Figure out what to do with the line below
    # launcher.game_data['platform_config'] = config['General']['Platform Config']

        launcher.launch_game()
    finally:
        revert_env(launcher)
        deactivate_input_mappers(used_mappers)


def revert_env(launcher):
    launcher.revert_env()
    # TODO sort out the problem with the non game-launcher plugins and versioning
    display_handler.get_implementation(ignore_versions=True).restore_resolution()


def set_game_menu_data(game_data, game_properties):
    game_data['title'] = game_properties['Title']

    # TODO add check for genres
    game_data['genre'] = game_properties['Genre']

    game_data['developer'] = game_properties['Developer']

    if game_properties.get('Specialization') is None:
        game_data['specialization'] = None
    else:
        game_data['specialization'] = game_properties['Specialization']

    if game_properties.get('Included') is None:
        game_data['included'] = None
    else:
        game_properties.included = game_properties['Included']

    if game_properties.get('Icon') is None:
        if game_data['id'] is not None:
            game_data['icon'] = game_data['id']
        else:
            game_data['icon'] = None
    else:
        game_data['icon'] = game_properties['Icon']


def set_id(game_data, game_properties):
    if game_properties.get('ID') is None:
        game_data['id'] = None
    else:
        game_data['id'] = game_properties['ID']


def set_optical_disk(game_data, game_properties):
    if game_properties.get('Optical Disk') is None:
        game_data['optical_disk'] = None
    else:
        game_data['optical_disk'] = game_properties['Optical Disk']


def set_resolution(game_data, game_properties):
    if game_properties.get('Resolution') is None:
        game_data['resolution'] = None
    else:
        game_data['resolution'] = game_properties['Resolution']


def get_used_mappers(control_properties):
    input_mapping_groups = group_input_mappings(control_properties)
    used_mappers = []

    for mapping_type in input_mapping_groups.keys():
        input_mappings = input_mapping_groups[mapping_type]
        implementation = None
        if mapping_type.find('=') > 0:
            mapping_type, implementation = mapping_type.split('=')
        input_mapper_impl = input_mapper.get_implementation(mapping_type, implementation, ignore_versions=True)
        input_mapper_impl.set_mappings(input_mappings)
        used_mappers.append(input_mapper_impl)

    return used_mappers


# Why not move this to input_mapper?
def group_input_mappings(control_properties):
    input_mapping_groups = {}

    for virtual_trigger in control_properties:
        if virtual_trigger.strip().startswith('mappers'):
            continue

        virtual_device = virtual_trigger.split('.')[0].strip()

        virtual_trigger_mapping = control_properties[virtual_trigger]

        if virtual_trigger_mapping.startswith('['):
            # TODO figure out what to do with this
            description = virtual_trigger_mapping[1:-1].strip()
        else:
            remaining_string = virtual_trigger_mapping
            while remaining_string != '':
                description = None

                physical_trigger, remaining_string = get_mapping_token(remaining_string, [' ', '/', '['])
                physical_trigger = physical_trigger.strip()

                remaining_string = remaining_string.strip()
                if remaining_string.startswith('/'):
                    remaining_string = remaining_string[1:].strip()

                if remaining_string.startswith('['):
                    description, remaining_string = get_mapping_token(remaining_string, [']'])
                    description = description.strip()

                    if remaining_string.startswith(']'):
                        remaining_string = remaining_string[1:].strip()

                if remaining_string.startswith('/'):
                    remaining_string = remaining_string[1:].strip()

                physical_device = physical_trigger.split('.')[0]
                mapping_type = virtual_device.lower() + ':' + physical_device.lower()
                if input_mapping_groups.get(mapping_type) is None:
                    input_mapping_groups[mapping_type] = []

                mapping = {
                    'virtual': virtual_trigger,
                    'physical': physical_trigger,
                    'description': description
                }

                input_mapping_groups[mapping_type].append(mapping)

    if control_properties.get('mappers') is not None:
        mappers = {}
        # not too happy with the name mapping
        for mapping in control_properties['mappers'].split(','):
            mapping_type, mapper = mapping.split('=')
            mappers[mapping_type.strip().lower()] = mapper.strip()

        tmp_input_mapping_groups = input_mapping_groups
        input_mapping_groups = {}
        for plain_mapping_type in tmp_input_mapping_groups.keys():
            enhanced_mapping_type = plain_mapping_type
            if mappers.get(plain_mapping_type) is not None:
                enhanced_mapping_type += '=' + mappers[plain_mapping_type]
            input_mapping_groups[enhanced_mapping_type] = tmp_input_mapping_groups[plain_mapping_type]

    return input_mapping_groups


def activate_input_mappers(input_mappers):
    if input_mappers is not None:
        for mapper in input_mappers:
            mapper.activate()


def deactivate_input_mappers(input_mappers):
    if input_mappers is not None:
        for mapper in input_mappers:
            mapper.deactivate()


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


def configure(id):
    launcher = game_launcher.get_implementation(name='RetroArch')
    launcher.game_data['platform'] = id

    try:
        launcher.set_launcher_data(None)
        launcher.configure_env()
        launcher.launch_game()
    finally:
        launcher.revert_env()


def validate_all():
    config = ConfigManager.get_instance().load_config('game-launcher', skip_inst_dir=True)
    # TODO remove hard-coded config locations
    files = glob.glob(os.environ.get('HOME') + '/.config/the-games-collector/*.game')
    for file in files:
        game_descriptor = configparser.ConfigParser(strict=False)
        game_descriptor.read(file)

        try:
            init_launcher(game_descriptor, config)
        except:
            print(file)
            raise

parser = argparse.ArgumentParser()
sub_parsers = parser.add_subparsers()

add_parser = sub_parsers.add_parser('add')
add_parser.set_defaults(action='add')
add_parser.add_argument('--descriptor', required=True)
add_parser.add_argument('--icon')
add_parser.add_argument('-c', '--config-location')
add_parser.add_argument('-i', '--installation-location')

launch_parser = sub_parsers.add_parser('play')
launch_parser.set_defaults(action='play')
launch_parser.add_argument('id')
launch_parser.add_argument('-c', '--config-location')
launch_parser.add_argument('-i', '--installation-location')

launch_parser = sub_parsers.add_parser('configure')
launch_parser.set_defaults(action='configure')
launch_parser.add_argument('id')

launch_parser = sub_parsers.add_parser('validate-all')
launch_parser.set_defaults(action='validate-all')
launch_parser.add_argument('-c', '--config-location')
launch_parser.add_argument('-i', '--installation-location')

args = parser.parse_args()

if args.action == 'play':
    if args.config_location is not None:
        ConfigManager.get_instance().set_user_dir(args.config_location)
    if args.installation_location is not None:
        ConfigManager.get_instance().set_inst_dir(args.installation_location)

install_dir = os.path.dirname(os.path.realpath(__file__))
game_launcher = GameLauncher()
game_launcher.init(install_dir)

input_mapper = InputMapper()
input_mapper.init(install_dir)

display_handler = DisplayHandler()
display_handler.init(install_dir)

if args.action == 'add':
    add_game(args.descriptor, args.icon)
elif args.action == 'play':
    try:
        launch_game(args.id)
    finally:
        display_handler.restore_resolution()
elif args.action == 'configure':
    configure(args.id)
elif args.action == 'validate-all':
    validate_all()
