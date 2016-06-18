import configparser
import os
import subprocess

import utils
from plugins.mappers.input_mapper import InputMapper


class AntiMicroMapper(InputMapper):

    def __init__(self):
        definitions_file = utils.get_config_file('antimicro.mapper')
        self.definitions = configparser.ConfigParser()
        self.definitions.read(definitions_file)

    def activate(self):
        # button, trigger, stickbutton, dpadbutton
        entry_xml = \
            '<{0} index="{1}">' + os.linesep + \
            ' <slots>' + os.linesep + \
            '  <slot>' + os.linesep + \
            '   <code>{2}</code>' + os.linesep + \
            '   <mode>keyboard</mode>' + os.linesep + \
            '  </slot>' + os.linesep + \
            ' </slots>' + os.linesep + \
            '</{0}>'

        sets = {}
        for mapping in self.input_mappings:
            parameters = mapping['physical'].split(',')
            trigger_value = parameters[0]
            trigger_type = parameters[1]
            if len(parameters) == 3:
                index = parameters[2]
            else:
                index = '1'

            if trigger_type == 'button':
                set_id = 'button'
            else:
                set_id = trigger_type + ' ' + index
                trigger_type += 'button'

            if sets.get(set_id) is None:
                sets[set_id] = []

            sets[set_id].append(
                '<!-- ' +
                mapping['description'] +
                ' -->' +
                os.linesep +
                entry_xml.format(trigger_type, trigger_value, mapping['virtual']))

        mappings_file = open('/tmp/antimicro.gamecontroller.amgp', 'w')
        mappings_file.write('<?xml version="1.0" encoding="UTF-8"?>' + os.linesep)
        mappings_file.write('<gamecontroller configversion="16" appversion="2.12">' + os.linesep)
        mappings_file.write('  <sets>' + os.linesep)
        mappings_file.write('    <set index="1">' + os.linesep)
        indentation = '      '
        for set_id in sets.keys():
            if set_id is not 'button':
                name, index = set_id.split(' ')
                mappings_file.write(indentation + '<' + name + ' index="' + index + '">' + os.linesep)
                indentation += '  '
                for set_entry in sets[set_id]:
                    set_entry = set_entry.replace(os.linesep, os.linesep + indentation)
                    mappings_file.write(indentation + set_entry + os.linesep)
                indentation = indentation[:-2]
                mappings_file.write(indentation + '</' + name + '>' + os.linesep)
            else:
                for set_entry in sets[set_id]:
                    set_entry = set_entry.replace(os.linesep, os.linesep + indentation)
                    mappings_file.write(indentation + set_entry + os.linesep)

        mappings_file.write('    </set>' + os.linesep)
        mappings_file.write('  </sets>' + os.linesep)
        mappings_file.write('</gamecontroller>' + os.linesep)

        mappings_file.close()
        self.antimicro = subprocess.Popen(['antimicro', '--hidden', '--profile', '/tmp/antimicro.gamecontroller.amgp'])

    def deactivate(self):
        self.antimicro.kill()

    name = 'antimicro'
    supported_implementations = {'Keyboard:Xbox360'}
    antimicro = None
