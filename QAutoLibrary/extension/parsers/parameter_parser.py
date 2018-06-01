"""
#    QAutomate Ltd 2018. All rights reserved.
#
#    Copyright and all other rights including without limitation all intellectual property rights and title in or
#    pertaining to this material, all information contained herein, related documentation and their modifications and
#    new versions and other amendments (QAutomate Material) vest in QAutomate Ltd or its licensor's.
#    Any reproduction, transfer, distribution or storage or any other use or disclosure of QAutomate Material or part
#    thereof without the express prior written consent of QAutomate Ltd is strictly prohibited.
#
#    Distributed with QAutomate license.
#    All rights reserved, see LICENSE for details.
"""
import os
import re
import xmltodict

from random import randint, choice
from xml.dom import minidom
from xml.sax.saxutils import escape

from QAutoLibrary.extension.util.GlobalUtils import GlobalUtils, throw_error
from QAutoLibrary.extension.util.testdata_xml_utils import XmlTestDataFunctions
from QAutoLibrary.extension.testdata import testdata

# This global variable used by get_parameter and get_parameter_dict. See 'ParameterParser' class
__PARAMETER_PARSER = None

# XML related constants
_TESTSET = XmlTestDataFunctions.TESTSET
_TESTCASE = XmlTestDataFunctions.TESTCASE
_PAGEMODEL_TAG = u'pagemodel'
_NAME_TAG = u'name'
_VALUE_TAG = u'value'
_VALIDATION_TAG = u'validation'
_VEIRFY_TAG = u'verify'

SECTION_GENERAL = 'general'
SECTION_TEARDOWN = 'teardown'
LOAD_TEST = False


## Returns parameters as dict
# @param path_to_parameters: path to parameters as String
# @return: old format parameter dict
def __initialize_parameters_to_dict(path_to_parameters):

    parameter_dict = {}
    # Open parameters file
    try:
        f = open(path_to_parameters, 'r')
    except Exception, e:
        raise("Could not open test data file: " + str(e))

    # Read parameters from xml to dict
    try:
        xmldoc = f.read()
        f.close()
        doc = xmltodict.parse(xmldoc)
    except Exception, e:
        throw_error("Could not parse test data file: " + str(e))

    # Read parameters to parameter dict
    try:
        rootkey = _TESTSET
        paramattr = "@name"
        paramval = "@value"
        table = []
        for keylevel1 in doc[rootkey].keys():
            # Find test_ and general keys from dict
            if keylevel1.startswith("test_") or keylevel1.startswith("gen") or keylevel1.startswith("teard"):
                # Save keys to table and check test_ and general parameters and save it parameter dict
                for keylevel2 in doc[rootkey][keylevel1].keys():
                    table = doc[rootkey][keylevel1][keylevel2]
                    table_length = 0
                    # only one parameter defined under the key
                    if isinstance(table, dict):
                        table_length = 1
                        parameter_dict[keylevel1, table[paramattr]] = str(table[paramval])
                    # multiple parameters defined under the key
                    elif type(table) is list:
                        table_length = len(table)
                        for k in range(0, table_length):
                            parameter_dict[keylevel1, table[k][paramattr]] = table[k][paramval]
                    else:
                        print 'Missing test data'
    except Exception, e:
        throw_error("Could not read values from dict: " + str(e))

    return parameter_dict


## Returns parameter value according to section, parameter name and pagemodel
# @param old_dict: old parameter dict
# @return: new parameter dict
def __convert_from_old_dict_to_new_dict(old_dict):
    new_dict = {}

    for k, v in old_dict.items():
        tc, name = k
        param = {_NAME_TAG: name, _VALUE_TAG: v}
        if new_dict.has_key(tc):
            new_dict[tc].append(param)
        else:
            new_dict[tc] = [param]

    return new_dict


def escape_xml_specific_chars(text):
    """
    | Returns escaped text
    | Replaces '>' to "&gt;"
    | Replaces '<' to "&lt;"
    | Replaces '&' to "&amp;"
    | Replaces '"' to "&quot;"
    | Replaces "'" to "&#39;"
    | Replaces "\n" to "&#xA;"
    | Replaces "\t" to "&#x9;"

    :param text: text to escape as string
    :return: escaped text
    """
    return escape(text, {u"'":u'&#39;', u'"':u'&quot;', u'\n':u'&#xA;', u'\t':u'&#x9;'})


def escape_xml_validation_chars(text):
    """
    | Replaces '>' to "&gt;"
    | Replaces '<' to "&lt;"
    | Replaces '&' to "&amp;"

    :param text: text to escape as string
    :return: escaped text
    """
    return escape(text)


def set_load_test(val):
    """
    Set global variable LOAD_TEST value

    :param val: True, if Load test case is ongoing; False: if Run test case is ongoing
    :return: None
    """
    global LOAD_TEST
    LOAD_TEST = val


