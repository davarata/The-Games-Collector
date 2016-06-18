import utils
from plugins.plugin_handler import Plugin


# TODO Add a dry run of the actual mapping process for validation, since errors can only be
# detected when the actual mapping is done.
class InputMapper(Plugin):

    def init(self, install_dir):
        self.install_dir = install_dir
        self.load_plugins('plugins.mappers', InputMapper)

    def set_mappings(self, mappings):
        self.input_mappings = []
        for mapping in mappings:
            translated_mapping = {
                'virtual': self.get_definitions()['Virtual Devices'][mapping['virtual']],
                'physical': self.get_definitions()['Physical Devices'][mapping['physical']]
            }

            if mapping['description'] is None:
                translated_mapping['description'] = ''
            else:
                translated_mapping['description'] = mapping['description']

            self.input_mappings.append(translated_mapping)

    def get_definitions(self):
        if self.definitions is None:
            self.definitions = utils.load_config(self.name, extension='mapper', skip_user_dirs=True, must_exist=True)

        return self.definitions

    def activate(self):
        pass

    def deactivate(self):
        pass

    input_mappings = None
    definitions = None
