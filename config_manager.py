import configparser
import os


class ConfigManager:

    @staticmethod
    def get_instance():
        if ConfigManager.instance is None:
            ConfigManager.instance = ConfigManager()

        return ConfigManager.instance

    def find_config_file(self, name, skip_user_dirs=False, skip_inst_dir=False, must_exist=False):
        if not skip_user_dirs:
            for user_dir in self.user_dirs:
                if os.path.isfile(user_dir + '/' + name):
                    return user_dir + '/' + name

        if not skip_inst_dir:
            if os.path.isfile(self.inst_dir + '/' + name):
                return self.inst_dir + '/' + name

        if must_exist:
            # TODO throw error
            pass

        return None

    def load_config(self, name, extension='cfg', skip_user_dirs=False, skip_inst_dir=False, must_exist=False):
        config_file = self.find_config_file(name + '.' + extension, skip_user_dirs, skip_inst_dir, must_exist)

        if config_file is not None:
            config = configparser.ConfigParser()
            config.read(config_file)
            return config

        return None

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

    def set_config(self, name, value):
        self.configurations[name] = value

    def get_config(self, name):
        return self.configurations[name]

    def set_user_dir(self, user_dir, replace_existing=True):
        if replace_existing:
            self.user_dirs = [user_dir]
        else:
            self.user_dirs = [user_dir] + self.user_dirs

    def set_inst_dir(self, inst_dir):
        self.inst_dir = inst_dir

    instance = None
    configurations = {}
    user_dirs = [os.environ.get('HOME') + '/.config/application-launcher/']
    inst_dir = os.path.dirname(os.path.realpath(__file__))
