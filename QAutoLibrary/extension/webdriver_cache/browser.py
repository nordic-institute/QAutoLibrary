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
import shutil
from lxml import etree as ET
from urlparse import urlparse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from QAutoLibrary.extension.util.GlobalUtils import GlobalUtils, throw_error
from QAutoLibrary.extension.config import get_config_value


class Browsers:
    IE = 0
    FIREFOX = 1
    CHROME = 2
    OPERA = 3
    ANDROID_CHROME = 4
    ANDROID_APPLICATION = 5
    EDGE = 6
    SAFARI = 7


def get_country_key(my_lang):
    """
    Country keys

    :param my_lang: my_lang language name as String
    :return: country_key
    """
    if my_lang == "Finnish":
        country_key = "fi-FI,en-US"
    elif my_lang == "English":
        country_key = "en-US,fi-FI"
    elif my_lang == "French":
        country_key = "fr-FR,en-US"
    else:
        country_key = "en-US,fi-FI"

    return country_key


if not os.path.exists(GlobalUtils.TOOL_CACHE):
    os.makedirs(GlobalUtils.TOOL_CACHE)
_geckodriver_log_path = os.path.join(os.getcwd(), GlobalUtils.GECKODRIVER_LOG)

# default values are hardcoded
_protected_values = [3, 3, 0, 0]
_use_ff_proxy = False

__REMOTE_SERVER_ADDRESS = None
_REMOTE_SERVER_CAPTIONS = None


def _get_browser_options_from_project_xml(suit, browser_name, function, if_cases=[]):
    config_file = os.path.join(os.getcwd(), GlobalUtils.BROWSER_CONFIG_FILE)
    if not os.path.isfile(config_file):
        shutil.copyfile(GlobalUtils.BROWSER_CONFIG_FILE_FRAMEWORK, config_file)
    tree = ET.parse(config_file)
    root = tree.getroot()

    options = []

    defaults = root.find(suit)

    browsers = [browser for browser in defaults if browser.attrib["name"] == browser_name]

    for browser in browsers:
        for option in browser.findall(function):
            info = {"text": option.text}
            try:
                info["option"] = option.attrib["option"]
            except:
                pass
            try:
                # options that have if_case have to be in the given if cases (otherwise continue to skip appending
                if option.attrib["if_case"] not in if_cases:
                    continue
            except:
                pass
            options.append(info)
    return options


