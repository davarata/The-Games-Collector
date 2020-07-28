import importlib
import inspect
import os
from pathlib import Path
# TODO allow plugin parameters to be checked (add a list of expected parameters than can be checked)
# ?? above comment still valid?
from config_manager import ConfigManager


# TODO consider changing the name of the file to plugin.py
class Plugin:

    def load_plugins(self, package_name, base_class, ignore_versions=False):
        if not inspect.isclass(base_class):
            raise Exception('The base_class parameter is not a class type.')

        if self.name is not None:
            raise Exception('The load_plugins(...) method cannot be called from an initialized plugin.')

        self.base_class = base_class
        self.implementations = []

        plugins_path = self.install_dir + '/' + package_name.replace('.', '/')
        if not os.path.isdir(plugins_path):
            raise Exception('The plugins path \'' + plugins_path + '\' does not exist.')

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
                    instance.install_dir = self.install_dir
#                    if instance.supported_implementations is not None:
#                        instance.supported_implementations = [s.lower() for s in instance.supported_implementations]

                    if not ignore_versions:
                        instance.verify_versions()

                    self.implementations.append(instance)

    def get_implementation(self, feature=None, name=None, ignore_versions=False, version=None):
        the_implementation = None
        if name is not None:
            for implementation in self.implementations:
                if implementation.name == name:
                    the_implementation = implementation
                    break

        if the_implementation is None and feature is not None:
#            feature = feature.lower()

            # TODO try to get this changed to:
            # TODO self.get_config_value(feature) or self.get_config_value('Defaults.' + feature)
            # The classes inheriting from Plugin should not have different versions
            config = self.get_config(ignore_versions=True)
            if config is not None:
                if config.has_section('Defaults') and config['Defaults'].get(feature) is not None:
                    name = config['Defaults'].get(feature)
                    for implementation in self.implementations:
                        if implementation.name == name:
                            the_implementation = implementation
                            break

            if the_implementation is None:
                for implementation in self.implementations:
                    # A hack until I rewrite the config stuff. Very annoying having mismatches simply due to case.
                    for a_feature in implementation.supported_implementations:
                        if feature.lower() == a_feature.lower():
                            the_implementation = implementation
                            break
                    # if feature in implementation.supported_implementations:
                    #     the_implementation = implementation
                    #     break

        if the_implementation is None:
            the_implementation = self.implementations[0]

        if not ignore_versions:
            if version is None:
                version = the_implementation.get_default_version()

            if version is not None:
                ConfigManager.get_instance().find_config_file(the_implementation.get_plugin_name() + '_' + version,
                                                              skip_inst_dir=True, must_exist=True)
            the_implementation.version = version
        return the_implementation

    def verify(self):
        pass

    def verify_version(self, config_file):
        pass

    # TODO fix bug. aLinux.cfg and _Linux.cfg are picked up as valid configuration files for the Linux launcher
    def verify_versions(self):
        config_files = ConfigManager.get_instance().find_config_files(self.name, skip_inst_dir=True)

        if len(config_files) == 0:
            return

        for config_file in config_files:
            *_ignore, config_file_name = config_file.rpartition('/')
            if self.name + '.cfg' == config_file_name:
                self.verify()
            else:
                self.verify_version(config_file[:-4])

    def get_default_version(self):
        config = ConfigManager.get_instance().load_config(self.get_plugin_name(), skip_inst_dir=True,
                                                          must_exist=True)

        if config.has_section('General') and config['General'].get('Default version') is not None:
            return config['General']['Default version']

        config_files = ConfigManager.get_instance().find_config_files(self.get_plugin_name(), skip_inst_dir=False,
                                                                      starts_with=True)
        if len(config_files) == 0:
            raise Exception('No configuration files found for \'' + self.get_plugin_name() + '\'.')

        if len(config_files) == 1 and config is not None:
            return None

        versions = []

        for version in [config_file[len(self.get_plugin_name()) + 1:][:-4] for config_file in config_files]:
            if len(version) == 0:
                continue

            if len(version.split('.')) > 4:
                continue

            for i in range(4 - len(version.split('.'))):
                version += '.0'
            major, minor, update, other, *_ignore = version.split('.')

            if len(_ignore) > 0:
                continue

            try:
                versions.append((int(major), int(minor), int(update), int(other)))
            except ValueError:
                continue
        versions.sort()

        index = 0
        version = str(versions[-1][index])
        while ConfigManager.get_instance().\
                find_config_file(self.get_plugin_name() + '_' + version, skip_inst_dir=True) is None:
            index += 1
            version += '.' + str(versions[-1][index])

        return version

    # TODO consider renaming to something like get_property(...)
    def get_config_value(self, key, required=False):
        config = self.get_config()

        if config is not None:
            # TODO try getting rid of the General bit. Some config files should be treated as normal property files.
            # TODO an alternative is to try and iterate through each section and see if the key is found in it
            if config.has_section('General') and config['General'].get(key) is not None:
                return config['General'][key]
            else:
                if required:
                    raise Exception('The property ' + key + ' was not found in the ' + self.get_plugin_name() +
                                    ' configuration file.')
        else:
            if required:
                raise Exception('The ' + self.get_plugin_name() + ' configuration file was not found.')

    def get_config(self, ignore_versions=False):
        if ConfigManager.get_instance().get_config(self.get_plugin_name()) is not None:
            return ConfigManager.get_instance().get_config(self.get_plugin_name())

        config = ConfigManager.get_instance().load_config(self.get_plugin_name(), save_config=False)

        if not ignore_versions and self.version is not None:
            version_config = ConfigManager.get_instance().load_config(self.get_plugin_name() + '_' + self.version,
                                                                      save_config=False)
            if version_config is not None:
                ConfigManager.merge(version_config, config)
                config = version_config

        if config is not None:
            ConfigManager.get_instance().set_config(self.get_plugin_name(), config)

        return config

    def get_plugin_name(self):
        plugin_name = self.name

        if plugin_name is None:
            plugin_name = self.__class__.__name__

        return plugin_name

    install_dir = None
    name = None
    base_class = None
    implementations = None
    # TODO consider changing name
    supported_implementations = None
    version = None
