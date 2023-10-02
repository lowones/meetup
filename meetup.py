#!/Users/lowone/environments/scraper/bin/python
import lowlib
import datetime
import argparse
import base64
import imp
import logging
import os
import pdb
import re
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
#dashboard = imp.load_source('dashboard', '/Users/lowk/dev/selenium/meraki/dashboard/dashboard.py')

results_frame = 'SitesResultFrame'
search_frame = 'mysearch'
sites_frame = 'SitesFrame'
reports_frame = 'ReportsFrame'

class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

log_level = logging.INFO
log_level = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(log_level)
handler = logging.FileHandler(lowlib.get_script_name() + '.log')
handler.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def find(wait, selector, elementStr):
    try:
        wait.until(EC.element_to_be_clickable((selector, elementStr)))
    except Exception as err:
        print(err.message)
        print('Element failed to be found while waiting, or selector is invalid')
        raise err

def click(wait, selector, elementStr):
    try:
        wait.until(EC.element_to_be_clickable((selector, elementStr))).click()
    except Exception as err:
        print(err.message)
        print('Element failed to be clickable while waiting, or selector is invalid')
        raise err


def sendKeys(wait, selector, elementStr, keysToSend):
    try:
        wait.until(EC.element_to_be_clickable((selector, elementStr))).send_keys(keysToSend)
    except Exception as err:
        print(err.message)
        print('Element failed to be clickable in 10s, or selector is invalid')
        raise err


def waitForOverlay(driver):
    i = 0
    try:
        while True:
            driver.find_element_by_css_selector("#loadingOverlay")
            time.sleep(1)
            i = i + 1
            print("waiting - {} iterations ... ".format(i))
    except Exception as err:
        print("Done waiting - {} iterations ... ".format(i))


def main():
    print("logger: %s" % type(logger))
    self_terminate_filename = 'SELF_TERMINATE'
    try:
        os.remove('RESTART')
    except:
        pass
    logger.critical("START")

#    for attempt in range(2):
#    while True:
#        handle_event()
    handle_event()

def handle_event():
#    pdb.set_trace()
    fudge = False
    fudge = True
    mode = run_at(fudge)
    start_time = lowlib.get_timestamp()
    event_day, event_name = get_event(mode)
    event_day, event_name = fudge_run()
    if not event_name:
        return()
    t_month, target_year, target_month, target_day = get_month_date_next_day(event_day)
#    target_day = '9'

    driver = webdriver.Chrome()
    driver.implicitly_wait(1)
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 30)

    meetup = 'https://meetup.com/'
    driver.get(meetup)
    if login(driver, wait):
#        set_events_filter(driver, wait)
        turn_off_suggested_events(driver, wait)
        new_choose_month(driver, wait, target_month)
        new_choose_event_day(driver, wait, target_day)
        day_e = new_find_day_section(driver, wait, target_day, target_month, event_day)
        if new_select_event(driver, wait, day_e, event_name):
        #    rsvp = handle_rsvp(driver, wait, 3)
#            pdb.set_trace()
            rsvp = handle_rsvp(driver, wait, 90)
            print("RSVP: {}".format(rsvp))
    else:
        print("Need to send message!")

    driver.close()

    print("\n\nRSVP: {}".format(rsvp))
    end_time = lowlib.get_timestamp()
    print("START: {} END: {}".format(start_time, end_time))

def fudge_run():
    event_day = 'Tuesday'
    event_day = 'Monday'
    event_name = 'Monday Night Volleyball'
    event_name = 'Indoor Volleyball at Pittsfield'
    event_name = 'Pittsfield'
    return(event_day, event_name)

def new_select_event(driver, wait, day_e, event_name):
    status = False
    parent = day_e.find_element(By.XPATH, '..')
    for element in parent.find_elements(By.TAG_NAME, 'p'):
        if event_name in element.text:
            element.click()
            status = element
            break
    return(status)

def select_event(driver, wait, day_e, event_name):
    status = False
    try:
        day_e.find_element_by_link_text(event_name).click()
        status = True
    except:
        print("NOT_FOUND: {}".format(event_name))
    return(status)

def new_find_day_section(driver, wait, target_day, target_month, event_day):
    when = event_day + ', ' + target_month + ' ' + target_day
    target_xpath = "//*[contains(text(),'" + when + "')]"
    find(wait, By.XPATH, target_xpath)
    day_e=driver.find_element(By.XPATH, target_xpath)
#    test=driver.find_element(By.XPATH, "//*[text()='Monday, October 2, 2023']")
    return(day_e)

def find_day_section(driver, wait, target_year, t_month, target_day):
    day_format = target_year+'-'+str(t_month)+'-'+target_day
    day_class = 'event-listing-container-li.container-' + day_format
    find(wait, By.CLASS_NAME, day_class)
    day_e = driver.find_element_by_class_name(day_class)
    return(day_e)

def login(driver, wait):
    global m_username, m_password
    status = False
    username = m_username
    password = m_password
    # let page load
    find(wait, By.LINK_TEXT, 'Log in')
#    driver.find_element_by_link_text('Log in').click()
    driver.find_element(By.LINK_TEXT, 'Log in').click()
#    driver.find_element_by_id('email').send_keys(username)
    driver.find_element(By.ID, 'email').send_keys(username)
    driver.find_element(By.ID, 'current-password').send_keys(password)
#    driver.find_element(By.ID, 'loginFormSubmit').click()
    driver.find_element(By.NAME, 'submitButton').click()
    try:
#        logged_in = find(wait, By.ID, 'simple-event-filter')
        logged_in = find(wait, By.ID, 'desktop-profile-menu')
        status = True
    except:
        print("Login failed")
    return(status)

