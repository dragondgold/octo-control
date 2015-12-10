import requests
import argparse
import sys

__author__ = 'Andres Torti'


class OctoprintAPI:
    """
    This class is an interface for the Octoprint server API
    """

    def __init__(self, address, port, api_key):
        self.host = address
        self.s = requests.Session()
        self.s.headers.update({'X-Api-Key': api_key,
                               'Content-Type': 'application/json'})

        # Base address for all the requests
        self.base_address = 'http://' + address + ':' + str(port)

    def is_printer_connected(self):
        """
        Checks if the printer is connected to the Octoprint server
        :return: True if connected, False if not
        """
        if self.s.get(self.base_address + '/api/printer').status_code != 200:
            return False
        else:
            return True

    def get_printer_status(self):
        """
        Get the printer status
        :return: string with the printer status (Operational, Disconnected, ...). Returns an empty string
                    if there was an error trying to get the status.
        """
        data = self.s.get(self.base_address + '/api/printer').content.decode('utf-8').split('\n')
        for line in data:
            if 'text' in line:
                # check if null
                if 'null' in line:
                    return ''
                else:
                    return line[line.find(':')+1:line.find(',')]
        return ''

    def set_bed_temp(self, temp):
        """
        Set the bed temperature
        :param temp: desired bed temperature
        """
        self.s.post(self.base_address + '/api/printer/bed', json={'command': 'target', 'target': temp})

    def get_bed_temp(self):
        """
        Get the current bed temperature
        :return: current bed temperature. Returns -1 y there was some error getting the temperature.
        """
        data = self.s.get(self.base_address + '/api/printer/bed').content.decode('utf-8').split('\n')
        for line in data:
            if 'target' in line:
                return int(float(line[line.find(':')+1:]))
        return -1

    def pause_job(self):
        """
        Pause the current job
        """
        self.s.post(self.base_address + '/api/job', json={'command': 'pause'})

    def resume_job(self):
        """
        Resume the current job
        """
        self.s.post(self.base_address + '/api/job', json={'command': 'pause'})

    def start_job(self):
        """
        Start printing with the currently selected file
        """
        self.s.post(self.base_address + '/api/job', json={'command': 'start'})

    def cancel_job(self):
        """
        Cancel the current job
        """
        self.s.post(self.base_address + '/api/job', json={'command': 'cancel'})

    def get_version(self):
        """
        Get Octoprint version
        :return: string with Octoprint version. It returns '0.0.0' if there was an error obtaining the version
        """
        data = self.s.get(self.base_address + '/api/version').content.decode('utf-8').split('\n')
        for line in data:
            if 'server' in line:
                return line[line.find(':')+3:-1]
        return '0.0.0'

    def get_print_progress(self):
        """
        Get the print progress as a percentage
        :return: float indicating the current print progress
        """
        data = self.s.get(self.base_address + '/api/job').content.decode('utf-8').split('\n')
        for line in data:
            if 'completion' in line:
                # check if null
                if 'null' in line:
                    return 0
                else:
                    return int(float(line[line.find(':')+1:line.find(',')]))
        return 0

    def get_total_print_time(self):
        """
        Get the total print time in seconds
        :return: total print time in seconds. Returns -1 y there was some error getting the time.
        """
        data = self.s.get(self.base_address + '/api/job').content.decode('utf-8').split('\n')
        for line in data:
            if 'estimatedPrintTime' in line:
                # check if null
                if 'null' in line:
                    return -1
                else:
                    return int(float(line[line.find(':')+1:line.find(',')]))
        return -1

    def get_print_time_left(self):
        """
        Get the print time left of the current job in seconds
        :return: print time left in seconds. Returns -1 y there was some error getting the time.
        """
        data = self.s.get(self.base_address + '/api/job').content.decode('utf-8').split('\n')
        for line in data:
            if 'printTimeLeft' in line:
                # check if null
                if 'null' in line:
                    return -1
                else:
                    return int(float(line[line.find(':')+1:]))
        return -1

    def get_elapsed_print_time(self):
        """
        Get the elapsed print time in seconds of the current job
        :return: elapsed print time in seconds. Returns -1 y there was some error getting the time.
        """
        data = self.s.get(self.base_address + '/api/job').content.decode('utf-8').split('\n')
        for line in data:
            if 'printTime' in line:
                # check if null
                if 'null' in line:
                    return -1
                else:
                    return int(float(line[line.find(':')+1:line.find(',')]))
        return -1

    def get_file_printing(self):
        """
        Get the name of the current file being printed
        :return: name of the file being printed. Returns an empty string if no file is being printed.
        """
        data = self.s.get(self.base_address + '/api/job').content.decode('utf-8').split('\n')
        for line in data:
            if 'name' in line:
                # check if null
                if 'null' in line:
                    return ''
                else:
                    return line[line.find(':')+1:line.find(',')].replace('"', '').strip()
        return ''

    def send_gcode(self, gcode):
        """
        Sends one or multiple comma separated G-codes to the printer
        :param gcode: G-Code/s to send as a list containing all the G-codes to send
        """
        self.s.post(self.base_address + '/api/printer/command', json={'commands': gcode})

    def select_file(self, file_name, location, print):
        self.s.post(self.base_address + '/api/files/' + location + '/'+ file_name, json={'command': 'select', 'print': print})

    def get_extruder_target_temp(self):
        """
        Get the target extruder temperature in degrees celsius
        :return: target extruder temperature in degrees celsius. Returns -1 y there was some error getting the temperature.
        """
        data = self.s.get(self.base_address + '/api/printer/tool').content.decode('utf-8').split('\n')
        for line in data:
            if 'target' in line:
                if 'null' in line:
                    return -1
                else:
                    return int( round(float(line[line.find(':')+1:line.find(',')]), 0) )
        return -1

    def get_extruder_current_temp(self):
        """
        Get the current extruder temperature in degrees celsius
        :return: current extruder temperature in degrees celsius. Returns -1 y there was some error getting the temperature.
        """
        data = self.s.get(self.base_address + '/api/printer/tool').content.decode('utf-8').split('\n')
        for line in data:
            if 'actual' in line:
                return int( round(float(line[line.find(':')+1:line.find(',')]), 0) )
        return -1

