import configparser
import os


def find_config_file(name, skip_user_dirs=False, skip_inst_dir=False, must_exist=False):
    if not skip_user_dirs:
        if os.path.isfile(os.environ.get('HOME') + '/.config/application-launcher/' + name):
            return os.environ.get('HOME') + '/.config/application-launcher/' + name

    if not skip_inst_dir:
        if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + '/' + name):
            return os.path.dirname(os.path.realpath(__file__)) + '/' + name

    if must_exist:
        # TODO throw error
        pass

    return None


def load_config(name, extension='cfg', skip_user_dirs=False, skip_inst_dir=False, must_exist=False):
    config_file = find_config_file(name + '.' + extension, skip_user_dirs, skip_inst_dir, must_exist)

    if config_file is not None:
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    return None


def merge_config_files(new_config_file, config_files):
    merged_config = {}

    for config_file in config_files:
        if os.path.isfile(config_file):
            with open(config_file) as f:
                for line in f:
                    conf_entry = line.split('=')
                    if len(conf_entry) > 1:
                        merged_config[conf_entry[0].strip()] = conf_entry[1].strip()

    merged_config_file = open(new_config_file, 'w')
    for key in sorted(merged_config.keys()):
        merged_config_file.write(key + ' = ' + merged_config[key] + os.linesep)
    merged_config_file.close()
