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
import glob
import os

import extension


def set_global_testdata(testdata):
    """
    Sets global test data dictionary

    :param testdata: test data dict
    :return: None
    """
    extension.TESTDATA = testdata


def get_global_testdata():
    """
    Get global test data

    :return: global test data dictionary
    """
    return extension.TESTDATA


class TestData(dict):
    """
    Custom dictionary class for Test data
    """
    def __init__(self):
        dict.__init__(self)

    def get_section(self, section_name):
        """
        Method for getting section

        :param section_name: test data section name
        :return: section dictionary
        """
        try:
            return self.__getitem__(section_name)
        except KeyError:
            return None

    def get_parameter(self, section_name, parameter_name):
        """
        | Method for getting parameter from section.
        | If section_name is none find all parameters with parameter_name

        :param section_name: test data section name
        :param parameter_name: test data parameter name
        :return: parameter or filtered test data
        """
        if section_name is not None:
            try:
                return self.get_section(section_name).get_parameter(parameter_name)
            except KeyError:
                return None
        else:
            # Filter sections with out parameter
            sections_with_parameter = self.get_sections_with_parameter(parameter_name)
            # Return dict of all parameter name values
            return {key: sections_with_parameter[key][parameter_name] for key in sections_with_parameter}

    def get_sections_with_parameter(self, parameter_name):
        """
        Return section dicts with given parameter

        :param parameter_name: test data parameter name
        :return: Dict of section dicts
        """
        return {key: value for key, value in self.items() if parameter_name in self.get_section(key)}

    def create_section(self, section_name):
        """
        Create empty section into test data

        :param section_name: Test data section name
        :return: Testdata section
        """
        test_data_section = TestDataSection()
        self.__setitem__(section_name, test_data_section)
        return self.get_section(section_name)

    def create_parameter(self, section_name, parameter_name, parameter_value):
        """
        Create parameter into section with given value

        :param section_name: Test data section name
        :param parameter_name: Test data parameter name
        :param parameter_value: Test data parameter value
        :return: Parameter value
        """
        test_data_section = self.get_section(section_name)
        return test_data_section.create_parameter(parameter_name, parameter_value)

    def copy_section(self, section_to_copy, section_to_create):
        """
        Add copy of section into test data

        :param section_to_copy: Name of section to copy
        :param section_to_create:
        :return: Testdata section
        """
        test_data_section = self.get_section(section_to_copy)
        self.__setitem__(section_to_create, test_data_section)
        return self.get_section(section_to_create)

    def copy_parameter(self, section_to_copy_from, parameter_to_copy, section_to_copy_to, parameter_to_create):
        """
        Add copy of parameter to section

        :param section_to_copy_from:
        :param parameter_to_copy:
        :param section_to_copy_to:
        :param parameter_to_create:
        :return: None
        """
        test_data_to_copy_from = self.get_section(section_to_copy_from)
        parameter_to_copy = test_data_to_copy_from.get_parameter(parameter_to_copy)

        section_to_copy_to = self.get_section(section_to_copy_to)
        return section_to_copy_to.create_parameter(parameter_to_create, parameter_to_copy)

    def add_testdata_file(self, path, relative_path=True, is_folder=False):
        """
        Add test data files to test data

        :param path: Path to test data file
        :return: None
        """
        #TODO import gives error when not imported inside function
        from extension import ParameterParser
        if relative_path:
            path = os.path.join(os.getcwd(), path)

        if is_folder:
            paths = glob.glob(os.path.join(path, '*.xml'))
            print paths
        else:
            paths = [path]

        for path in paths:
            new_test_data = ParameterParser(path, add_common=False).get_all_parameters_dict()

            sections_to_create = [data for data in new_test_data if not data in self]
            for data in sections_to_create:
                self.__setitem__(data, new_test_data[data])

            sections_to_update = [data for data in new_test_data if data in self]
            for data in sections_to_update:
                self.get_section(data).update(new_test_data[data])


class TestDataSection(dict):
    """
    Custom dictionary class for Test data section
    """

    def get_parameter(self, parameter_name):
        """
        Gets test data parameter value

        :param parameter_name: Parameters name
        :return: Parameter value
        """
        try:
            return self.__getitem__(parameter_name)
        except KeyError:
            return None

    def create_parameter(self, parameter_name, parameter_value):
        """
        Create parameter to section with given value

        :param parameter_name: Test data parameter name
        :param parameter_value: Test data parameter value
        :return: Parameter value
        """
        self.__setitem__(parameter_name, parameter_value)
        return self.get_parameter(parameter_name)

    def copy_parameter(self, parameter_to_copy, parameter_to_create):
        """
        Add copy of parameter to section

        :param parameter_to_copy: Parameter to copy
        :param parameter_to_create: Parameter to create
        :return: Parameter value
        """
        parameter_value = self.get_parameter(parameter_to_copy)
        self.__setitem__(parameter_to_create, parameter_value)
        return self.get_parameter(parameter_to_create)
