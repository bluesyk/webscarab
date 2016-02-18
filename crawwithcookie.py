#-*- coding: utf-8 -*-
from selenium import webdriver
import time,pickle,json,urllib2,m3u8,traceback,shutil,os

#删除目录函数
def remove_folder(path):
    # check if folder exists
    if os.path.exists(path):
         # remove if exists
         shutil.rmtree(path)

#if os.path.exists('output'):
#    remove_folder('output')
#os.mkdir('output');

#设置底层要调用的浏览器引擎
#driver = webdriver.PhantomJS(executable_path='C:\phantomjs-1.9.7-windows\phantomjs.exe')
driver = webdriver.Chrome()

#需要在首页设置cookies完后再跳转
driver.get("http://edu.gooann.com")
print 'load cookies'
cookies = pickle.load(open("cookies.pkl", "rb"))
#print cookies
for cookie in cookies:
    driver.add_cookie(cookie)


#跳转到要抓取数据的课程首页
driver.get("http://edu.gooann.com/course/162")
#driver.get_screenshot_as_file('show.png')
#print driver.page_source

#从页面中抓取课程的章节链接
# ul class="period-list" id="course-item-list">...
# <li><a href="/course/151/learn#lesson/1382" title="Kali Linux渗透测试介绍">...
domlinks= driver.find_element_by_css_selector('ul#course-item-list').find_elements_by_css_selector('a')

#需要实现提取数据，避免页面切换后dom元素释放，造成不可访问
links =[];
for domlink in domlinks:
    linkdict={};
    linkdict['href'] = domlink.get_attribute('href');
    linkdict['title'] = domlink.find_elements_by_css_selector('span.title')[0].text;
    links.append(linkdict)

for count, link in enumerate(links, start=1):
    url = link['href']

    #去掉无效的字符，避免保存中文文件名失败
    title = link['title'].replace('\\','').replace('/','')

    try:
        print '\r\nbegin to fetch '+ title +' ' +url;
        #进入子页面
        driver.get(url)
        #wait iframe to load
        time.sleep(3)

        #从iframe下面提取m3u8的链接
        #<iframe src="../../course/151/lesson/1383/player" name="viewerIframe" id="viewerIframe" width="100%"
        #  allowfullscreen="" webkitallowfullscreen="" height="100%" style="border:0px"></iframe>
        driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))

        #DOM节点 <div id="lesson-video-content" data-user-id="7082" data-file-id="1167" data-file-type="video"
        #  data-url="http://edu.gooann.com/hls/1167/playlist/H0dYpAQKJiDqW8Rjuvv0MMXLyaIl8mty.m3u8" ...>
        m3u8_url = driver.find_element_by_id('lesson-video-content').get_attribute('data-url')
        driver.switch_to_default_content()

        data = urllib2.urlopen(m3u8_url).read()
        m3u8_data = json.loads(data)

        #取m3u8数组中最后一个数据，一般对应超清的m3u8链接, 这个URL不需要cookie,直接用urllib2读取
        url_src = m3u8_data[-1].get('src')
        #driver.get(url_src)
        #m3u8_file_data = driver.page_source;
        m3u8_file_data = urllib2.urlopen(url_src).read()
        m3u8_file_name='output\\'+ title +'.m3u8'
        with open(m3u8_file_name, 'w') as file_:
            file_.write(m3u8_file_data)

        #解析m3u8文件，获取key的url,请求key必须带上cookie
        m3u8_obj = m3u8.loads(m3u8_file_data);
        keyuri = m3u8_obj.segments[0].key.uri;
        print 'keyuri:'+keyuri;

        #Key读取有限制，最多不能超过2次，否则后面的数字都是错误的，48个字节
        driver.get(keyuri)
        m3u8_key_data = driver.find_element_by_css_selector('body').text;
        print 'key len:' +str(len(m3u8_key_data)) + ', key data:' + m3u8_key_data
        key_file_name='output\\'+title+'.key'
        with open(key_file_name, 'w') as file_:
            file_.write(m3u8_key_data)
    except:
        print 'failed to fetch '+ title +' ' +url;
        print traceback.print_exc()








