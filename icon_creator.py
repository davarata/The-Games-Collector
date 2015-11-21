import configparser
import argparse
import os
import subprocess
import sys
from gi.repository import Gtk, Gdk


def add_icon(icon_file, config):
    icon_conf = config['Icons']
    create_icons(
        icon_file,
        icon_conf['Sizes'],
        icon_conf['Icon set root'],
        icon_conf['Icon path pattern'])


def create_icons(original_svg, sizes, icon_set_root, icon_path_pattern):
    if not os.path.isfile(original_svg):
        print('Icon file ' + original_svg + ' does not exist.')
        sys.exit(1)

    if not original_svg.endswith('.svg'):
        print('Wrong extension type.')

    if (sizes is None) or (len(sizes) == 0):
        print('Sizes not specified.')
        sys.exit(1)
    for size in sizes.split(','):
        try:
            int(size)
        except ValueError:
            print(size + ' is not an integer.')
            sys.exit(1)

    if (icon_set_root is None) or (len(icon_set_root) == 0):
        print('Icon set root not specified.')
        sys.exit(1)

    if (icon_path_pattern is None) or (len(icon_path_pattern) == 0):
        print('Icon path pattern not specified.')
        sys.exit(1)

    name = original_svg[original_svg.rfind('/') + 1: len(original_svg) - 4]
    for size in sizes.split(','):
        icon_location = icon_set_root + '/' + icon_path_pattern.replace('__size__', size)
        if os.path.isdir(icon_location):
            subprocess.call([
                'inkscape',
                '-w=' + size,
                '-h=' + size,
                original_svg,
                '-e',
                icon_location + '/' + name + '.png'])
        else:
            print('Directory \'' + icon_location + '\' not found - skipping.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--svg', required=True)
    parser.add_argument('--sizes', nargs='?')
    parser.add_argument('--icon-set-root', nargs='?')
    parser.add_argument('--icon-path-pattern', nargs='?')

    args = parser.parse_args()

    # TODO Change this:
    # Try and use the command-line parameters first. If a config file is found, the command-line
    # parameters will be ignored.
    config = configparser.ConfigParser()
    if os.path.isfile(os.environ.get('HOME') + '/.config/application-launcher/icon-creator.cfg'):
        config.read(os.environ.get('HOME') + '/.config/application-launcher/icon-creator.cfg')
        add_icon(args.svg, config)
    else:
        create_icons(args.svg, args.sizes, args.icon_set_root, args.icon_path_pattern)
