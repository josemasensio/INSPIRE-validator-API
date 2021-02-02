import json, requests, os
_AssertionDictionary = {}
_errorDictionary = {}
_fileName = "./report-result/{0}.log"

def transform_validation_errors(testrun_url, test_id):
    global _fileName
    _remove_old_message_file()
    _data = json.loads(requests.get(testrun_url + "/{0}.json".format(test_id)).text)
    _test_runs = _data["EtfItemCollection"]["testRuns"]
    _referencedItems = _data["EtfItemCollection"]["referencedItems"]
    _TestResults = _referencedItems["testTaskResults"]["TestTaskResult"]
    _error_translations = _referencedItems["translationTemplateBundles"]["TranslationTemplateBundle"]["translationTemplateCollections"]["LangTranslationTemplateCollection"]
    _fileName = _fileName.format(test_id)


    for _error_translation in _error_translations:
        _error_translation = _error_translation["translationTemplates"]["TranslationTemplate"]
        if _error_translation["name"] != "TR.blankLine":
            _errorDictionary[_error_translation["name"]] = _error_translation["$"]
            
    for _TestRun in _test_runs:
        if _test_runs[_TestRun]["status"] == "FAILED":
            _executableTestSuites = _referencedItems["executableTestSuites"]["ExecutableTestSuite"]
            
            if not "id" in _executableTestSuites:
                for _executableTestSuite in _executableTestSuites:
                    _get_TestModule_TestRun(_executableTestSuite)
            else:
                _get_TestModule_TestRun(_executableTestSuites)
        else:
            print("Report returned no errors")

    if not "id" in _TestResults:
        for _TestResult in _TestResults:
            if not "id" in _TestResult:
                for res in _TestResult:
                    _get_TestModule_TestResult(_TestResult)
            else:
                _get_TestModule_TestResult(_TestResult)
    else: 
        _get_TestModule_TestResult(_TestResults)



def _get_TestModule_TestRun(executableTestSuites):
    TestModules = executableTestSuites["testModules"]["TestModule"]
    if not "id" in TestModules:
        for TestModule in TestModules:
            _get_TestCase_TestRun(TestModule)
    else:
        _get_TestCase_TestRun(TestModules)


def _get_TestCase_TestRun(TestModule):
    TestCases = TestModule["testCases"]["TestCase"]
    if not "id" in TestCases:           
        for TestCase in TestCases:
            _get_TestStep_TestRun(TestCase)
    else:     
        _get_TestStep_TestRun(TestCases)


def _get_TestStep_TestRun(TestCase):
    if "testSteps" in TestCase:
        TestSteps = TestCase["testSteps"]["TestStep"]
        if not "id" in TestSteps:           
            for TestStep in TestSteps:
                _get_TestAssertion_TestRun(TestStep)
        else:
            _get_TestAssertion_TestRun(TestSteps)

def _get_AssertionDictionary_TestRun(TestAssertion):
    _AssertionDictionary[TestAssertion["id"]] = TestAssertion["label"]

def _get_TestAssertion_TestRun(TestStep):
    if "testAssertions" in TestStep:
        TestAssertions = TestStep["testAssertions"]["TestAssertion"]
        if not "id" in TestAssertions:
            for TestAssertion in TestAssertions:
                _get_AssertionDictionary_TestRun(TestAssertion)
        else:
            _get_AssertionDictionary_TestRun(TestAssertions)


def _get_TestModule_TestResult(TestResult):
    if "testModuleResults" in TestResult:
        TestModules = TestResult["testModuleResults"]["TestModuleResult"]
    if not "id" in TestResult:
        for TestModule in TestResult:
            _get_TestCase_TestResult(TestModule)
    else:
        _get_TestCase_TestResult(TestResult)


def _get_TestCase_TestResult(TestModule):
    if TestModule["status"] == "FAILED" and 'testCaseResults' in TestModule:
        TestCases = TestModule["testCaseResults"]["TestCaseResult"]
        if not "id" in TestCases:
            for TestCase in TestCases:
                _get_TestStep_result(TestCase)
        else:
            _get_TestStep_result(TestCases)
            
    elif TestModule["status"] == "FAILED" and 'testModuleResults' in TestModule:
        TestModules = TestModule["testModuleResults"]["TestModuleResult"]
        if not "id" in TestModules:
            for TestModule in TestModules:
                _get_TestCase_TestResult(TestModule)
        else:
            _get_TestCase_TestResult(TestModules)

