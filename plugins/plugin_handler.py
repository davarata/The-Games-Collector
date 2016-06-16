import configparser
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
            plugin_config_file = utils.get_config_file(self.base_class.__name__ + '.cfg')
            if plugin_config_file is not None:
                plugin_config = configparser.ConfigParser()
                plugin_config.read(plugin_config_file)

                if plugin_config.has_section('Defaults') and plugin_config['Defaults'].get(feature) is not None:
                    name = plugin_config['Defaults'].get(feature)
                    for implementation in self.implementations:
                        if implementation.name == name:
                            return implementation

            for implementation in self.implementations:
                if feature in implementation.supported_implementations:
                    return implementation

        return self.implementations[0]

    install_dir = None
    name = None
    base_class = None
    implementations = None
    # TODO consider changing name
    supported_implementations = None
