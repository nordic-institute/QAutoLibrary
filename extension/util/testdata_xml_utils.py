from lxml import etree as ET
from xml.dom import minidom

from FileOperations import save_content_to_file


class XmlTestDataFunctions():
    """
    Method container for editing and getting information from/to testdata xml file
    """
    TESTCASE = "Section"
    TESTSET = "TestData"
    PARAMETER = "parameter"
    EMPTY_STRING = ""
    TESTCASE_NAME = 'name'
    SECTION_NAME = 'name'
    PARAMETER_NAME = 'name'
    PARAMETER_VALUE = 'value'
    PARAMETER_PAGEMODEL = 'pagemodel'
    PARAMETER_VALIDATION = 'validation'
    PARAMETER_VERIFY = 'verify'
    PARAMETER_OPTIONAL = 'optional'
    QUOT_CHANGE = "&quot;"
    XML_TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<TestData>
    <Section name="$test_method_name">
        $parameters
    </Section>
</TestData>
"""


    @classmethod
    def generate_xml_file(cls, xml_file):
        test_set = ET.Element(cls.TESTSET)
        testcase = ET.SubElement(test_set, cls.TESTCASE)
        testcase.set(cls.TESTCASE_NAME, cls.EMPTY_STRING)
        xml_pretty = minidom.parseString(ET.tostring(test_set).replace("\n", "").strip()).toprettyxml(indent="   ")
        save_content_to_file(xml_pretty, xml_file)

    @classmethod
    def rename_pagemodel_in_test_data(cls, xml_file, pagemodel, page_model_new):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for section in root:
            for parameter in section:
                try:
                    parameter_pagemodel = parameter.attrib[cls.PARAMETER_PAGEMODEL]
                    if parameter_pagemodel == pagemodel:
                        parameter.set(cls.PARAMETER_PAGEMODEL, page_model_new)
                except Exception:
                    pass
        xml_pretty = cls.generate_xml_pretty_print(root)
        save_content_to_file(xml_pretty, xml_file)

    @classmethod
    def find_sections_using_parameters(cls, xml_file, parameters):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        sections = []
        for section in root:
            add_section = True
            for given_parameter in parameters:
                parameter_found = False
                for parameter in section:
                    if parameter.attrib[cls.PARAMETER_NAME] == given_parameter:
                        parameter_found = True
                if not parameter_found:
                    add_section = False
                    break
            if add_section:
                sections.append(section.attrib[cls.SECTION_NAME])
        return sections

    @classmethod
    def find_all_parameter_values_with_name(cls, xml_file, parameter_name):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        parameter_values = []
        for section in root:
            for parameter in section:
                try:
                    section_parameter_name = parameter.attrib[cls.PARAMETER_NAME]
                except:
                    continue
                if section_parameter_name == parameter_name:
                    parameter_values.append(parameter.attrib[cls.PARAMETER_VALUE])
        return parameter_values

    @classmethod
    def find_section_with_name(cls, xml_file, section_name):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for section in root:
            if section.attrib[cls.SECTION_NAME] == section_name:
                return section
        return None

    @classmethod
    def find_parameter_with_value(cls, xml_file, value):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        names = []
        for section in root:
            for param in section:
                if param.attrib[cls.PARAMETER_VALUE].strip() == value.strip():
                    names.append([section.attrib[cls.SECTION_NAME], param.attrib[cls.PARAMETER_NAME]])
        return names

    @classmethod
    def find_parameters_attrb_with_section_name(cls, xml_file, section_name):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        found_section = None
        for section in root:
            if section.attrib[cls.SECTION_NAME] == section_name:
                found_section = section
        if found_section is None:
            return None

        parameters_info = []
        for parameter in found_section:
            parameter_info = parameter.attrib
            parameters_info.append(parameter_info)
        return parameters_info

    @classmethod
    def find_param_with_name_in_xml_section(cls, xml_file, param_name, section_name):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        current_section = None

        for section in root:
            if section.attrib[cls.SECTION_NAME] == section_name:
                current_section = section

        if current_section is not None:
            for parameter in current_section:
                if parameter.attrib[cls.PARAMETER_NAME] == param_name:
                    return parameter
            return None
        else:
            return None

    @classmethod
    def get_root(cls, xml_file):
        tree = ET.parse(xml_file)
        return tree.getroot()

    @classmethod
    def edit_root_with_list_of_dicts(cls, section_name, params, root):
        current_section = None

        # Finds if given section already exists and adds it as current_section
        for section in root:
            if section.attrib[cls.SECTION_NAME] == section_name:
                current_section = section

        if current_section is not None:
            for param in params:
                for parameter in current_section:
                    if param[cls.PARAMETER_NAME] == parameter.attrib[cls.PARAMETER_NAME]:
                        current_section.remove(parameter)
                parameter = ET.SubElement(current_section, cls.PARAMETER)
                parameter.set(cls.PARAMETER_PAGEMODEL, param[cls.PARAMETER_PAGEMODEL])
                parameter.set(cls.PARAMETER_NAME, param[cls.PARAMETER_NAME])
                parameter.set(cls.PARAMETER_VALUE, param[cls.PARAMETER_VALUE])
                parameter.set(cls.PARAMETER_VALIDATION, param[cls.PARAMETER_VALIDATION])
                parameter.set(cls.PARAMETER_VERIFY, param[cls.PARAMETER_VERIFY])
        else:
            new_section = ET.SubElement(root, cls.TESTCASE)
            new_section.set(cls.SECTION_NAME, section_name)
            for param in params:
                parameter = ET.SubElement(new_section, cls.PARAMETER)
                parameter.set(cls.PARAMETER_PAGEMODEL, param[cls.PARAMETER_PAGEMODEL])
                parameter.set(cls.PARAMETER_NAME, param[cls.PARAMETER_NAME])
                parameter.set(cls.PARAMETER_VALUE, param[cls.PARAMETER_VALUE])
                parameter.set(cls.PARAMETER_VALIDATION, param[cls.PARAMETER_VALIDATION])
                parameter.set(cls.PARAMETER_VERIFY, param[cls.PARAMETER_VERIFY])

    @classmethod
    def edit_xml_file(cls, xml_file, section_name, param_name, param_value, pagemodel, validation=None, verify=None):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        current_section = None

        # Finds if given section already exists and adds it as current_section
        for section in root:
            if section.attrib[cls.SECTION_NAME] == section_name:
                current_section = section

        # If section exists edit values
        # Else generates section to xml
        if current_section is not None:
            parameter_found = False
            for parameter in current_section:
                if parameter.attrib[cls.PARAMETER_NAME] == param_name:
                    parameter.set(cls.PARAMETER_NAME, param_name)
                    parameter.set(cls.PARAMETER_VALUE, param_value)
                    parameter.set(cls.PARAMETER_PAGEMODEL, pagemodel)
                    if validation is not None:
                        parameter.set(cls.PARAMETER_VALIDATION, validation)
                    if verify is not None:
                        parameter.set(cls.PARAMETER_VERIFY, verify)
                    parameter_found = True
            if not parameter_found:
                parameter = ET.SubElement(current_section, cls.PARAMETER)
                parameter.set(cls.PARAMETER_PAGEMODEL, pagemodel)
                parameter.set(cls.PARAMETER_NAME, param_name)
                parameter.set(cls.PARAMETER_VALUE, param_value)
                if validation is not None:
                    parameter.set(cls.PARAMETER_VALIDATION, validation)
                if verify is not None:
                    parameter.set(cls.PARAMETER_VERIFY, verify)
        else:
            new_section = ET.SubElement(root, cls.TESTCASE)
            new_section.set(cls.SECTION_NAME, section_name)
            parameter = ET.SubElement(new_section, cls.PARAMETER)
            parameter.set(cls.PARAMETER_PAGEMODEL, pagemodel)
            parameter.set(cls.PARAMETER_NAME, param_name)
            parameter.set(cls.PARAMETER_VALUE, param_value)
            if validation is not None:
                parameter.set(cls.PARAMETER_VALIDATION, validation)
            if verify is not None:
                parameter.set(cls.PARAMETER_VERIFY, verify)
        xml_pretty = cls.generate_xml_pretty_print(root)
        save_content_to_file(xml_pretty, xml_file)

    @classmethod
    def generate_xml_pretty_print(cls, root):
        xml_string = ET.tostring(root).replace("\n", "").replace("\t", "").replace("    ", "").strip()
        xml_pretty = minidom.parseString(xml_string).toprettyxml(encoding='utf-8').decode('utf-8')
        return xml_pretty