import sys
import subprocess
import os
from get_test_ids import refresh_ids
from api_request import api_request
from create_report import transform_validation_errors
from variables import validator_name

directory = os.getcwd()
args = sys.argv
def execute():
        response=api_request()
        try:
                transform_validation_errors(response[0], response[1])
        except TypeError:
                print("The specified file does not exist.")
        except:
                print("Please fix the issue showed above before retrying")

def start():
        subprocess.call([r'{0}\load_ETF.bat'.format(directory), validator_name])
        
def reload():
        subprocess.call([r'{0}\reload_ETF.bat'.format(directory), validator_name])

if len(args) != 1:
        if "--refresh" in args or "-r" in args:
                refresh_ids()
        if "--execute" in args or "-e" in args:
                execute()
        if "--start" in args or "-s" in args:
                start()
        if "--reload" in args or "-rl" in args:
                reload()
        if "--help" in args or "-h" in args:
                print("AVAILABLE COMMANDS:\n")
                print("--help, -h\tOpens help menu\n")
                print("--refresh, -r\tRefresh test-name-id.json file\n")
                print("--reload, -rl\tReload the ETF\n")
                print("--start, -s\tStarts the ETF\n")
                print("--execute, -e\tExecutes the api request and received data transformation\n")
else:
        execute()
