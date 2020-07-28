import configparser
import os

from pathlib import Path


class ConfigManager:

    @staticmethod
    def get_instance():
        if ConfigManager.instance is None:
            ConfigManager.instance = ConfigManager()

        return ConfigManager.instance

    @staticmethod
    def merge(config, other, override=False):
        for section_name in other.keys():
            if section_name == 'DEFAULT':
                continue
            if not config.has_section(section_name):
                config.add_section(section_name)

            section = config[section_name]
            other_section = other[section_name]
            for property in other_section.keys():
                if section.get(property) is None or override:
                    section[property] = other_section[property]

    # TODO rename to locate_config(...)
    def find_config_file(self, name, extension='cfg', skip_user_dirs=False, skip_inst_dir=False, must_exist=False):
        if not skip_user_dirs:
            for user_dir in self.user_dirs:
                if os.path.isfile(user_dir + '/' + name + '.' + extension):
                    return user_dir + '/' + name + '.' + extension

        if not skip_inst_dir:
            if os.path.isfile(self.inst_dir + '/' + name + '.' + extension):
                return self.inst_dir + '/' + name + '.' + extension

        if must_exist:
            raise Exception('Could not find configuration file named \'' + name + '.' + extension + '\'.')

        return None

    # TODO rename to locate_configs(...)
    def find_config_files(self, partial_name, extension='cfg', skip_inst_dir=False, skip_user_dirs=False,
                          starts_with=False):
        config_files = []

        if not skip_user_dirs:
            for user_dir in self.user_dirs:
                for entry in Path(user_dir).iterdir():
                    if entry.is_file() and entry.name.endswith(extension):
                        if (starts_with and entry.name.startswith(partial_name))\
                                or (not starts_with and entry.name.find(partial_name) >= 0):
                            config_files.append(entry.name)

        if not skip_inst_dir:
            for entry in Path(self.inst_dir).iterdir():
                if entry.is_file() and entry.name.endswith(extension):
                    if (starts_with and entry.name.startswith(partial_name))\
                            or (not starts_with and entry.name.find(partial_name) >= 0):
                        config_files.append(entry.name)

        return config_files

    # TODO rename to load(...)
    def load_config(self, name, extension='cfg', skip_user_dirs=False, skip_inst_dir=False, must_exist=False,
                    save_config=True):
        if os.path.isfile(name):
            *_ignore, filename = name.rpartition('/')
            if self.get_config(filename) is not None:
                return self.get_config(filename)

            config_file = name
        else:
            filename = name
            if extension is not None:
                filename += '.' + extension
            if self.get_config(filename) is not None:
                return self.get_config(filename)

            config_file = self.find_config_file(name, extension, skip_user_dirs, skip_inst_dir, must_exist)

        if config_file is not None:
            config = configparser.ConfigParser()
            config.read(config_file)
        else:
            return None

        if save_config:
            self.set_config(filename, config)

        return config

    # TODO rename to merge_files(...)
    def merge_config_files(self, new_config_file, config_files):
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

    # TODO rename to set(...)
    def set_config(self, name, value):
        self.configurations[name] = value

    # TODO rename to get(...)
    def get_config(self, name):
        return self.configurations.get(name)

    def set_user_dir(self, user_dir, replace_existing=True):
        if replace_existing:
            self.user_dirs = [user_dir]
        else:
            self.user_dirs = [user_dir] + self.user_dirs

    def set_inst_dir(self, inst_dir):
        self.inst_dir = inst_dir

    instance = None
    configurations = {}
    user_dirs = [os.environ.get('HOME') + '/.config/the-games-collector/']
    inst_dir = os.path.dirname(os.path.realpath(__file__))