## Return WebDriver object.
# Create correct WebDriver object by name.
# In this function profiles and options can be specified for each browser.
# @return: WebDriver object
def create_driver(browser_name):
    if browser_name not in GlobalUtils.BROWSER_NAMES:
        raise Exception("Unsupported browser string: '%s' Use: %s" % (browser_name, GlobalUtils.BROWSER_NAMES))

    if __REMOTE_SERVER_ADDRESS:
        if _REMOTE_SERVER_CAPTIONS:
            desired_capabilities = _REMOTE_SERVER_CAPTIONS
        else:
            desired_capabilities = __get_desired_capabilities(browser_name)
        print __REMOTE_SERVER_ADDRESS
        print desired_capabilities

        _driver = webdriver.Remote(__REMOTE_SERVER_ADDRESS, desired_capabilities)
        return _driver

    if browser_name == GlobalUtils.BROWSER_NAMES[Browsers.IE]:
        # Read browser language from config
        import _winreg
        try:
            my_lang = get_config_value("browser_language")
            country_key = get_country_key(my_lang)
            try:

                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Internet Explorer\\International",
                                      0, _winreg.KEY_ALL_ACCESS)
                _winreg.SetValueEx(key, "AcceptLanguage", 0, _winreg.REG_SZ, str(country_key + ";q=0.5"))
                _winreg.CloseKey(key)
            except Exception, e:
                try:
                    _winreg.CloseKey(key)
                    throw_error("\nCould not set language value: " + str(e))
                except Exception, msg:
                    print str(msg)
        except:
            pass

        # Turn protected mode on for all zones
        try:
            for i in range(1, 5):
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                      "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\" + str(i),
                                      0, _winreg.KEY_ALL_ACCESS)
                try:
                    _protected_values[i - 1] = _winreg.QueryValueEx(key, "2500")[0]
                except WindowsError, e:
                    pass
                _winreg.SetValueEx(key, "2500", 0, _winreg.REG_DWORD, 0)
                _winreg.CloseKey(key)
        except Exception, e:
            try:
                _winreg.CloseKey(key)
                reset_protected_mode()
                throw_error("\nCould not change Internet Explorer zone settings: " + str(e))
            except Exception, msg:
                print str(msg)
                pass

        capabilities = _get_browser_options_from_project_xml("default",
                                                             _browser_full_names[GlobalUtils.BROWSER_NAMES[Browsers.IE]],
                                                             "capabilities")

        ie_capabilities = DesiredCapabilities.INTERNETEXPLORER
        for arg in capabilities:
            ie_capabilities[arg["option"]] = eval(arg["text"])

        # Adding driver to path
        if not GlobalUtils.is_linux():
            print "Using IEDriverServer"
            if not os.path.join(GlobalUtils.RESOURCES_IE_PATH) in os.environ["PATH"]:
                print "Adding IEDriverServer to path"
                os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_IE_PATH)
        else:
            raise Exception("Linux can't use IEDriverServer")

        _driver = webdriver.Ie(capabilities=ie_capabilities)
        return _driver
    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.CHROME]:
        options = webdriver.ChromeOptions()

        # enable chrome switches
        try:
            opt_values = get_config_value("browser_options")
            for opt_value in opt_values:
                options.add_argument("--" + opt_value)
        except:
            pass

        extension_if_cases = []
        argument_if_cases = []

        # enable cache cleaner for resource timings
        if get_config_value("enable_live_monitoring").lower() == 'true':
            extension_if_cases.append("enable_live_monitoring")
        # enable precise memory info
        if get_config_value("enable_precise_memory").lower() == 'true':
            argument_if_cases.append("enable_precise_memory")

        # Get add_argument options from xml
        add_arguments = _get_browser_options_from_project_xml("default",
                                                              GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.CHROME]],
                                                              "add_argument", argument_if_cases)
        # Get add_extensions options from xml
        add_extensions = _get_browser_options_from_project_xml("default",
                                                               GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.CHROME]],
                                                               "add_extension", extension_if_cases)
        # Get add_experimental_options options from xml
        add_experimental_options = _get_browser_options_from_project_xml("default",
                                                                         GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.CHROME]],
                                                                         "add_experimental_option")
        # add_argument using dict parsed from xml
        for arg in add_arguments:
            options.add_argument(eval(arg["text"]))
        # add_extension using dict parsed from xml
        for arg in add_extensions:
            options.add_extension(eval(arg["text"]))
        # add_experimental_option using dict parsed from xml
        for arg in add_experimental_options:
            try:
                # Selenium 2.26
                options.add_experimental_option(arg["option"], eval(arg["text"]))
            except:
                pass

        # Adding driver to path
        if not GlobalUtils.is_linux():
            print "Using 32bit win chromedriver"
            if not os.path.join(GlobalUtils.RESOURCES_CHROME32_PATH) in os.environ["PATH"]:
                print "Adding 32bit win chromedriver to path"
                os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_CHROME32_PATH)
        else:
            print "Using 64bit linux chromedriver"
            if not os.path.join(GlobalUtils.RESOURCES_LINUX_CHROME64_PATH) in os.environ["PATH"]:
                print "Adding 64bit linux chromedriver to path"
                os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_LINUX_CHROME64_PATH)

        _driver = webdriver.Chrome(chrome_options=options)
        return _driver
    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.FIREFOX]:
        profile = webdriver.FirefoxProfile()
        preference_if_cases = []

        set_preferences = _get_browser_options_from_project_xml("default",
                                                                GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.FIREFOX]],
                                                                "set_preference", preference_if_cases)
        for arg in set_preferences:
            profile.set_preference(arg["option"], eval(arg["text"]))

        set_capabilities = _get_browser_options_from_project_xml("default",
                                                                 GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.FIREFOX]],
                                                                "set_capabilities")

        firefox_capabilities = DesiredCapabilities.FIREFOX
        for arg in set_capabilities:
            firefox_capabilities[arg["option"]] = eval(arg["text"])

        # Adding driver to path
        if not GlobalUtils.is_linux():
            print "Using 32bit win geckodriver"
            # first we try to use 32bit wersion
            if not os.path.join(GlobalUtils.RESOURCES_GECKO32_PATH) in os.environ["PATH"]:
                print "Adding 32bit win geckodriver to path"
                os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_GECKO32_PATH)
        else:
            print "Using 64bit linux geckodriver"
            if not os.path.join(GlobalUtils.RESOURCES_LINUX_GECKO64_PATH) in os.environ["PATH"]:
                print "Adding 64bit linux geckodriver to path"
                os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_LINUX_GECKO64_PATH)
        try:
            _driver = webdriver.Firefox(firefox_profile=profile, capabilities=firefox_capabilities, log_path=_geckodriver_log_path)
        except WebDriverException as e:
            # try with 64bit version if we are using windows
            if not GlobalUtils.is_linux():
                print "Failed to use win 32bit geckodriver "
                print "Using win 64bit geckodriver"
                if os.path.join(GlobalUtils.RESOURCES_GECKO32_PATH) in os.environ["PATH"]:
                    print "Removing win 32bit geckodriver from path"
                    os.environ["PATH"] = os.environ["PATH"].replace(os.pathsep + os.path.join(GlobalUtils.RESOURCES_GECKO32_PATH), "")
                if not os.path.join(GlobalUtils.RESOURCES_GECKO64_PATH) in os.environ["PATH"]:
                    print "Adding win 64bit geckodriver to path"
                    os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_GECKO64_PATH)
                _driver = webdriver.Firefox(firefox_profile=profile, capabilities=firefox_capabilities)
            else:
                raise e
        return _driver
    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.OPERA]:
        desired_capabilities = {}
        des_caps = _get_browser_options_from_project_xml("default", GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.OPERA]],
                                                         "desired_capabilities")
        for arg in des_caps:
            desired_capabilities[arg["option"]] = eval(arg["text"])

        _driver = webdriver.Opera(desired_capabilities=desired_capabilities)
        return _driver

    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.ANDROID_CHROME]:
        desired_caps = {}
        des_caps = _get_browser_options_from_project_xml("default",
                                                         GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.ANDROID_CHROME]],
                                                         "desired_caps")
        for arg in des_caps:
            desired_caps[arg["option"]] = eval(arg["text"])

        _driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        return _driver

    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.ANDROID_APPLICATION]:
        desired_caps = {}
        des_caps = _get_browser_options_from_project_xml("default",
                                                         GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.ANDROID_APPLICATION]],
                                                         "desired_caps")
        for arg in des_caps:
            desired_caps[arg["option"]] = eval(arg["text"])

        _driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        return _driver

    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.EDGE]:
        capabilities = _get_browser_options_from_project_xml("default",
                                                             GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.EDGE]],
                                                             "capabilities")

        edge_capabilities = DesiredCapabilities.EDGE
        for arg in capabilities:
            edge_capabilities[arg["option"]] = eval(arg["text"])

        # Adding driver to path
        if not GlobalUtils.is_linux():
            print "Using MicrosoftWebDriver"
            if not os.path.join(GlobalUtils.RESOURCES_EDGE_PATH) in os.environ["PATH"]:
                print "Adding MicrosoftWebDriver to path"
                os.environ["PATH"] += os.pathsep + os.path.join(GlobalUtils.RESOURCES_EDGE_PATH)
        else:
            raise Exception("Linux can't use MicrosoftWebDriver")

        _driver = webdriver.Edge(capabilities=edge_capabilities)
        return _driver

    elif browser_name == GlobalUtils.BROWSER_NAMES[Browsers.SAFARI]:
        desired_capabilities = _get_browser_options_from_project_xml("default",
                                                                     GlobalUtils.BROWSER_FULL_NAMES[GlobalUtils.BROWSER_NAMES[Browsers.SAFARI]],
                                                                     "desired_capabilities")

        safari_capabilities = DesiredCapabilities.SAFARI
        for arg in desired_capabilities:
            safari_capabilities[arg["option"]] = eval(arg["text"])

        _driver = webdriver.Safari(desired_capabilities=safari_capabilities)
        return _driver

    else:
        return None


