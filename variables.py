import socket

def _get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

my_ip = _get_ip_address()
# test_object_type = "data" #serviceEndpoint
validator_url = 'http://{0}:8080/validator/v2'.format(my_ip)#IP del validador
# test_object = 'http://mapy.geoportal.gov.pl/wss/service/CSWINSP/guest/CSWStartup?SERVICE=CSW&REQUEST=GetRecordById&VERSION=2.0.2&ID=91710ff0-bad2-11e1-afa6-0800200c9a66&OUTPUTFORMAT=application/xml&OUTPUTSCHEMA=http://www.isotc211.org/2005/gmd&ELEMENTSETNAME=full'.format(my_ip) 
# + "?SERVICE=WFS&REQUEST=GetCapabilities"
test_object = 'http://{0}/Proyectos/HelpDesk-Issues/staging-ge.gml'.format(my_ip)
chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s' #PATH de chrome para abrir el report
validator_name = "validator-v2021.0"
ets_ids = ["EID8f869e23-c9e9-4e86-8dca-be30ff421229"]
