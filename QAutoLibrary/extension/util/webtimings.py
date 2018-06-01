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
import time
import urllib2

from selenium.common.exceptions import WebDriverException

from QAutoLibrary.extension.util.common_methods_helpers import CommonMethodsHelpers
from QAutoLibrary.extension.util.GlobalUtils import GlobalUtils
from QAutoLibrary.extension.config import get_config_value
from QAutoLibrary.FileOperations import save_content_to_file, get_file_lines

__RESPONSE = None


def __get_timing_whole_process(driver):
    CommonMethodsHelpers.webdriver_wait(
        lambda driver: CommonMethodsHelpers.contains_nonascii(driver.execute_script("return document.readyState")) ==
        CommonMethodsHelpers.contains_nonascii("complete"), driver, "")

    total_time = driver.execute_script("var start = window.performance.timing.navigationStart; " +
                                       "var end = window.performance.timing.loadEventEnd; return end-start;")
    return int(total_time)


def __get_latency(driver):
    CommonMethodsHelpers.webdriver_wait(
        lambda driver: CommonMethodsHelpers.contains_nonascii(driver.execute_script("return document.readyState")) ==
        CommonMethodsHelpers.contains_nonascii("complete"), driver, "")
    latency = driver.execute_script("var start = window.performance.timing.fetchStart; var end = " +
                                    "window.performance.timing.responseEnd; return end-start;")
    return int(latency)


def __get_timing_page_load(driver):
    CommonMethodsHelpers.webdriver_wait(
        lambda driver: CommonMethodsHelpers.contains_nonascii(driver.execute_script("return document.readyState")) ==
        CommonMethodsHelpers.contains_nonascii("complete"), driver, "")
    load_time = driver.execute_script("var start = window.performance.timing.responseEnd; var end = " +
                                      "window.performance.timing.loadEventEnd; return end-start;")
    return int(load_time)


# Method can be used only on browsers that support navigation timing  API.
# Implemented on commonly used browsers starting from Chrome 6, Firefox 7, Internet Explorer 9
def get_measurements(label, driver, *args):
    time_stamp = long(time.time()) * 1000
    total_time = None
    latency = None
    load_time = None
    timings = []
    timings_tuple = []

    try:
        if(is_page_up(driver.current_url)):

            for attribute in args:
                if(str(attribute) == "total"):
                    total_time = __get_timing_whole_process(driver)
                    timings.append(total_time)
                    timings_tuple.append(("Total time", str(total_time)))
                if(str(attribute) == "latency"):
                    latency = __get_latency(driver)
                    timings.append(latency)
                    timings_tuple.append(("Latency", str(latency)))
                if(str(attribute) == "load"):
                    load_time = __get_timing_page_load(driver)
                    timings.append(load_time)
                    timings_tuple.append(("Load time", str(load_time)))

        else:
            for attribute in args:
                if(str(attribute) == "total"):
                    total_time = 0
                    timings.append(total_time)
                    timings_tuple.append(("Total time", "0"))
                if(str(attribute) == "latency"):
                    latency = 0
                    timings.append(latency)
                    timings_tuple.append(("Latency", "0"))
                if(str(attribute) == "load"):
                    load_time = 0
                    timings.append(load_time)
                    timings_tuple.append(("Load time", "0"))

        __generate_files(timings_tuple, total_time=total_time, load_time=load_time, latency=latency, ts=time_stamp, lb=str(label))
        if len(timings) == 1:
            return timings[0]
        return timings
    except WebDriverException:
        print "Javascript error occurred. Make sure your browser supports navigation timing API"


def is_page_up(url):
    global __RESPONSE
    try:
        # Return true if there was a response and it was between 200-299
        __RESPONSE = urllib2.urlopen(url)
        print "* Response code: " + str(__RESPONSE.code)
        print "* Response msg: " + str(__RESPONSE.msg)
        if(200 <= __RESPONSE.code < 300):
            return True
        else:
            return False
    # Return false if there was a response and it was not between 200-299
    except urllib2.HTTPError, e:
        class backup:
            code = e.code
            msg = e.msg

        __RESPONSE = backup()
        print "* Response code: " + str(__RESPONSE.code)
        print "* Response msg: " + str(__RESPONSE.msg)
        return False
    # Return false if there was no response at all
    except:
        class backup:
            code = 0
            msg = " URL does not exist"

        __RESPONSE = backup()
        print "* Response code: " + str(__RESPONSE.code)
        print "* Response msg: " + str(__RESPONSE.msg)
        return False


