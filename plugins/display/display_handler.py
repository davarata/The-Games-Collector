from plugins.plugin_handler import Plugin


class DisplayHandler(Plugin):

    def init(self, install_dir):
        self.install_dir = install_dir
        self.load_plugins('plugins.display', DisplayHandler)

    def change_resolution(self):
        pass

    def save_resolution(self):
        pass

    def restore_resolution(self):
        pass
