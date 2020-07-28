from plugins.plugin_handler import Plugin


class DisplayHandler(Plugin):

    def init(self, install_dir):
        self.install_dir = install_dir
        self.load_plugins('plugins.display', DisplayHandler, ignore_versions=True)

    def change_resolution(self, parameters):
        pass

    def save_resolution(self):
        pass

    def restore_resolution(self):
        pass
