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
import unittest
from datetime import datetime

from selenium.common.exceptions import StaleElementReferenceException, ElementNotVisibleException, \
    ElementNotSelectableException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait

from QAutoLibrary.extension.config import get_config_value


class CommonMethodsHelpers(object):
    ## Wait until function returns True
    # Executes passed function until it returns True
    # or time exceeds DEFAULT_TIMEOUT
    # @exception If time exceeds DEFAULT_TIMEOUT throws exception
    # @param function Function which should return True
    # @param msg      Exception message
    #
    # Example:
    # @code
    #   webdriver_wait(execute_js(js_script), msg="Function didn't return True or exeeded default timeout" , default_timeout)
    # @endcode
    @classmethod
    def webdriver_wait(cls, function, driver, msg='', timeout=None):
        if not timeout:
            timeout = get_config_value(("default_timeout"))
        TimeOutError = AssertionError
        try:
            WebDriverWait(driver, timeout, ignored_exceptions=[ElementNotVisibleException, StaleElementReferenceException,
                                                               ElementNotSelectableException]).until(function, msg)
        except TimeoutException, e:
            raise TimeOutError("%s %s" % (DebugLog.get_timestamp(), msg))
        except Exception, e:
            raise e

    ## Helper method to avoid unicode related issues
    # Converts all input strings to unicode if non-ascii characters are found in any
    @classmethod
    def contains_nonascii(self, *args):
        result = []
        found = False
        for i in args:
            try:
                if(isinstance(i, unicode)):
                    found = True
                    break
                if(isinstance(i, str)):
                    i.decode('ascii')
            except UnicodeDecodeError:
                found = True
                break

        if(found):
            for string in args:
                if(isinstance(string, str)):
                    result.append(unicode(string, "utf8"))
                else:
                    result.append(string)
            if(len(result) == 1):
                return result[0]
            return result
        else:
            if(len(args) == 1):
                return args[0]
            return args

    ## Assertion with printing
    # On fail prints out expected and actual values
    # @param expected Expected value
    # @param actual   Actual value
    # @param msg_pass Message to print if pass
    # @param msg_fail Message to print if fail
    #
    # Example (from example_tests/pagemodel/google/youtube.py):
    # @code
    #   assert_equal(2,execute_js("return document.getElementById('movie_player').getPlayerState();"),"> Video is now paused", "> Video is not paused")
    # @endcode
    @classmethod
    def assert_equal(cls, expected, actual, msgpass='', msg=''):
        expected, actual = CommonMethodsHelpers.contains_nonascii(expected, actual)
        info = "%s %s\nexpected: '%s', actual '%s'" % (DebugLog.get_timestamp(), msg, expected, actual)
        unittest.TestCase("assertEqual").assertEqual(expected, actual, info)
        try:
            if msgpass:
                DebugLog.log(msgpass)
        except:
            pass

    @classmethod
    def escape_xpath_text(csl, text):
        text = unicode(text)
        if '"' in text and '\'' in text:
            parts = text.split('\'')
            return "concat('%s')" % "', \"'\", '".join(parts)
        if '\'' in text:
            return "\"%s\"" % text
        return "'%s'" % text


class DebugLog(object):

    @staticmethod
    def get_timestamp():
        (tm, micro) = datetime.now().strftime('%H:%M:%S.%f').split('.')
        return "%s.%03d" % (tm, int(micro) / 1000)

    @staticmethod
    def log(msg):
        if msg.startswith("* "):
            msg = msg.lstrip("* ")
        print "* %s %s" % (DebugLog.get_timestamp(), msg)