def _get_TestStep_result(TestCase):
    if TestCase["status"] == "FAILED":
        TestSteps = TestCase["testStepResults"]["TestStepResult"]
        if not "id" in TestSteps:           
            for TestStep in TestSteps:
                _transform_TestStep_TestResult(TestStep)
        else:
            _transform_TestStep_TestResult(TestSteps)

def _transform_TestStep_TestResult(TestStep):
    if TestStep["status"]=="FAILED":
        if "testAssertionResults" in TestStep:
            TestAssertions = TestStep["testAssertionResults"]["TestAssertionResult"]
            if not "id" in TestAssertions:
                for TestAssertion in TestAssertions:
                    _get_message_TestResult(TestAssertion)
            else:
                _get_message_TestResult(TestAssertions)
        elif "invokedTests" in TestStep:
                _TestResults = TestStep["invokedTests"]

                if "TestStepResult" in _TestResults:
                    TestSteps = _TestResults["TestStepResult"]
                    if not "id" in TestSteps:
                        for TestStep in TestSteps:
                            if "testAssertionResults" in TestStep:
                                _get_TestAssertion_result(TestStep["testAssertionResults"])
                    else: 
                        if "testAssertionResults" in TestSteps:
                            _get_TestAssertion_result(TestSteps)
                elif "TestCaseResult" in _TestResults:
                    TestCases = _TestResults["TestCaseResult"]["testStepResults"]["TestStepResult"]
                    if not "id" in TestCases:
                        for TestCase in TestCases:
                            _transform_TestStep_TestResult(TestCase)
                    else:
                        _transform_TestStep_TestResult(TestCases)
                        
def _get_TestAssertion_result(TestStep):
    TestAssertions = TestStep["TestAssertionResult"]
    if not "id" in TestAssertions:
        for TestAssertion in TestAssertions:
            _get_message_TestResult(TestAssertion)
    else:
        _get_message_TestResult(TestAssertions)

def _get_message_TestResult(TestAssertion):
    if TestAssertion["status"]=="FAILED":
        if not "ref" in TestAssertion["messages"]["message"]:
            for errorMessage_reference in TestAssertion["messages"]["message"]:
                _save_errorMessage_TestResult(TestAssertion, errorMessage_reference)
        else:
            _save_errorMessage_TestResult(TestAssertion,TestAssertion["messages"]["message"])


def _save_errorMessage_TestResult(TestAssertion, errorMessage_reference):
    if TestAssertion["status"] == "FAILED" and not ".manual." in errorMessage_reference["ref"] and not errorMessage_reference["ref"] == "TR.recordsWithErrors":
        error_reference = errorMessage_reference["ref"]
        error_definition = _errorDictionary[error_reference]
        if "argument" in errorMessage_reference["translationArguments"]:
            arguments = errorMessage_reference["translationArguments"]["argument"]
            if not "token" in arguments:
                for arg in arguments:
                    error_definition = _set_error_definition(error_definition, arg)
                    
            else: 
                error_definition = _set_error_definition(error_definition, arguments)
        
        if _AssertionDictionary[TestAssertion["resultedFrom"]["ref"]].find("gmlas.") == -1:
            error = "{0} : Test '{1}' failed with the following error: '{2}'\n".format(TestAssertion["startTimestamp"], _AssertionDictionary[TestAssertion["resultedFrom"]["ref"]], error_definition)
            _save_in_file(error)
            
        
def _set_error_definition(error_definition, argument):
    try:
        error = error_definition.replace("{"+str(argument["token"])+"}", str(argument["$"]))
    except KeyError as key_error:
            print("The key {0} has not a value. Please check it".format(key_error))
            error = error_definition
    finally:
        return error

def _remove_old_message_file():
    if os.path.exists(_fileName):
        os.remove(_fileName)

def _save_in_file(log_message):
    log_file=open(_fileName, "a+")
    log_file.write(log_message)
    log_file.close()


