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
from extension.util.common_methods_helpers import DebugLog
from extension.util.GlobalUtils import GlobalUtils, Singleton
from extension.webdriver_cache.browser import reset_protected_mode, Browsers


class DriverIdAlias(object):
    # Here is class variables that we should store from created driver
    id = None
    alias = None
    driver = None
    browser = None


class DriverCache(object):

    # make class as singleton
    __metaclass__ = Singleton

    def __init__(self):
        # current DriverIdAlias
        self.current_driver_id_alias = None
        # max created drivers
        self.max_ids = 0
        # active driver id's
        self.open_ids = []
        # closed driver id's
        self.closed_ids = []
        # DriverIdAlias stored with ids
        self.drivers_by_id = {}
        # DriverIdAlias stored with alias
        self.drivers_by_alias = {}

    # store new driver and return its id
    def register(self, driver, browser=None, alias=None):

        self.current_driver_id_alias = DriverIdAlias()
        self.current_driver_id_alias.driver = driver
        self.current_driver_id_alias.browser = browser
        self.current_driver_id_alias.alias = alias

        # is there closed ids
        if not self.closed_ids:
            # create new id
            self.max_ids += 1
            self.current_driver_id_alias.id = str(self.max_ids)
        else:
            # reuse closed ids
            self.current_driver_id_alias.id = self.closed_ids.pop()

        # store new driver, first store id to open id's
        self.open_ids.append(self.current_driver_id_alias.id)
        # DriverIdAlias by id
        self.drivers_by_id.update({self.current_driver_id_alias.id: self.current_driver_id_alias})
        # store by alias if we have it
        if alias:
            # DriverIdAlias by alias
            self.drivers_by_alias.update({self.current_driver_id_alias.alias: self.current_driver_id_alias})

        # return id
        return self.current_driver_id_alias.id

    def reset(self):
        self.current_driver_id_alias = None
        self.max_ids = 0
        del self.open_ids[:]
        del self.closed_ids[:]
        self.drivers_by_id.clear()
        self.drivers_by_alias.clear()

    # return current used driver
    def _get_current_driver(self):

        if self.current_driver_id_alias:
            return self.current_driver_id_alias.driver

        raise DriverNotFoundException("WebDriver not found! Maybe all applications are closed?")

    def _is_current_driver(self):
        return self.current_driver_id_alias and True or False

    # returns current used alias if exist, otherwise returns id
    def get_current_id_or_alias(self):

        if self.current_driver_id_alias:
            if self.current_driver_id_alias.alias:
                return self.current_driver_id_alias.alias
            else:
                return self.current_driver_id_alias.id

        raise DriverNotFoundException("WebDriver not found! Maybe all applications are closed?")

    # returns current used browser
    def _get_current_browser(self):

        if self.current_driver_id_alias:
            return self.current_driver_id_alias.browser

        raise DriverNotFoundException("WebDriver not found! Maybe all applications are closed?")

    # check that is there any drivers in the cache
    # returns True or False
    def is_drivers_in_cache(self):
        return self.current_driver_id_alias is not None

    # closes current driver and sets last opened driver as current driver
    def close(self):

        if self.current_driver_id_alias:
            if self.current_driver_id_alias.browser == GlobalUtils.IE:
                reset_protected_mode()
            # close current driver and remove stored drivers
            self.current_driver_id_alias.driver.quit()
            # remove ids
            del self.drivers_by_id[self.current_driver_id_alias.id]
            self.open_ids.remove(self.current_driver_id_alias.id)
            # add id to closed ids
            self.closed_ids.append(self.current_driver_id_alias.id)
            # remove by alias if exist
            if self.current_driver_id_alias.alias:
                del self.drivers_by_alias[self.current_driver_id_alias.alias]

            # set last opened driver as current, if there is any
            if self.open_ids:
                self.current_driver_id_alias = self.drivers_by_id.get(self.open_ids[-1])
            else:
                self.reset()
        else:
            print "There is not any application to close!!"

    # closes all drivers
    def close_all(self):

        for current_driver in self.drivers_by_id.values():
            id_or_alias = current_driver.alias and current_driver.alias or current_driver.id
            DebugLog.log("* Closing browser '%s' with id or alias '%s'" % (current_driver.browser, id_or_alias))
            if current_driver.browser == GlobalUtils.IE:
                reset_protected_mode()
            current_driver.driver.quit()

        self.reset()

    def close_all_except_current(self):
        for driver in self.drivers_by_id.values():
            # id_or_alias = driver.alias and driver.alias or driver.id
            if not driver.id == self.current_driver_id_alias.id:
                # DebugLog.log("* Closing browser '%s' with id or alias '%s'" % (driver.browser, id_or_alias))
                if driver.browser == GlobalUtils.IE:
                    reset_protected_mode()
                driver.driver.quit()
                # remove ids
                del self.drivers_by_id[driver.id]
                self.open_ids.remove(driver.id)
                # add id to closed ids
                self.closed_ids.append(driver.id)
                # remove by alias if exist
                if driver.alias:
                    del self.drivers_by_alias[driver.alias]

    # switch driver by id or alias
    def switch_driver(self, id_or_alias):
        if id_or_alias in self.drivers_by_alias:
            self.current_driver_id_alias = self.drivers_by_alias[id_or_alias]
            # add id "top of the list"
            self.open_ids.remove(self.current_driver_id_alias.id)
            self.open_ids.append(self.current_driver_id_alias.id)
            return
        id_or_alias = str(id_or_alias)
        if id_or_alias in self.drivers_by_id:
            self.current_driver_id_alias = self.drivers_by_id[id_or_alias]
            # add id "top of the list"
            self.open_ids.remove(self.current_driver_id_alias.id)
            self.open_ids.append(self.current_driver_id_alias.id)
            return

        # Id or alias not found
        raise DriverIdOrAliasNotFoundException("Id or alias not found for driver: '%s'" % id_or_alias)

    # returns all drivers as a list
    def get_all_drivers(self):
        return self.drivers_by_id.values()

    # Returns True is browser is Internet Explorer, else - False.
    def _is_ie(self):
        return self._get_current_browser() == GlobalUtils.BROWSER_NAMES[Browsers.IE]

    # Returns True is browser is Firefox, else - False.
    def _is_ff(self):
        return self._get_current_browser() == GlobalUtils.BROWSER_NAMES[Browsers.FIREFOX]

    # Returns True is browser is Google Chrome, else - False.
    def _is_gc(self):
        return self._get_current_browser() == GlobalUtils.BROWSER_NAMES[Browsers.CHROME]

    ## Returns True is browser is Opera, else - False.
    def _is_op(self):
        return self._get_current_browser() == GlobalUtils.BROWSER_NAMES[Browsers.OPERA]

    # Returns True is browser is Android Chrome, else - False.
    def _is_ac(self):
        return self._get_current_browser() == GlobalUtils.BROWSER_NAMES[Browsers.ANDROID_CHROME]

    # Returns True is browser is Android Application, else - False.
    def _is_aa(self):
       return self._get_current_browser() == GlobalUtils.BROWSER_NAMES[Browsers.ANDROID_APPLICATION]


class DriverNotFoundException(Exception):
    pass


class DriverIdOrAliasNotFoundException(Exception):
    pass