def reset_load_test():
    """
    Reset global variable LOAD_TEST value

    :return: None
    """
    global LOAD_TEST
    LOAD_TEST = False


def get_parameter(section, name, catch_value_error=True):
    """
    | Returns parameter value according to section, parameter name and pagemodel
    | If parameter file wasn't set or value not found while catch_value_error is set True raises exception.

    :param section: test case name in xml file as string
    :param name: parameter name as string
    :param catch_value_error: parameter as True or False
    :return: parameter value according to section, parameter name and pagemodel or False
    """
    if __PARAMETER_PARSER:
        value = testdata.get_global_testdata().get_parameter(section, name)
        if value:
            return value
        elif catch_value_error:
            msg = "ERROR: Parameter value wasn't found with section='%s', name='%s'" % (section, name)
            raise Exception(msg)
        else:
            return False
    else:
        if LOAD_TEST == False:
            raise Exception("Test data file was not set")


def get_parameter_dict(section):
    """
    | Returns Parameters object according to section
    | If parameter file wasn't set raises exception.

    :param section: test case name in xml file as String
    :return: Parameters object according to section
    """
    if __PARAMETER_PARSER:
        return __PARAMETER_PARSER.get_parameters(section)
    else:
        if LOAD_TEST == False:
            raise Exception("Test data file was not set")


def get_all_parameters(param_file=None):
    """
    get global test data dictionary, if parameter file is not given use default

    :param param_file: path to parameter file
    :return: return global test data file
    """
    if __PARAMETER_PARSER and not param_file:
        parser = __PARAMETER_PARSER
    elif param_file:
        parameter_file = os.path.join(os.getcwd(), GlobalUtils.DATA_FOLDER_NAME, param_file)
        if not parameter_file.endswith(GlobalUtils.XML):
            parameter_file += GlobalUtils.XML
        param_parser = ParameterParser(parameter_file)
        parser = param_parser
    else:
        if LOAD_TEST is False:
            return {}
        else:
            return None

    return parser.get_all_parameters_dict()


def set_parameter_file(parameter_file):
    """
    Sets ParameterParser object to global variable

    :param parameter_file: path to parameter file
    :return: None
    """
    global __PARAMETER_PARSER
    try:
        __PARAMETER_PARSER = ParameterParser(parameter_file)
        testdata_dict = __PARAMETER_PARSER.get_all_parameters_dict()
        testdata.set_global_testdata(testdata_dict)
    except Exception, e:
        __PARAMETER_PARSER = None
        raise e


## Resets global variable to None
def reset_parameter_file():
    global __PARAMETER_PARSER
    __PARAMETER_PARSER = None


## Returns dictionary of parameters
# @param param_file: path to parameter file
# @return: dictionary of parameters
def parse_xml_to_dict(param_file):
    ext = os.path.splitext(param_file)[-1]
    is_xml = ext == ".xml"

    if is_xml:
        function = __initialize_parameters_to_dict
    else:
        throw_error("File is not supported: '%s'" % param_file)

    def get_unique_list(list1, list2):
        return list1 + [l for l in list2 if l not in list1]

    _dict = {}

    if is_xml:
        xml = minidom.parse(param_file)

        for testcase in xml.getElementsByTagName(XmlTestDataFunctions.TESTCASE):
            params = []

            for parameter in testcase.getElementsByTagName(XmlTestDataFunctions.PARAMETER):
                attributes = {}
                for name, value in parameter.attributes.items():
                    attributes[name] = value
                params.append(attributes)

            section = testcase.attributes[XmlTestDataFunctions.TESTCASE_NAME].value
            if section in _dict.keys():
                _dict[section] = get_unique_list(_dict[section], params)
            else:
                _dict[section] = params

    if len(_dict.items()) == 0:
        _dict = function(param_file)
        _dict = __convert_from_old_dict_to_new_dict(_dict)

    return _dict


## Instance of this class represents single parameter from parameter file
class _Parameter(object):
    ## Constructs object
    # @param pagemodel: pagemodel as string
    # @param name: name as string
    # @param value: value as string
    def __init__(self, pagemodel, name, value, validation, verify):
        self.pagemodel = pagemodel
        self.name = name
        self.value = value
        self.validation = validation
        self.verify = verify


