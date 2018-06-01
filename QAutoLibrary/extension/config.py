"""
#    QAutomate Ltd 2018. All rights reserved.
#
#    Copyright and all other rights including without limitation all intellectual property rights and title in or pertaining to this material, 
#    all information contained herein, related documentation and their modifications and new versions and other amendments (QAutomate Material) vest in QAutomate Ltd or its licensors.
#    Any reproduction, transfer, distribution or storage or any other use or disclosure of QAutomate Material or part thereof without the express prior written consent
#    of QAutomate Ltd is strictly prohibited.
#
#    Distributed with QAutomate license.
#    All rights reserved, see LICENSE for details.
"""
import os
from ConfigParser import ConfigParser
from StringIO import StringIO

_DEFAULT_CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "framework_config.ini"))
_DEFAULT_SECTION = "default_config"
_config_file = None
_settings = {}


class SimpleConfigParser(ConfigParser):
    """
    Class is wrapper for ConfigParser
    It add section to string, so we can use ConfigParser without dealing with sections
    """
    def read(self, filename):
        try:
            text = open(filename).read()
        except IOError:
            raise Exception("Could not load config file: " + filename)
        else:
            file_content = StringIO("[" + _DEFAULT_SECTION + "]\n" + text)
            self.readfp(file_content, filename)


def _read_and_load_options():
    """
    Read file and add all settings to dict

    :return: None
    """
    parser = SimpleConfigParser()
    parser.read(_config_file)
    global _settings
    _settings = {}

    for item in parser.items(_DEFAULT_SECTION):
        _settings[item[0]] = item[1]


def _write_options(key, value):
    """
    Write option

    :param key: Option key
    :param value: Option value
    :return:
    """
    parser = SimpleConfigParser()
    parser.read(_config_file)
    parser.set(_DEFAULT_SECTION, key, value)
    with open(_DEFAULT_CONFIG_FILE, 'wb') as configfile:
        parser.write(configfile)


# TODO: add Android section support
def write_options(key, value):
    """
    Write option

    :param key: Option key
    :param value: Option value
    :return:
    """
    _write_options(key, value)


def set_config(config_file=None):
    """
    Set current config, from where all settings will be loaded

    :param config_file: path to config file
    :return: None
    """
    global _config_file

    if _config_file and config_file:
        if _config_file != config_file:
            _config_file = config_file
            _read_and_load_options()
        else:
            return
    elif not _config_file and config_file:
        _config_file = config_file
    elif _config_file and not config_file:
        if _config_file != _DEFAULT_CONFIG_FILE:
            _config_file = _DEFAULT_CONFIG_FILE
        else:
            return
    else:
        _config_file = _DEFAULT_CONFIG_FILE
    _read_and_load_options()


def get_config_value(key):
    """
    Read config value

    :param key: config variable name
    :return: None
    """
    if not _config_file:
        set_config()
    try:
        if key == "default_timeout":
            return int(_settings[key])
        else:
            return _settings[key]
    except Exception, e:
        raise Exception("Could not read config file: " + str(e))


def set_config_value(key, value):
    """
    Set new config value

    :param key: config variable name
    :param value: variable value
    :return: None
    """
    if not _config_file:
        set_config()
    try:
        _settings[key] = value
    except Exception, e:
        raise Exception("Could not set value to file: " + str(e))