def __generate_files(timings, total_time, load_time, latency, ts, lb):
    header = ""
    data = ""

    for i in timings:
        header += i[0]
        data += i[1]
        if(i != timings[-1]):
            header += ", "
            data += ", "

    try:
        measurement_folder = os.path.join(get_config_value("reporting_folder"), GlobalUtils.MEASUREMENTS_FOLDER_NAME)
        if not os.path.exists(measurement_folder):
            os.mkdir(measurement_folder)
    except Exception, e:
        print "Could not create measurements folder:\n%s" % str(e)

    try:
        CSV_FILE = os.path.join(measurement_folder, GlobalUtils.NAVIGATION_DATA_PREFIX + str(lb) + ".csv")
        content = header + "\n" + data
        save_content_to_file(content, CSV_FILE)
    except Exception, e:
        print "Could not generate csv file:\n%s" % str(e)

    JTL_FILE = os.path.join(measurement_folder, GlobalUtils.NAVIGATION_DATA_PREFIX + str(lb) + ".jtl")
    JS_FILE = os.path.join(measurement_folder, GlobalUtils.NAVIGATION_DATA_PREFIX + str(lb) + ".js")

    # in jtl file we are using only load time or total time, default is load time
    if load_time:
        t = load_time
    elif total_time:
        t = total_time
    else:
        t = load_time

    # jtl file
    try:
        if(os.path.isfile(JTL_FILE)):
            read_lines = get_file_lines(JTL_FILE)
            str_to_insert = "<sample" + (' t=\'' + str(t) + '\'' if t is not None else '') + "" + \
                            (' lt=\'' + str(latency) + '\'' if latency is not None else '') + " ts='" + str(ts) + "' s='" \
                            + str('true' if 200 <= __RESPONSE.code < 300 else 'false') + "' lb='" + str(lb) + "' rc='" \
                            + str(__RESPONSE.code) + "' rm='" + str(__RESPONSE.msg) + "'/>\n"
            new_lines = read_lines[:-1] + [str_to_insert] + [read_lines[-1]]
            content = "".join(new_lines)
            save_content_to_file(content, JTL_FILE)
        else:
            heading = "<?xml version='1.0' encoding='UTF-8'?>\n<testResults version='1.2'>"
            lines = "\n<sample" + (' t=\'' + str(t) + '\'' if t is not None else '') + "" + \
                    (' lt=\'' + str(latency) + '\'' if latency is not None else '') + " ts='" + str(ts) + "' s='" \
                    + str('true' if 200 <= __RESPONSE.code < 300 else 'false') + "' lb='" + str(lb) + "' rc='" \
                    + str(__RESPONSE.code) + "' rm='" + str(__RESPONSE.msg) + "'/>"
            ending = "\n</testResults>"
            new_lines = heading + lines + ending
            content = "".join(new_lines)
            save_content_to_file(content, JTL_FILE)
    except Exception, e:
        print "Could not generate jtl file:\n%s" % str(e)

    # javascript file
    try:
        if(os.path.isfile(JS_FILE)):
            read_lines = get_file_lines(JS_FILE)
            str_to_insert = "{" + ("'load': '" + str(load_time) + "', " if load_time is not None else "") + \
                            ("'total': '" + str(total_time) + "', " if t is not None else "") + \
                            ("'latency': '" + str(latency) + "', " if latency is not None else "") + "'timestamp': '" \
                            + str(ts) + "', 'succes': " + str('true' if 200 <= __RESPONSE.code < 300 else 'false') \
                            + ", 'label': '" + str(lb) + "', 'response_code': '" + str(__RESPONSE.code) + "', 'response_msg': '" \
                            + str(__RESPONSE.msg) + "'},\n"
            new_lines = read_lines[:-1] + [str_to_insert] + [read_lines[-1]]
            content = "".join(new_lines)
            save_content_to_file(content, JS_FILE)
        else:
            heading = "var timings_js_data = ["
            lines = "\n{" + ("'load': '" + str(load_time) + "', " if load_time is not None else "") + \
                    ("'total': '" + str(total_time) + "', " if t is not None else "") + \
                    ("'latency': '" + str(latency) + "', " if latency is not None else "") + "'timestamp': '" \
                    + str(ts) + "', 'succes': " + str('true' if 200 <= __RESPONSE.code < 300 else 'false') \
                    + ", 'label': '" + str(lb) + "', 'response_code': '" + str(__RESPONSE.code) + "', 'response_msg': '" \
                    + str(__RESPONSE.msg) + "'},"
            ending = "\n];"
            new_lines = heading + lines + ending
            content = "".join(new_lines)
            save_content_to_file(content, JS_FILE)
    except Exception, e:
        print "Could not generate js file:\n%s" % str(e)
