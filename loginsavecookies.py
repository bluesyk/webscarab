#-*- coding: utf-8 -*-
from selenium import webdriver
import time
import pickle

#phamtomsjs是没有界面的浏览器引擎，其他的是有界面的浏览器引擎。
#driver = webdriver.PhantomJS(executable_path='C:\phantomjs-1.9.7-windows\phantomjs.exe')
driver = webdriver.Chrome()


driver.get("http://edu.gooann.com/login")
driver.find_element_by_xpath('//input[@name="_username"]').send_keys(u'中文账户')
driver.find_element_by_xpath('//input[@name="_password"]').send_keys('密码')
driver.find_element_by_xpath('//button[@class="btn btn-primary btn-lg btn-block"]').click()
time.sleep(2)

#保存屏幕截屏
driver.get_screenshot_as_file('show.png')
print driver.current_url
print driver.get_cookies()

#save cookies
print 'dump cookies'
pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))

#driver.get("http://edu.gooann.com/course/151")
#driver.get_screenshot_as_file('show.png')
#print driver.current_url





