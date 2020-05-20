import requests
import argparse
import sys
import json

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

    def connect_to_printer(self, port=None, baudrate=None, printer_profile=None, save=None, autoconnect=None):
        """
        Connects to the printer
        :param port: [Optional] port where the printer is connected (ie: COMx in Windows, /dev/ttyXX in Unix systems).
                if not specified the current selected port will be used or if no port is selected auto detection will
                be used
        :param baudrate: [Optional] baud-rate, if not specified the current baud-rate will be used ot if no baud-rate
                is selected auto detection will be used
        :param printer_profile: [Optional] printer profile to be used for the connection, if not specified the default
                one will be used
        :param save: [Optional] whether to save or not the connection settings
        :param autoconnect: [Optional] whether to connect automatically or not on the next Ocotprint start
        """
        data = {'command': 'connect'}
        if port is not None:
            data['port'] = port
        if baudrate is not None:
            data['baudrate'] = baudrate
        if printer_profile is not None:
            data['printerProfile'] = printer_profile
        if save is not None:
            data['save'] = save
        if autoconnect is not None:
            data['autoconnect'] = autoconnect

        r = self.s.post(self.base_address + '/api/connection', json=data)
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def is_printer_connected(self):
        """
        Checks if the printer is connected to the Octoprint server
        :return: True if connected, False if not
        """
        r = self.s.get(self.base_address + '/api/printer')
        if r.status_code != 200:
            raise Exception('Error trying to get printer connection status')
        try:
            return json.loads(r.content.decode('utf-8'))["state"]["flags"]["operational"]
        except:
            raise Exception('Error trying to get printer connection status')

    def get_printer_status(self):
        """
        Get the printer status
        :return: string with the printer status (Operational, Disconnected, ...). Returns an empty string
                    if there was an error trying to get the status.
        :raise: TypeError when failed to get printer status
        """
        r = self.s.get(self.base_address + '/api/printer')
        if r.status_code != 200:
           raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8'))) 
        try:
            return json.loads(r.content.decode('utf-8'))["state"]["text"]
        except:
            raise Exception('Error trying to get printer status')

    def set_bed_temp(self, temp):
        """
        Set the bed temperature
        :param temp: desired bed temperature
        """
        r = self.s.post(self.base_address + '/api/printer/bed', json={'command': 'target', 'target': temp})
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def get_bed_temp(self):
        """
        Get the current bed temperature
        :return: current bed temperature. Returns -1 y there was some error getting the temperature.
        """
        r = self.s.get(self.base_address + '/api/printer/bed')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["bed"]["actual"]
        except:
            raise Exception("Error getting bed temperature")

    def pause_job(self):
        """
        Pause the current job
        """
        r = self.s.post(self.base_address + '/api/job', json={'command': 'pause'})
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def resume_job(self):
        """
        Resume the current job
        """
        r = self.s.post(self.base_address + '/api/job', json={'command': 'pause'})
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def start_job(self):
        """
        Start printing with the currently selected file
        """
        r = self.s.post(self.base_address + '/api/job', json={'command': 'start'})
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def cancel_job(self):
        """
        Cancel the current job
        """
        r = self.s.post(self.base_address + '/api/job', json={'command': 'cancel'})
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def get_version(self):
        """
        Get Octoprint version
        :return: string with Octoprint version. It returns '0.0.0' if there was an error obtaining the version
        """
        r = self.s.get(self.base_address + '/api/version')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["server"]
        except:
            raise Exception("Error getting Octoprint version")

    def get_print_progress(self):
        """
        Get the print progress as a percentage
        :return: float indicating the current print progress
        """
        r = self.s.get(self.base_address + '/api/job')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["progress"]["completion"]
        except:
            raise Exception('Error reading print progress')

    def get_total_print_time(self):
        """
        Get the total print time in seconds
        :return: total print time in seconds
        """
        r = self.s.get(self.base_address + '/api/job')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["job"]["estimatedPrintTime"]
        except:
            raise Exception('Error reading total print time')

    def get_print_time_left(self):
        """
        Get the print time left of the current job in seconds
        :return: print time left in seconds
        """
        r = self.s.get(self.base_address + '/api/job')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["progress"]["printTimeLeft"]
        except:
            raise Exception('Error reading print time left')

    def get_elapsed_print_time(self):
        """
        Get the elapsed print time in seconds of the current job
        :return: elapsed print time in seconds
        """
        r = self.s.get(self.base_address + '/api/job')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["progress"]["printTime"]
        except:
            raise Exception('Error reading elapsed print time')

    def get_file_printing(self):
        """
        Get the name of the current file being printed
        :return: name of the file being printed
        """
        r = self.s.get(self.base_address + '/api/job')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["job"]["file"]["name"]
        except:
            raise Exception('Error reading filename being printed')

    def send_gcode(self, gcode):
        """
        Sends one or multiple comma separated G-codes to the printer
        :param gcode: G-Code/s to send as a list containing all the G-codes to send
        """
        r = self.s.post(self.base_address + '/api/printer/command', json={'commands': gcode})
        if r.status_code != 204:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def select_file(self, file_name):
        r = self.s.post(self.base_address + '/api/files/local/' + file_name, json={'command': 'select', 'print': True})
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))

    def get_extruder_target_temp(self):
        """
        Get the target extruder temperature in degrees celsius
        :return: target extruder temperature in degrees celsius
        """
        r = self.s.get(self.base_address + '/api/printer/tool')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["tool0"]["target"]
        except:
            raise Exception('Error retrieving extruder target temperature')

    def get_extruder_current_temp(self):
        """
        Get the current extruder temperature in degrees celsius
        :return: current extruder temperature in degrees celsius
        """
        r = self.s.get(self.base_address + '/api/printer/tool')
        if r.status_code != 200:
            raise Exception("Error: {code} - {content}".format(code=r.status_code, content=r.content.decode('utf-8')))
        try:
            return json.loads(r.content.decode('utf-8'))["tool0"]["actual"]
        except:
            raise Exception('Error retrieving extruder temperature')


