import subprocess
import time

from plugins.display.display_handler import DisplayHandler


class XrandrDisplayHandler(DisplayHandler):

    def change_resolution(self, parameters):
        left = 0
        right = 1
        resolutions = [r for r in parameters.split(' ') if r != '']

        if len(resolutions) == 1:
            resolutions.append('current')

        if len(resolutions) > 2:
            raise Exception('Max 2 resolutions allowed.')

        # TODO need to add check that ensures that the outputs matches the resolutions (Size)

        outputs = self.get_display_outputs()

        if resolutions[left] == 'off' or (resolutions[left] == 'current' and outputs[left]['on'] == False):
            outputs[left]['on'] = False
            outputs[left]['primary'] = False
            outputs[right]['primary'] = True
        else:
            outputs[left]['on'] = True
            if resolutions[left] not in ['current', 'auto']:
                # TODO consider removing this check since it is done in build_output again
                if not resolutions[left] in outputs[left]['modes']:
                    raise Exception('Unknown mode: ' + resolutions[left])
            if resolutions[left] != 'current':
                outputs[left]['mode'] = resolutions[left]

        if len(outputs) > 1:
            if resolutions[right] == 'off' or (resolutions[right] == 'current' and outputs[right]['on'] == False):
                outputs[right]['on'] = False
                outputs[right]['primary'] = False
                outputs[left]['primary'] = True
            else:
                outputs[right]['on'] = True
                if resolutions[right] not in ['current', 'auto']:
                    # TODO consider removing this check since it is done in build_output again
                    if not resolutions[right] in outputs[right]['modes']:
                        raise Exception('Unknown mode: ' + resolutions[right])
                if resolutions[right] != 'current':
                    outputs[right]['mode'] = resolutions[right]

        xrandr_cmd = 'xrandr ' + self.build_xrandr_parameters(outputs)
        print(xrandr_cmd)
        subprocess.Popen(xrandr_cmd.split(' ')).wait()
        time.sleep(10)

    def save_resolution(self):
        self.saved_outputs = self.get_display_outputs()

    def restore_resolution(self):
        time.sleep(2)
        # TODO first make sure that I actually need to restore the resolution
        xrandr_cmd = 'xrandr ' + self.build_xrandr_parameters(self.saved_outputs)
        print(xrandr_cmd)
        subprocess.Popen(xrandr_cmd.split(' ')).wait()

    def get_display_outputs(self):
        outputs = []

        xrandr_output = subprocess.getoutput(['xrandr', '-q'])

        output = {}
        mode_and_offset = ''
        for line in xrandr_output.split('\n'):
            tokens = [t for t in line.split(' ') if t is not '']
            if tokens[1] in ['connected', 'disconnected']:
                if len(output) > 0:
                    outputs.append(output)
                    output = {}

            if tokens[1] == 'connected':
                output['name'] = tokens[0]
                output['on'] = False
                output['mode'] = None
                output['offset'] = None
                output['modes'] = []
                if tokens[2] == 'primary':
                    output['primary'] = True
                    mode_and_offset = tokens[3]
                else:
                    output['primary'] = False
                    mode_and_offset = tokens[2]

            if len(output) > 0:
                if mode_and_offset.startswith(tokens[0]) and line.find('*') >= 0:
                    output['on'] = True
                    output['mode'], output['offset'], _ignore = mode_and_offset.split('+')
                if tokens[0] != output['name']:
                    output['modes'].append(tokens[0])

        if len(output) > 0:
            outputs.append(output)

        # need to make sure outputs are ordered
        if len(outputs) > 1:
            left_output = None
            right_output = None

            if outputs[0].get('offset') == '0':
                left_output = outputs[0]
                right_output = outputs[1]
            elif outputs[1].get('offset') == '0':
                left_output = outputs[1]
                right_output = outputs[0]
            elif outputs[0].get('offset') is not None and int(outputs[0]['offset']) > 0:
                left_output = outputs[1]
                right_output = outputs[0]
            elif outputs[1].get('offset') is not None and int(outputs[1]['offset']) > 0:
                left_output = outputs[0]
                right_output = outputs[1]

            outputs = [left_output, right_output]
        return outputs

    def build_xrandr_parameters(self, outputs):
        left = 0
        right = 1

        if len(outputs) > 1:
            if not outputs[left]['on'] and not outputs[right]['on']:
                raise Exception('Both outputs cannot be turned off.')
            if outputs[left]['primary'] and outputs[right]['primary']:
                raise Exception('Both outputs cannot be primary.')
            if outputs[left].get('offset') is not None and int(outputs[left]['offset']) > 0 and \
                    outputs[right].get('offset') is not None and int(outputs[right]['offset']) > 0:
                        raise Exception('Both outputs cannot have an offset > 0.')
        else:
            if outputs[left]['off']:
                raise Exception('Cannot turn the only output off.')

        if outputs[left]['mode'] == 'auto':
            outputs[left]['on'] = True
        left_output = '--output ' + outputs[left]['name']
        if outputs[left]['on']:
            if outputs[left]['primary']:
                left_output += ' --primary'
            if outputs[left]['mode'] == 'auto':
                left_output += ' --auto'
            else:
                if not outputs[left]['mode'] in outputs[left]['modes']:
                    raise Exception('Unknown mode: ' + outputs[left]['mode'])
                left_output += ' --mode ' + outputs[left]['mode']
            if outputs[left]['primary']:
                left_output += ' --panning ' + outputs[left]['mode']
        else:
            left_output += ' --off'

        right_output = ''
        if len(outputs) > 1:
            if outputs[right]['mode'] == 'auto':
                outputs[right]['on'] = True
            right_output = '--output ' + outputs[right]['name']
            if outputs[right]['on']:
                if outputs[right]['primary']:
                    right_output += ' --primary'
                if outputs[right]['mode'] == 'auto':
                    right_output += ' --auto'
                else:
                    if not outputs[right]['mode'] in outputs[right]['modes']:
                        raise Exception('Unknown mode: ' + outputs[right]['mode'])
                    right_output += ' --mode ' + outputs[right]['mode']
                if outputs[right]['primary']:
                    right_output += ' --panning ' + outputs[right]['mode']
                right_output += ' --right-of ' + outputs[left]['name']
            else:
                right_output += ' --off'

        return left_output + ' ' + right_output

    saved_outputs = None