if __name__ == '__main__':
    # First, check if we have any arguments
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()

        # apikey, host, and port are required arguments to communicate with Octoprint
        parser.add_argument('--apikey', help='Octoprint\'s API Key', type=str, required=True)
        parser.add_argument('--host', help='Octoprint host address, port must not be specified here', type=str, required=True)
        parser.add_argument('--port', help='Port on which Octoprint is running', type=int, required=True)

        # Optional arguments
        parser.add_argument('--printer-connected', help='Checks if there is a printer connected', action='store_true')
        parser.add_argument('--printer-status', help='Gets the printer status (Operational, Disconnected, ...)',
                            action='store_true')

        parser.add_argument('--print-progress', help='Gets the print progress as percentage', action='store_true')
        parser.add_argument('--total-time', help='Gets the total print time in seconds', action='store_true')
        parser.add_argument('--left-time', help='Gets the time left for the print to finish', action='store_true')
        parser.add_argument('--elapsed-time', help='Gets the elapsed print time', action='store_true')

        parser.add_argument('--printing-file', help='Gets the name of the file being printed', action='store_true')
        parser.add_argument('--send-gcode', help='Sends specified G-code/s to the printer. Multiple G-Codes can be '
                                                 'specified', nargs='*', type=str, metavar=('GCODE'))

        parser.add_argument('--select-file', help='Selects an already uploaded file. FILE_LOCATION can be'
                                                  ' \'local\' or \'sdcard\'', type=str, nargs=2,
                            metavar=('FILE_NAME', 'FILE_LOCATION'))
        parser.add_argument('--print', help='When used with --select-file will also start printing the selected file',
                            action='store_true')


        parser.add_argument('--set-bed-temp', help='Sets the bed temperature in degrees celsius', type=int,
                            metavar=('BED_TEMP'))
        parser.add_argument('--get-bed-temp', help='Gets the current bed temperature', action='store_true')

        parser.add_argument('--ext-temp', help='Gets the current extruder temperature in degrees celsius',
                            action='store_true')
        parser.add_argument('--ext-target', help='Gets the target extruder temperature in degrees celsius',
                            action='store_true')

        parser.add_argument('--pause', help='Pause the current job', action='store_true')
        parser.add_argument('--resume', help='Resume the current job', action='store_true')
        parser.add_argument('--start', help='Starts printing with the currently selected file', action='store_true')
        parser.add_argument('--cancel', help='Cancel the current job', action='store_true')

        parser.add_argument('--version', help='Reads Octoprint version', action='store_true')

        # Parse the arguments!
        args = parser.parse_args()

        # Create the Octoprint interface
        octo_api = OctoprintAPI(args.host, args.port, args.apikey)

        # Printer options
        if args.printer_connected:
            print(octo_api.is_printer_connected())

        elif args.printer_status:
            print(octo_api.get_printer_status())

        elif args.print_progress:
            print(octo_api.get_print_progress())

        elif args.total_time:
            print(octo_api.get_total_print_time())

        elif args.left_time:
            print(octo_api.get_print_time_left())

        elif args.elapsed_time:
            print(octo_api.get_elapsed_print_time())

        elif args.printing_file:
            print(octo_api.get_file_printing())

        elif args.send_gcode:
            octo_api.send_gcode(args.send_gcode)

        elif args.select_file:
            octo_api.select_file(args.select_file[0], args.select_file[1], args.print)

        # Extruder
        elif args.ext_temp:
            print(octo_api.get_extruder_current_temp())

        elif args.ext_target:
            print(octo_api.get_extruder_target_temp())

        # Bed options
        elif args.set_bed_temp:
            if args.set_bed_temp < 0:
                print('Bed temperature can\'t be negative')
            else:
                octo_api.set_bed_temp(args.set_bed_temp)

        elif args.get_bed_temp:
            print(octo_api.get_bed_temp())

        # Job options
        elif args.pause:
            octo_api.pause_job()

        elif args.resume:
            octo_api.resume_job()

        elif args.start:
            octo_api.start_job()

        elif args.cancel:
            octo_api.cancel_job()

        # Other options
        elif args.version:
            print(octo_api.get_version())