## Instance of this class represents list of parameters
class Parameters(object):
    ## Constructs object
    # Passed parameters example:
    # [
    #  {u'name': u'username', u'value': u'teardown_login_username'},
    #  {u'name': u'password', u'value': u'teardown_login_password'}
    # ]
    # @param parameters: list of dictionary, each dictionary represents parameter
    def __init__(self, parameters):
        self.parameters = []
        for param in parameters:
            name = param[_NAME_TAG]
            value = param[_VALUE_TAG]
            if param.has_key(_VALIDATION_TAG):
                validation = param[_VALIDATION_TAG]
            else:
                validation = None
            if param.has_key(_VEIRFY_TAG):
                verify = param[_VEIRFY_TAG]
            else:
                verify = None
            if param.has_key(_PAGEMODEL_TAG):
                pm = param[_PAGEMODEL_TAG]
            else:
                pm = None
            self.parameters.append(_Parameter(pm, name, value, validation, verify))

    ## Returns parameter value or None
    # @param args: could be a tuple ('name', 'pagemodel') or string
    # @return: None or parameter value
    def __getitem__(self, args):
        if type(args) == tuple:
            name = args[0]
            pagemodel = args[1]
        else:
            name = args
            pagemodel = None

        if pagemodel:
            params = [param for param in self.parameters \
                      if param.name == name and \
                      (param.pagemodel and param.pagemodel == pagemodel)]
        else:
            params = [param for param in self.parameters if param.name == name]

        if len(params) > 0:
            return params[0].value
        else:
            return None


class ParameterParser(object):

    def __init__(self, path_to_parameter, add_common=True):
        self._parsed_dict = {}

        if add_common:
            common_xml_dir = os.path.join(os.getcwd(), GlobalUtils.COMMON_PARAMETERS_FOLDER_NAME)
            self._add_common_files(common_xml_dir)
            file_xml_dir = os.path.dirname(os.path.realpath(path_to_parameter))
            self._add_common_files(file_xml_dir)

        if not os.path.isfile(path_to_parameter):
            return
        self._add_xml_to_parsed_dict(path_to_parameter)

    def _add_xml_to_parsed_dict(self, xml_file):
        xml_dict = parse_xml_to_dict(xml_file)
        xml_dict = self.update_test_data_dict(self._parsed_dict, xml_dict)
        self._parsed_dict = xml_dict

    def _add_common_files(self, xml_dir):
        if not os.path.isdir(xml_dir):
            print "dir %s not found!" % xml_dir
            return
        xml_files = [file_name for file_name in os.listdir(xml_dir) if file_name.endswith(".xml")]
        xml_files = [file_name for file_name in xml_files if file_name.startswith("common_")]
        for file_name in xml_files:
            xml_file = os.path.join(xml_dir, file_name)
            self._add_xml_to_parsed_dict(xml_file)

    def update_test_data_dict(self, test_data_dict, new_test_data_dict):
        for section in new_test_data_dict:
            if section in test_data_dict:
                new_parameters = self.update_parameters_list(test_data_dict[section], new_test_data_dict[section])
                test_data_dict[section] = new_parameters
            else:
                test_data_dict[section] = new_test_data_dict[section]
        return test_data_dict

    def update_parameters_list(self, old_parameters, new_parameters):
        for parameter in new_parameters:
            for x, param in enumerate(old_parameters):
                if parameter[u'name'] == param[u'name']:
                    old_parameters[x].update(parameter)
            if parameter[u'name'] not in (param[u'name'] for param in old_parameters):
                old_parameters.append(parameter)
        return old_parameters

    ## Returns Parameters object or None
    # @param section: section as string
    # @return: Parameters object or None
    def get_parameters(self, section):
        params = []

        for __section in [SECTION_GENERAL, SECTION_TEARDOWN, section]:
            if self._parsed_dict.has_key(__section):
                params += self._parsed_dict[__section]

        if self._parsed_dict.has_key(section):
            return Parameters(params)
        else:
            return None

    def get_all_parameters_dict(self):
        """
        Returns dictionary which include all parameters from the parameter file

        :Example:
            | {u'general':{u'username': u'some_username', u'password': u'some_password'},
            | u'test_my_testcase': {u'param_name': u'param_value'}}

        :return: Test data dictionary
        """
        test_data = testdata.TestData()
        for section, section_params in self._parsed_dict.iteritems():
            section_params_table = testdata.TestDataSection()
            for section_param in section_params:
                section_params_table[section_param['name']] = self.check_parameter_value(section_param['value'])
                test_data[section] = section_params_table
        return test_data

    def get_parameter(self, section, name):
        """
        Get parameter from test data dict

        :param section: Section name
        :param name: parameter name
        :return: parameter value
        """
        return self.get_all_parameters_dict().get_parameter(section, name)

    def check_parameter_value(self, parameter):
        regexp = r"randomint\((.+)\)"
        found = re.findall(regexp, parameter)
        if found:
            try:
                values = [int(v.strip()) for v in found[0].split(",")]
                if values[0] < values[1]:
                    return randint(values[0], values[1])
                else:
                    return randint(values[1], values[0])
            except:
                print "Failed to parse random integer parameter"
                return parameter

        regexp = r"randomchoices\((.+)\)"
        found = re.findall(regexp, parameter)
        if found:
            try:
                values = [v.strip() for v in found[0].split(",")]
                return choice(values)
            except:
                print "Failed to parse random choices parameter"
                return parameter

        return parameter