def run_and_handle(method, *_args):
    """
    Just a clean way to call any function and print the returned value to 'stdout' if valid or print the error message to
        to 'stderr'
    :param method: function to execute
    :param _args: arguments to pass to the function
    :return: None
    """
    try:
        result = method(*_args)
        if result is not None:
            print(result)
    except Exception as e:
        print(str(e), file=sys.stderr)

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

        parser.add_argument('--connect', help='Connect to the printer. If no other connection parameter is specified '
                                              'the default values in Octoprint will be used, see --printer-port,'
                                              ' --baudrate, --profile, --save and --autoconnect', action='store_true')
        parser.add_argument('--printer-port', help='Port where the printer is connected ie: /dev/tty02, COM2 and so on',
                            type=str)
        parser.add_argument('--baudrate', help='Baud-rate for the connection to the printer', type=int)
        parser.add_argument('--profile', help='Printer profile to be used in the connection, the name here is the name'
                                              'specified in the profile identifier, not the profile name', type=str)
        parser.add_argument('--save', help='Save the connection settings when connecting', action='store_true',
                            default=None)
        parser.add_argument('--autoconnect', help='Connect automatically on the next Octoprint start',
                            action='store_true', default=None)

        parser.add_argument('--print-progress', help='Gets the print progress as percentage', action='store_true')
        parser.add_argument('--total-time', help='Gets the total print time in seconds', action='store_true')
        parser.add_argument('--left-time', help='Gets the time left for the print to finish', action='store_true')
        parser.add_argument('--elapsed-time', help='Gets the elapsed print time', action='store_true')

        parser.add_argument('--printing-file', help='Gets the name of the file being printed', action='store_true')
        parser.add_argument('--send-gcode', help='Sends specified G-code/s to the printer. Multiple G-Codes can be '
                                                 'specified', nargs='*', type=str, metavar=('GCODE'))

        parser.add_argument('--select-file', help='Selects an already uploaded file. FILE_LOCATION can be'
                                                  ' \'local\' or \'sdcard\'', type=str, nargs=1,
                            metavar=('FILE_NAME'))
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

        parser.add_argument('--octo-version', help='Reads Octoprint version', action='store_true')
        parser.add_argument('--version', help='Get script version', action='store_true')

        # Parse the arguments!
        args = parser.parse_args()

        # Create the Octoprint interface
        octo_api = OctoprintAPI(args.host, args.port, args.apikey)

        # Printer options
        if args.printer_connected:
            run_and_handle(octo_api.is_printer_connected)

        elif args.connect:
            run_and_handle(octo_api.connect_to_printer, args.printer_port, args.baudrate, args.profile, args.save,
                           args.autoconnect)

        elif args.printer_status:
            run_and_handle(octo_api.get_printer_status)

        elif args.print_progress:
            run_and_handle(octo_api.get_print_progress)

        elif args.total_time:
            run_and_handle(octo_api.get_total_print_time)

        elif args.left_time:
            run_and_handle(octo_api.get_print_time_left)

        elif args.elapsed_time:
            run_and_handle(octo_api.get_elapsed_print_time)

        elif args.printing_file:
            run_and_handle(octo_api.get_file_printing)

        elif args.send_gcode:
            run_and_handle(octo_api.send_gcode, args.send_gcode)

        elif args.select_file:
            run_and_handle(octo_api.select_file, args.select_file[0])

        # Extruder
        elif args.ext_temp:
            run_and_handle(octo_api.get_extruder_current_temp)

        elif args.ext_target:
            run_and_handle(octo_api.get_extruder_target_temp)

        # Bed options
        elif args.set_bed_temp:
            if args.set_bed_temp < 0:
                print('Error, bed temperature can\'t be negative', file=sys.stderr)
            else:
                run_and_handle(octo_api.set_bed_temp, args.set_bed_temp)

        elif args.get_bed_temp:
            run_and_handle(octo_api.get_bed_temp)

        # Job options
        elif args.pause:
            run_and_handle(octo_api.pause_job)

        elif args.resume:
            run_and_handle(octo_api.resume_job)

        elif args.start:
            run_and_handle(octo_api.start_job)

        elif args.cancel:
            run_and_handle(octo_api.cancel_job)

        # Other options
        elif args.octo_version:
            run_and_handle(octo_api.get_version)

        elif args.version:
            print('1.0.1')
