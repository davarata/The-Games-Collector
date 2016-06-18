import importlib
import inspect
import os
from pathlib import Path

import utils


# TODO allow plugin parameters to be checked (add a list of expected parameters than can be checked)
class Plugin:

    def load_plugins(self, package_name, base_class):
        if not inspect.isclass(base_class):
            # TODO throw an error
            return

        if self.name is not None:
            # TODO throw an error
            return

        self.base_class = base_class
        self.implementations = []

        plugins_path = self.install_dir + '/' + package_name.replace('.', '/')
        if not os.path.isdir(plugins_path):
            # TODO throw an error
            return

        for entry in Path(plugins_path).iterdir():
            if not entry.is_file():
                continue
            if not entry.name.endswith('.py'):
                continue

            module = importlib.import_module(package_name + '.' + entry.name[:-3])
            for name, implementation in inspect.getmembers(module):
                if inspect.isclass(implementation) \
                        and issubclass(implementation, self.base_class) \
                        and name is not self.base_class.__name__:
                    instance = implementation()
                    if instance.supported_implementations is not None:
                        instance.supported_implementations = [s.lower() for s in instance.supported_implementations]
                    self.implementations.append(instance)

    def get_implementation(self, feature=None, name=None):
        if name is not None:
            for implementation in self.implementations:
                if implementation.name == name:
                    return implementation

        if feature is not None:
            feature = feature.lower()
            # TODO try to get this changed to:
            # TODO self.get_config_value(feature) or self.get_config_value('Defaults.' + feature)
            config = self.get_config()
            if config is not None:
                if config.has_section('Defaults') and config['Defaults'].get(feature) is not None:
                    name = config['Defaults'].get(feature)
                    for implementation in self.implementations:
                        if implementation.name == name:
                            return implementation

            for implementation in self.implementations:
                if feature in implementation.supported_implementations:
                    return implementation

        return self.implementations[0]

    def get_config_value(self, key, required=False):
        self.get_config()

        if self.config is not None:
            # TODO try getting rid of the General bit. Some config files should be treated as normal property files.
            # TODO an alternative is to try and iterate through each section and see if the key is found in it
            if self.config.has_section('General') and self.config['General'].get(key) is not None:
                return self.config['General'][key]
            else:
                if required:
                    print('The property ' + key + ' was not found in the ' + self.get_config_file_name() +
                          ' configuration file.')
        else:
            if required:
                print('The ' + self.get_config_file_name() + ' configuration file was not found.')

    def get_config(self):
        self.config = utils.load_config(self.get_config_file_name(), 'cfg')

        return self.config

    def get_config_file_name(self):
        if self.name is not None:
            return self.name
        else:
            return self.__class__.__name__

    install_dir = None
    name = None
    base_class = None
    implementations = None
    # TODO consider changing name
    supported_implementations = None
    config = None