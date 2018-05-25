import os
import sys
from types import FunctionType

from extension.screencast.vlc_recorder import VlcRecorder
from extension.testdata.testdata import get_global_testdata, TestData
from extension.parsers.parameter_parser import set_parameter_file
from extension.util.GlobalUtils import Singleton

from SeleniumQautorobot import CommonUtils

DefaultDirectory = ["pagemodel", "common_lib"]
MethodNameStrip = ["component_", "common_lib_"]
TestReportFolder = "test_reports"
WarningNoTestData = "QautoRobot: Not using TestData"
WarningMethodAlreadyBound = '\nQautoRobot: Attribute "{0}" already bound:\n{1} (bound)\n{2} (not bound)\n'
WarningDirectoryNotFound = "QautoRobot: Method directory could not be found: "
LibraryScope = 'TEST SUITE'
LibraryAttributeName = "QA"

class QautoRobot(CommonUtils):
    """
    Robot library for dynamically adding all qautorobot methods to robot runnable state or in robot project libraries
    """
    __metaclass__ = Singleton
    ROBOT_LIBRARY_SCOPE = LibraryScope

    def __init__(self, testdata=None, *shared_directory):
        """
        During initilization adds dynamically all library methods to library
        """
        super(CommonUtils, self).__init__()

        # Test data file to use in library
        self.test_data_file = testdata

        # Set directory's to add
        self.default_directory = DefaultDirectory
        self.shared_directory = [x for x in shared_directory]
        self.directory = self.default_directory + self.shared_directory

        # Set all dynamic imports
        self.dynamically_import_librarys()

    def dynamically_import_librarys(self):
        """
        Dynamically add all library methods to library
        """
        # Add class into module for using in project python libraries
        sys.modules[LibraryAttributeName] = self

        # Set test data methods to library if test data file set
        if self.test_data_file:
            set_parameter_file(self.test_data_file)
            self.set_testdata_methods()
        else:
            self.warning(WarningNoTestData)

        # Set directory methods into library
        for directory in self.directory:
            sys.path.append(directory)
            self.set_module_methods(directory)

    def set_testdata_methods(self):
        """
        Set testdata methods from global testdata to class

        :return: None
        """
        # Get global testdata for adding method into library
        testdata = get_global_testdata()

        method_names = (_name for _name in self.get_class_methods(TestData) if not _name.startswith("_"))
        for _method_name in method_names:
            # Get method
            _method = getattr(testdata, _method_name)
            # Set testdata method into library
            self.set_attribute_if_not_exists(self, _method_name, _method)

    def set_module_methods(self, dir):
        """
        Set all module methods from path to class

        :param dir: Path to directory
        :return: None
        """
        # Find all library files from the directory
        # If folder does not exist abort setting modules
        try:
            library_files = [_file for _file in os.listdir(dir) if _file.endswith(".py") and not _file.startswith("__")]
        except OSError as e:
            self.warning(WarningDirectoryNotFound + str(e))
            return

        for library in library_files:
            library = os.path.basename(library).replace(".py", "")
            _import = "{}.{}".format(os.path.basename(dir), library)

            # Import keyword module
            _module = __import__(_import, fromlist=[''])
            # Get keyword library from module
            _class = getattr(_module, library.capitalize())
            method_names = (_name for _name in self.get_class_methods(_class) if not _name.startswith("_"))
            for _method_name in method_names:
                # Get method
                _method = getattr(_class(), _method_name)
                # Generate method name that allows methods with same name to exists in project
                _library_method_name = library
                # Strip parts for library name
                for x in MethodNameStrip:
                    _library_method_name = _library_method_name.replace(x, "")
                _library_method_name = _library_method_name + "_" + _method_name
                # Set method with library name + method name
                self.set_attribute_if_not_exists(self, _library_method_name, _method)
                # Set method with library name + . + method name
                self.set_attribute_if_not_exists(self, library + "." + _method_name, _method)
                # Set method with method name
                self.set_attribute_if_not_exists(self, _method_name, _method)

    def set_attribute_if_not_exists(self, _class, _name, _attr):
        """
        Checks that attribute does not exist. If id does not add it to class

        :param _class: Class to add attribute into
        :param _name: Name for given attribute
        :param _attr: Attribute to add
        :return: None
        """
        try:
            attr = getattr(_class, _name)
            # TODO decide how to implement this (might need way to disable)
            # self.warning(WarningMethodAlreadyBound.format(_name, attr, _attr))
        except AttributeError:
            setattr(_class, _name, _attr)

    @staticmethod
    def get_class_methods(_class):
        """
        Get all class methods

        :param _class: Class to add attribute into
        :return: List of class methods
        """
        return [x for x, y in _class.__dict__.items() if type(y) == FunctionType]

    @staticmethod
    def get_failure_image_path(test_case):
        """
        Get image path to failure image

        :param test_case: Test case name
        :return: image_path
        """
        image_path = os.path.join(os.getcwd(), TestReportFolder, test_case.replace(" ", "_") + ".png")
        return image_path

    @staticmethod
    def generate_failure_documentation(documentation, test_case):
        """
        Get image path to failure image

        :param documentation: Documentation string
        :param test_case: Test case name
        :return: image_path
        """
        test_case = test_case.replace(" ", "_")
        documentation = "{}\n\nRecording: [{}.ogg|recording]\n\n[{}.png|image]".format(documentation,
                                                                                       test_case, test_case)
        return documentation

    def start_recording(self, test_case):
        """
        Start screencast recording

        :return: None
        """
        record_path = os.path.join(os.getcwd(), TestReportFolder, test_case.replace(" ", "_") + ".ogg")
        self.recorder = VlcRecorder(record_path)
        self.recorder.start()

    def stop_recording(self):
        """
        Stop screencast recording

        :return: Path to recording file
        """
        self.recorder.stop()
        return self.recorder.get_file()

    @staticmethod
    def get_testdata():
        """
        Get global test data object

        :return: Global testdata object
        """
        return get_global_testdata()
