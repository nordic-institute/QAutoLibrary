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
import codecs
import os
import re
import shutil

# Default encoding
_DEFAULT_ENCODING = 'utf-8'

# Supported file modes:
READING_MODE = 'rb'
WRITING_MODE = 'wb'
APPENDING_MODE = 'ab'


def __open(path_to_file, mode):
    """
     Returns opened file object
     Contains information about file encoding

    :param path_to_file: path to file
    :param mode: opening mode
    :return: file object
    """
    return codecs.open(path_to_file, mode, _DEFAULT_ENCODING)


def open_file(path_to_file, mode=READING_MODE):
    """
    Returns opened file object

    :param path_to_file: path to file
    :param mode: opening mode
    :return: file object
    """
    return __open(path_to_file, mode)


def get_file_content(path_to_file):
    """
    Returns file content

    :param path_to_file: path to file
    :return: content of file as string
    """
    with __open(path_to_file, READING_MODE) as file_:
        return file_.read()


def get_file_lines(path_to_file):
    """
    Returns file lines

    :param path_to_file: path to file
    :return: lines of file as list
    """
    with __open(path_to_file, READING_MODE) as file_:
        return file_.readlines()


def get_file_lines_without_newlines(path_to_file):
    """
    Returns file lines without newline at the end

    :param path_to_file: path to file
    :return: lines of file without newlines as list
    """
    return get_file_content(path_to_file).splitlines()


def save_content_to_file(content, path_to_file):
    """
    Saves content to file

    :param content: content to write
    :param path_to_file: path to file
    :return: None
    """
    with __open(path_to_file, WRITING_MODE) as file_:
        file_.write(content)


def append_content_to_file(content, path_to_file):
    """
    Adds content to the end of file

    :param content: content to write
    :param path_to_file: path to file
    :return: None
    """
    with __open(path_to_file, APPENDING_MODE) as file_:
        file_.write(content)


def get_xml_files_dict(path_to_dir):
    """
    Get all python files in folder

    :param path_to_dir: path to dir
    :return: directory of directorys containing xml files
    """
    files = {}
    for root, dirnames, filenames in os.walk(path_to_dir):
        for filename in filenames:
            dir_name = os.path.basename(os.path.normpath(root))
            if filename.endswith(".xml") and dir_name not in files:
                files[dir_name] = [os.path.join(root, filename)]
            elif filename.endswith("xml"):
                files[dir_name].append(os.path.join(root, filename))
    return files


def get_python_files_dict(path_to_dir):
    """
    Get all python files in folder

    :param path_to_dir: path to dir
    :return: directory of directorys containing python files
    """
    files = {}
    for root, dirnames, filenames in os.walk(path_to_dir):
        for filename in filenames:
            dir_name = os.path.basename(os.path.normpath(root))
            if filename == "__init__.py":
                continue
            if filename.endswith(".py") and dir_name not in files:
                files[dir_name] = [os.path.join(root, filename)]
            elif filename.endswith(".py"):
                files[dir_name].append(os.path.join(root, filename))
    return files


# @TODO: all global functions in this file should be moved to this class
class FileUtils(object):
    # returns index in the string of the first method in the codestring or -1
    @classmethod
    def first_method_index(self, codestring):

        prefix = "    def "
        first_m_index = codestring.find(prefix)

        return first_m_index

    # returns True if file exists and name is case sensitive
    # otherwise returns False
    @classmethod
    def isfile_case_sensitive(self, path):
        if not os.path.isfile(path):
            return False
        directory, filename = os.path.split(path)
        return filename in os.listdir(directory)

    # returns String where tabs are changed to spaces
    @classmethod
    def change_taps_to_spaces(self, content):
        """


        :param content:
        :return:
        """
        return re.sub('\t', '    ', content)

    @classmethod
    def rename(self, old_name, new_name):
        """
        rename or move the file

        :param old_name:
        :param new_name:
        :return:
        """
        try:
            shutil.move(old_name, new_name)
            return True
        except Exception, e:
            print "File operation exception: ", str(e)
            return False


    @classmethod
    def get_method_index(self, method_name, codestring):
        """
        returns index in the string of the given method name in the codestring or -1

        :param method_name: Method name
        :param codestring:
        :return:
        """
        prefix = "    def %s(" % method_name
        method_index = codestring.find(prefix)
        return method_index

