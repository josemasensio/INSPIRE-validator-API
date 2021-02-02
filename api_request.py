import requests, json, datetime, webbrowser, socket
from variables import ets_ids, test_object, my_ip, chrome_path, validator_url
from requests.exceptions import ConnectionError
#Sacar la ipo local de nuestro validador

def api_request():
    _ets_url = validator_url + '/ExecutableTestSuites.json?fields=*' #Nombres de los ETS

    # Dato que se va a testear
    # testdata_url = "http://{0}/Proyectos/HelpDesk-Issues/ExampleMetadata/Dataset_metadata_2.0_example.xml".format(my_ip)


    _now = datetime.datetime.now() #Hora actual para el reporte
    # test_name = 'Common Requirements for ISO/TC 19139:2007 based INSPIRE metadata records.' #Nombre del test que queremos utilizar
    _testrun_url = validator_url + '/TestRuns' #Direccion API para lanzar los test-report
    _testrun_id =  _testrun_url + "/{0}" #Direccion API para ver el progreso del test que estamos corriendo
    _service_ids = ["EIDc837298f-a10e-42d1-88f2-f1415cbbb463","EIDed2d3501-d700-4ff9-b9bf-070dece8ddbd","EID11571c92-3940-4f42-a6cd-5e2b1c6f4d93","EID0ff73873-5601-41ff-8d92-3fb1fbba3cf2","EID174edf55-699b-446c-968c-1892a4d8d5bd","EID074570ad-d720-47b3-af79-d54201793404","EIDeec9d674-d94b-4d8d-b744-1309c6cae1d2","EID550ceacf-b3cb-47a0-b2dd-d3edb18344a9"]

    #Comprobamos que la URL del ETS esté accesible
    try:
        _ets_response = requests.get(_ets_url)
        _executed = False
        #Parseamos la respuesta que nos da para sacar los nombres de los ETS
        if (ets_ids[0] in _service_ids):
            _test_object_type = "serviceEndpoint"
        else:
            _test_object_type = "data"
        
        _api_response = json.loads(_ets_response.text)

        for ets_test_object in _api_response["EtfItemCollection"]["executableTestSuites"]["ExecutableTestSuite"]:
            if ets_test_object['id'] in ets_ids and _executed == False:
                _executed = True
                test_name = ets_test_object["label"]
                #Creamos el JSON para enviar el test report al validador
                testRunRequest_json = {"label": "Test run on {0} - {1} with {2}".format(_now.strftime("%H:%M"), ("{0}.{1}.{2}".format(_now.day, _now.month, _now.year)), test_name),
                            # "executableTestSuiteIds": [ets_test_object["id"]],
                            "executableTestSuiteIds": ets_ids,
                            # "executableTestSuiteIds": ['EID09820daf-62b2-4fa3-a95f-56a0d2b7c4d8','EID63f586f0-080c-493b-8ca2-9919427440cc','EID499937ea-0590-42d2-bd7a-1cafff35ecdb','EID61070ae8-13cb-4303-a340-72c8b877b00a'],
                            "arguments": {
                                "files_to_test": ".*",
                                "tests_to_execute": ".*",
                                "connectivity_tolerance": "1"
                            },
                            "testObject": {
                                "resources": {
                                        # data para mandar un fichero, serviceEndpoint para mandar un servicio
                                        _test_object_type: test_object
                                        # "serviceEndpoint": testdata_url + "?SERVICE=WFS&REQUEST=GetCapabilities"
                                        
                                    }
                                }
                            }
                print("post sent")
                #Enviamos la peticion de test
                _post_request = requests.post(_testrun_url, data=json.dumps(testRunRequest_json), headers={'Content-Type':'application/json'})
                #parseamos la respuesta del servidor para ver que todo ha ido bien y coger la id que nos ha asignado
                _post_json = json.loads(_post_request.text)
                if _post_request.status_code >= 400:
                    print("Something went wrong, please check the following error message: {0}".format(_post_json["error"]))
                else: 
                    print("Validation has started, please wait until this is completed")
                    _test_id = _post_json["EtfItemCollection"]["testRuns"]["TestRun"]["id"]
                    _actual_progress = -1
                    _total_progress = 0

                    #Comprobar como va el reporte para darle feedback al usuario
                    while _actual_progress != _total_progress:
                        _progress = requests.get(_testrun_id.format(_test_id) + "/progress/")
                        _progress_json = json.loads(_progress.text)
                        if "error" in _progress_json:
                            print("An error ocurred: {0}".format(_progress_json["error"]))
                        else:
                            _old_progress = _actual_progress
                            _actual_progress = _progress_json["val"]
                            _total_progress = _progress_json["max"]
                            _log = _progress_json["log"]
                            
                            #Dar feedback solo cuando el tiempo se actualice para no saturar
                            if (_old_progress != _actual_progress):
                                print("{0} of {1} progress done".format(_actual_progress, _total_progress))
                    
                    #Una vez terminado el test, recoger el fichero y lo abrimos en el navegador. Tambien se puede recibir en json.
                    print("opening report")
                    _report_url = _testrun_id.format(_test_id) + ".html"
                    webbrowser.get(chrome_path).open(_report_url)
                    return [_testrun_url, _test_id]
    except ConnectionError:
        print("The server is not available")
        