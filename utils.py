import os


def get_config_file(name):
    if os.path.isfile(os.environ.get('HOME') + '/.config/application-launcher/' + name):
        return os.environ.get('HOME') + '/.config/application-launcher/' + name

    if os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + '/' + name):
        return os.path.dirname(os.path.realpath(__file__)) + '/' + name

    return None