## Reverts changes done to protected mode settings when browser was IE
def reset_protected_mode():
    try:
        import _winreg
        for i in range(1, 5):
            if _protected_values[i - 1] is not None:
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                      "Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\Zones\\" + str(i),
                                      0, _winreg.KEY_ALL_ACCESS | _winreg.KEY_WOW64_32KEY)
                _winreg.SetValueEx(key, "2500", 0, _winreg.REG_DWORD, _protected_values[i - 1])
                _winreg.CloseKey(key)
    except Exception, e:
        try:
            _winreg.CloseKey(key)
            raise Exception("\nCould not change Internet Explorer zone settings back to original: " + str(e))
        except Exception, msg:
            print str(msg)
        pass


def set_ff_proxy(use_proxy=False):
    global _use_ff_proxy
    _use_ff_proxy = use_proxy


## Sets remote server address
# @param address: address to remote server as string
def set_remote_server_address(address):
    global __REMOTE_SERVER_ADDRESS

    result = urlparse(address)
    if result.scheme in ["http", "https"] and result.path == "/wd/hub":
        __REMOTE_SERVER_ADDRESS = address
    else:
        raise Exception("Remote server address is not correct '%s'" % address)


## Sets captions for the remote driver
def set_remote_server_caps(des_caps):
    global _REMOTE_SERVER_CAPTIONS
    _REMOTE_SERVER_CAPTIONS = des_caps


def get_remote_server_caps():
    return _REMOTE_SERVER_CAPTIONS


## Returns address to remote server as string
#@return: address to remote server as string
def get_remote_server_address():
    return __REMOTE_SERVER_ADDRESS


## Returns browser's capabilities as dictionary
# @param name: browser short name
# @return: browser's capabilities as dictionary
def __get_desired_capabilities(name):
    if name == GlobalUtils.BROWSER_NAMES[0]:
        return DesiredCapabilities.INTERNETEXPLORER
    elif name == GlobalUtils.BROWSER_NAMES[1]:
        return DesiredCapabilities.FIREFOX
    elif name == GlobalUtils.BROWSER_NAMES[2]:
        return DesiredCapabilities.CHROME
    elif name == GlobalUtils.BROWSER_NAMES[3]:
        return DesiredCapabilities.OPERA
    elif name == GlobalUtils.BROWSER_NAMES[6]:
        return DesiredCapabilities.EDGE
    elif name == GlobalUtils.BROWSER_NAMES[7]:
        return DesiredCapabilities.SAFARI
    else:
        raise Exception("Desired capabilities wasn't found for '%s'" % name)
