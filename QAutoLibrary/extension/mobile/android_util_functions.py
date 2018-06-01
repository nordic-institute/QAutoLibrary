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
import time
from subprocess import Popen, PIPE, STDOUT

from QAutoLibrary.extension.util.GlobalUtils import GlobalUtils
from QAutoLibrary.extension.config import get_config_value


# static class
class AndroidUtilFunctions(object):

    @classmethod
    def check_connection_to_android_device(cls):
        adb_ready_cmd = "adb shell echo ready"
        Popen("adb start-server", shell=True, stdout=PIPE, stderr=STDOUT)
        time.sleep(2)
        adb_ready_out = Popen(adb_ready_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        adb_ready_line = adb_ready_out.stdout.readline()
        adb_ready = re.sub('[^a-z]', '', adb_ready_line)
        if adb_ready != "ready":
            return False
        else:
            return True

    # @TODO: implement killing functionality also for Linux
    @classmethod
    def kill_appium_node(cls):
        if GlobalUtils.is_linux():
            Popen('killall /usr/bin/nodejs', shell=True, stdout=PIPE, stderr=STDOUT)
        else:
            Popen('taskkill /f /im node.exe', shell=True, stdout=PIPE, stderr=STDOUT)

        Popen('adb kill-server', shell=True, stdout=PIPE, stderr=STDOUT)
        time.sleep(1)

    @classmethod
    def kill_chromedriver(cls):
        if not GlobalUtils.is_linux():
            Popen('taskkill /f /im chromedriver.exe', shell=True, stdout=PIPE, stderr=STDOUT)
            time.sleep(1)

    @classmethod
    def start_appium_node(cls):
        Popen("adb start-server", shell=True, stdout=PIPE, stderr=STDOUT)
        time.sleep(2)

        if GlobalUtils.is_linux():
            appium_path = get_config_value("appium_path_linux")
            nodejs_path = get_config_value("nodejs_path_linux")

            Popen([nodejs_path, appium_path],
                  stdout=open('/dev/null', 'w'),
                  stderr=open('logfile.log', 'a'),
                  preexec_fn=os.setpgrp)  # @UndefinedVariable
        else:
            a_path = get_config_value("appium_path")
            njs_path = get_config_value("nodejs_path")
            if a_path:
                appium_path = a_path
            else:
                appium_path = GlobalUtils.APPIUM_PATH
            if njs_path:
                nodejs_path = njs_path
            else:
                nodejs_path = GlobalUtils.NODE_JS_PATH

            appium_cmd = nodejs_path + " " + appium_path + " -a 127.0.0.1 -q"
            Popen(appium_cmd, shell=False)
        time.sleep(3)

    @classmethod
    def check_device_ready(cls):
        adb_ready_cmd = "adb shell echo ready"
        adb_ready_out = Popen(adb_ready_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        adb_ready_line = adb_ready_out.stdout.readline()
        adb_ready = re.sub('[^a-z]', '', adb_ready_line)

        if adb_ready == "ready":
            return True
        else:
            return False

    @classmethod
    def close_node_adb_chrome(cls):
        try:
            cls.kill_appium_node()
            cls.kill_chromedriver()
        except:
            pass

    ## Opens android application specified by package./activity string
    @classmethod
    def open_android_activity(cls, package_activity):
        activity_to_open = "adb shell am start -n " + package_activity
        os.popen(activity_to_open, "r")

    ## Returns current application package./activity string
    # @return: current application package./activity string
    @classmethod
    def get_current_package_activity(cls):
        package_activity = ""
        try:
            activities_list = os.popen("adb shell dumpsys window windows", "r")
            activities_list_lines = activities_list.readlines()

            for line in activities_list_lines:
                #if "mFocusedApp" in line:
                if "mCurrentFocus" in line:
                    break

            words = line.split(" ")
            for item in words:
                if "/" in item:
                    break

            if "}" in item:
                package_activity = item[: item.find("}")]
            else:
                package_activity = item
        except:
            pass

        return package_activity

    @classmethod
    def get_current_android_resolution(cls):
        TITLE_STR = "Physical size:"
        resolution_p = os.popen("adb shell wm size", "r")
        resolution_str_lines = resolution_p.readlines()
        resolution_str = ""

        if len(resolution_str_lines):
            resolution_str = resolution_str_lines[0]
        else:
            return (0, 0)

        if TITLE_STR in resolution_str:
            resolution_str = resolution_str[resolution_str.find(TITLE_STR) + len(TITLE_STR):]
            resolution_str.strip()

            x_ind = resolution_str.find("x")

            if x_ind != -1:
                try:
                    return (int(resolution_str[:x_ind]), int(resolution_str[x_ind + 1:]))
                except:
                    return (0, 0)
            else:
                return (0, 0)
        else:
            return (0, 0)
