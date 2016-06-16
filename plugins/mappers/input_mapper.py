from plugins.plugin_handler import Plugin


# TODO Remove all structs. Replace with on-the-fly class creation or rather use a dictionary (prefer the dictionary)
class Struct:
    pass


# TODO Add a dry run of the actual mapping process for validation, since errors can only be
# detected when the actual mapping is done.
class InputMapper(Plugin):

    def init(self, install_dir):
        self.install_dir = install_dir
        self.load_plugins('plugins.mappers', InputMapper)

    def set_mappings(self, mappings):
        self.input_mappings = []
        for mapping in mappings:
            translated_mapping = Struct()

            translated_mapping.virtual = self.definitions['Virtual Devices'][mapping.virtual]
            translated_mapping.physical = self.definitions['Physical Devices'][mapping.physical]
            if mapping.description is None:
                translated_mapping.description = ''
            else:
                translated_mapping.description = mapping.description

            self.input_mappings.append(translated_mapping)

    def activate(self):
        pass

    def deactivate(self):
        pass

    input_mappings = None
    definitions = None
