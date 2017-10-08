#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/10/6 11:39
# @File    : crack_geetest.py
# @Software: PyCharm

import time, random, re
import StringIO
import urllib2
import PIL.Image
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as ec


class WebCracker(object):
    def __init__(self, driver_name, timeout=20, freq=1):
        if driver_name.lower() == 'chrome':
            self.driver = webdriver.Chrome()
        elif driver_name.lower() == 'phantomjs':
            # TODO
            pass
        self.wait = WebDriverWait(self.driver, timeout=timeout, poll_frequency=freq)
        self.driver.set_page_load_timeout(20)
        self.driver.set_script_timeout(10)

    def run_crack(self, word, url='http://www.gsxt.gov.cn/index.html'):
        self.driver.get(url)
        # send keyword
        element = self.wait_appear(By.ID, 'keyword')
        element.send_keys(word)
        time.sleep(0.1)
        self.driver.find_element_by_id('btn_query').click()
        # get image
        self.wait_appear(By.CLASS_NAME, 'gt_cut_fullbg_slice')
        image1 = self.get_image("//div[@class='gt_cut_fullbg_slice']")
        image2 = self.get_image("//div[@class='gt_cut_bg_slice']")
        # get first different place
        pos = self.get_diff_place(image1, image2) - 5
        print pos
        # simulate
        self.simulate(pos)
        self.wait_appear(By.CLASS_NAME, 'search-result')
        print self.driver.current_url
        # self.driver.close()

    def simulate(self, pos):
        # select the ball
        element = self.driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
        ActionChains(self.driver).click_and_hold(on_element=element).perform()

        diff = [1, 1, -1, -1, -1, 1, -1]
        pos += random.choice(diff)
        while pos > 0:
            mul = random.random()
            off = random.randint(0, 4)
            ActionChains(self.driver).move_by_offset(off, 0).perform()
            time.sleep(mul * 0.05)
            pos -= off

        time.sleep(0.11)
        ActionChains(self.driver).release(on_element=element).perform()
        element = self.wait_appear(By.CLASS_NAME, "gt_info_content")
        result = element.text.encode("utf-8")
        print result

    def wait_appear(self, what, value):
        return self.wait.until(ec.presence_of_element_located((what, value)))

    # Image Process
    def get_image(self, xpath):
        location_list = []
        image_url = ''
        for each in self.driver.find_elements_by_xpath(xpath):
            location = {}
            location['x'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                           each.get_attribute('style'))[0][1])
            location['y'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                           each.get_attribute('style'))[0][2])
            image_url = re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                  each.get_attribute('style'))[0][0]
            location_list.append(location)
        print image_url
        image = StringIO.StringIO(self.repeat_get(image_url))
        return self.recover_image(image, location_list)

    @staticmethod
    def repeat_get(url, times=10):
        while times > 0:
            try:
                tmp = urllib2.urlopen(url)
                return tmp.read()
            except:
                times -= 1

    @staticmethod
    def recover_image(org_image, location_list):
        org_image = PIL.Image.open(org_image)
        image = PIL.Image.new('RGB', (260, 116))
        low_offset_x = 0
        high_offset_x = 0
        for each in location_list:
            if each['y'] == -58:
                chip = org_image.crop((abs(each['x']), 58, abs(each['x']) + 10, 166))
                image.paste(chip, (low_offset_x, 0))
                low_offset_x += 10
            else:
                chip = org_image.crop((abs(each['x']), 0, abs(each['x']) + 10, 58))
                image.paste(chip, (high_offset_x, 58))
                high_offset_x += 10
        return image

    @staticmethod
    def get_diff_place(image1, image2):
        for i in range(260):
            for j in range(116):
                for k in range(3):
                    if abs(image1.getpixel((i, j))[k] - image2.getpixel((i, j))[k]) > 50:
                        return i


if __name__ == '__main__':
    wc = WebCracker('chrome')
    wc.run_crack(u'百度')