def turn_off_suggested_events(driver, wait):
    find(wait, By.ID, 'suggestedEventsTopFiltersToggle')
    toggle = driver.find_element(By.ID, 'suggestedEventsTopFiltersToggle')
    if toggle.is_selected():
        toggle.click()


def set_events_filter(driver, wait):
    find(wait, By.ID, 'simple-event-filter')
    filter_section = driver.find_element_by_id('simple-event-filter')
    for filter_e in filter_section.find_elements_by_tag_name('li'):
        if filter_e.text == 'Your groups only':
            filter_e.click()
            break

def choose_event_day(driver, wait, target_day):
    time.sleep(2)
    find(wait, By.LINK_TEXT, target_day)
    driver.find_element_by_link_text(target_day).click()

def new_choose_event_day(driver, wait, target_day):
    time.sleep(2)
    find(wait, By.CLASS_NAME, 'DayPicker-Day')
    days = driver.find_elements(By.CLASS_NAME, 'DayPicker-Day')
    for day in days:
        if day.text == target_day:
            day.click()
            break


def new_choose_month(driver, wait, target_month):
    find(wait, By.CLASS_NAME, 'DayPicker-Caption')
    month = driver.find_element(By.CLASS_NAME, 'DayPicker-Caption')
    while not month.text.startswith(target_month):
        next_month = driver.find_element(By.CLASS_NAME, 'DayPicker-NavButton.DayPicker-NavButton--next')    
        next_month.click()
        month = driver.find_element(By.CLASS_NAME, 'DayPicker-Caption')


def choose_month(driver, wait, target_month):
    while True:
        find(wait, By.CLASS_NAME, 'ui-datepicker-month')
        month = driver.find_element_by_class_name('ui-datepicker-month').text
        if month == target_month:
            break
        else:
            driver.find_element_by_class_name('ui-datepicker-next').click()

def handle_popup(driver, wait):
    when = "You're going to a Meetup event!"
    target_xpath = "//*[contains(text(),'" + when + "')]"
    find(wait, By.XPATH, target_xpath)
    day_e=driver.find_element(By.XPATH, target_xpath)

    target_xpath = "//*[contains(text(),'" + when + "')]"

def handle_rsvp(driver, wait, attempts):
    rsvp = ''
#    while True:
    for attempt in range(attempts):
        find(wait, By.TAG_NAME, 'button')
#        for button in driver.find_elements_by_tag_name('button'):
        for button in driver.find_elements(By.TAG_NAME, 'button'):
#            print(button.text)
            if button.text == 'Not open':
                print("wait and reload: {}".format(attempt))
                break
            elif button.text == 'Attend':
                button.click()
                rsvp = 'attend'
                break
            elif button.text == 'Join waitlist':
                button.click()
                rsvp = 'waitlist'
                break
            elif button.text == 'Edit RSVP':
                rsvp = 'already'
                break
        else:
            rsvp = 'nothing'
        if not rsvp:
            time.sleep(1)
            driver.refresh()
        else:
            break

    pdb.set_trace()
    return(rsvp)

def get_event(mode):
    event_day = ''
    event_name = ''
    today = datetime.date.today().strftime("%A")
    hour = int(lowlib.get_timestamp().split('-')[-1].split(':')[0])
    if mode == 'fudge':
        event_day = today
        event_day = 'Monday'
        event_name = 'fudge'
        event_name = 'Monday Night Volleyball'
    elif today == 'Saturday':
        event_day = 'Tuesday'
        event_name = 'Indoor Volleyball at Pittsfield'
    elif today == 'Monday':
        if hour > 18:
            event_day = 'Thursday'
            event_name = 'Indoor Volleyball at Pittsfield'
        else:
            event_day = 'Monday'
            event_name = 'Monday Night Volleyball'
    else:
        print("Unkown event to target")
    return(event_day, event_name)

def next_weekday(weekday_name):
    next_date = ''
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    try:
        weekday = days.index(weekday_name)
    except:
        return(next_date)
    d = datetime.date.today()
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    next_date =  d + datetime.timedelta(days_ahead)
    return(next_date)

def get_month_date_next_day(day):
    next_day = ''
    next_month = ''
    next_year = ''
    month = ''
    next_date = next_weekday(day)
    if next_date:
#        next_day = next_date.strftime("%d")
        next_day = next_date.strftime("%-d")
        next_month = next_date.strftime("%B")
        next_year = next_date.strftime("%Y")
        month = next_date.month
#        print(next_day, next_month)
#        print(next_month, next_day)
    return(month, next_year, next_month, next_day)

def run_at(fudge=False):
    status = ''
    if fudge:
        status = 'fudge'
    else:
        run_times = ['Saturday:1900', 'Monday:1630', 'Monday:1900']
        # setup times so they kick off early and get logged in and hopefully loop until event is open
        run_times = ['Saturday:1859', 'Monday:1629', 'Monday:1859']
#        run_times = ['Saturday:1900', 'Monday:1630', 'Monday:1900', 'Friday:1018', 'Friday:1009', 'Monday:1154', 'Sunday:1051']
        run_days = get_run_days(run_times)
        while True:
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.strftime("%M")
            day = now.strftime("%A")
            if day in run_days:
                delay = 40
            else:
                delay = 600
            now = day+':'+str(hour)+str(minute)
            print("{} {}".format(now, run_times))
            if now in run_times:
                status = 'run'
                break
            else:
                print("SLEEP: {}".format(delay))
                time.sleep(delay)
    return(status)

def get_run_days(run_times):
    run_days = set()
    for run_time in run_times:
        run_day = run_time.split(':')[0]
        run_days.add(run_day)
    return(run_days)

m_username = os.environ['m_username']
m_password = os.environ['m_password']
'''
print("username: {}".format(m_username))
print("password: {}".format(m_password))
quit()
'''

if __name__ == '__main__':
    main()
