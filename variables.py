import socket

def _get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

my_ip = _get_ip_address()
validator_url = 'http://{0}:8080/validator/v2'.format(my_ip)#IP del validador
test_object = 'URL to data. Localhost available via https://{0}/'.format(my_ip) 
chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s' #PATH de chrome para abrir el report
validator_name = "validator-v2021.0"
ets_ids = ["ID from test-name-is.json. To update run $python ./__main__.py -r"]
