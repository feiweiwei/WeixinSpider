# Python爬取微信公众号文章

最近在做一个自己的项目，涉及到需要通过python爬取微信公众号的文章，因为微信独特一些手段，导致无法直接爬取，研究了一些文章大概有了思路，并且网上目前能搜到的方案思路都没啥问题，但是里面的代码因为一些三方库的变动基本都不能用了，这篇文章写给需要爬取公众号文章的朋友们，文章最后也会提供python源码下载。

## 公众号爬取方式

爬取公众号目前主流的方案主要有两种，一种是通过搜狗搜索微信公众号的页面去找到文章地址，再去爬取具体文章内容；第二种是通过注册公众号然后通过公众号的搜索接口去查询到文章地址，然后再根据地址去爬文章内容。

这两种方案各有优缺点，通过搜狗搜索来做其实核心思路就是通过request模拟搜狗搜索公众号，然后解析搜索结果页面，再根据公众号主页地址爬虫，爬取文章明细信息，但是这里需要注意下，因为搜狗和腾讯之间的协议问题,只能显示最新的10条文章，没办法拿到所有的文章。如果要拿到所有文章的朋友可能要采用第二种方式了。第二种方式的缺点就是要注册公众号通过腾讯认证，流程麻烦些，通过调用接口公众号查询接口查询，但是翻页需要通过selenium去模拟滑动翻页操作，整个过程还是挺麻烦的。因为我的项目里不需要历史文章，所以我采用通过搜狗搜索去做爬取公众号的功能。



## 爬取最近10篇公众号文章

python需要依赖的三方库如下：

urllib、pyquery、requests、selenium

具体的逻辑都写在注释里了，没有特别复杂的地方。

爬虫核心类

```python
#!/usr/bin/python
# coding: utf-8

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from urllib import quote
from pyquery import PyQuery as pq

import requests
import time
import re
import os

from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait


# 搜索入口地址，以公众为关键字搜索该公众号
def get_search_result_by_keywords(sogou_search_url):
    # 爬虫伪装头部设置
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'}

    # 设置操作超时时长
    timeout = 5
    # 爬虫模拟在一个request.session中完成
    s = requests.Session()
    log(u'搜索地址为：%s' % sogou_search_url)
    return s.get(sogou_search_url, headers=headers, timeout=timeout).content


# 获得公众号主页地址
def get_wx_url_by_sougou_search_html(sougou_search_html):
    doc = pq(sougou_search_html)
    return doc('div[class=txt-box]')('p[class=tit]')('a').attr('href')


# 使用webdriver 加载公众号主页内容，主要是js渲染的部分
def get_selenium_js_html(url):
    options = Options()
    options.add_argument('-headless')  # 无头参数
    driver = Chrome(executable_path='chromedriver', chrome_options=options)
    wait = WebDriverWait(driver, timeout=10)

    driver.get(url)
    time.sleep(3)
    # 执行js得到整个页面内容
    html = driver.execute_script("return document.documentElement.outerHTML")
    driver.close()
    return html


# 获取公众号文章内容
def parse_wx_articles_by_html(selenium_html):
    doc = pq(selenium_html)
    return doc('div[class="weui_media_box appmsg"]')


# 将获取到的文章转换为字典
def switch_arctiles_to_list(articles):
    # 定义存贮变量
    articles_list = []
    i = 1

    # 遍历找到的文章，解析里面的内容
    if articles:
        for article in articles.items():
            log(u'开始整合(%d/%d)' % (i, len(articles)))
            # 处理单个文章
            articles_list.append(parse_one_article(article))
            i += 1
    return articles_list


# 解析单篇文章
def parse_one_article(article):
    article_dict = {}

    # 获取标题
    title = article('h4[class="weui_media_title"]').text().strip()
    ###log(u'标题是： %s' % title)
    # 获取标题对应的地址
    url = 'http://mp.weixin.qq.com' + article('h4[class="weui_media_title"]').attr('hrefs')
    log(u'地址为： %s' % url)
    # 获取概要内容
    summary = article('.weui_media_desc').text()
    log(u'文章简述： %s' % summary)
    # 获取文章发表时间
    date = article('.weui_media_extra_info').text().strip()
    log(u'发表时间为： %s' % date)
    # 获取封面图片
    pic = parse_cover_pic(article)

    # 返回字典数据
    return {
        'title': title,
        'url': url,
        'summary': summary,
        'date': date,
        'pic': pic
    }


# 查找封面图片，获取封面图片地址
def parse_cover_pic(article):
    pic = article('.weui_media_hd').attr('style')

    p = re.compile(r'background-image:url\((.*?)\)')
    rs = p.findall(pic)
    log(u'封面图片是：%s ' % rs[0] if len(rs) > 0 else '')

    return rs[0] if len(rs) > 0 else ''


# 自定义log函数，主要是加上时间
def log(msg):
    print u'%s: %s' % (time.strftime('%Y-%m-%d_%H-%M-%S'), msg)


# 验证函数
def need_verify(selenium_html):
    ' 有时候对方会封锁ip，这里做一下判断，检测html中是否包含id=verify_change的标签，有的话，代表被重定向了，提醒过一阵子重试 '
    return pq(selenium_html)('#verify_change').text() != ''


# 创建公众号命名的文件夹
def create_dir(keywords):
    if not os.path.exists(keywords):
        os.makedirs(keywords)

        # 爬虫主函数


def run(keywords):
    ' 爬虫入口函数 '
    # Step 0 ：  创建公众号命名的文件夹
    create_dir(keywords)

    # 搜狐微信搜索链接入口
    sogou_search_url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&s_from=input&_sug_=n&_sug_type_=' % quote(
        keywords)

    # Step 1：GET请求到搜狗微信引擎，以微信公众号英文名称作为查询关键字
    log(u'开始获取，微信公众号英文名为：%s' % keywords)
    log(u'开始调用sougou搜索引擎')
    sougou_search_html = get_search_result_by_keywords(sogou_search_url)

    # Step 2：从搜索结果页中解析出公众号主页链接
    log(u'获取sougou_search_html成功，开始抓取公众号对应的主页wx_url')
    wx_url = get_wx_url_by_sougou_search_html(sougou_search_html)
    log(u'获取wx_url成功，%s' % wx_url)

    # Step 3：Selenium+PhantomJs获取js异步加载渲染后的html
    log(u'开始调用selenium渲染html')
    selenium_html = get_selenium_js_html(wx_url)

    # Step 4: 检测目标网站是否进行了封锁
    if need_verify(selenium_html):
        log(u'爬虫被目标网站封锁，请稍后再试')
    else:
        # Step 5: 使用PyQuery，从Step 3获取的html中解析出公众号文章列表的数据
        log(u'调用selenium渲染html完成，开始解析公众号文章')
        articles = parse_wx_articles_by_html(selenium_html)
        log(u'抓取到微信文章%d篇' % len(articles))

        # Step 6: 把微信文章数据封装成字典的list
        log(u'开始整合微信文章数据为字典')
        articles_list = switch_arctiles_to_list(articles)
        return [content['title'] for content in articles_list]

```

main入口函数：

```python
# coding: utf8
import spider_weixun_by_sogou

if __name__ == '__main__':

    gongzhonghao = raw_input(u'input weixin gongzhonghao:')
    if not gongzhonghao:
        gongzhonghao = 'spider'
    text = " ".join(spider_weixun_by_sogou.run(gongzhonghao))

    print text
```

直接运行main方法，在console中输入你要爬的公众号的英文名称，中文可能会搜出来多个，这里做的是精确搜索只搜出来一个，查看公众号英文号，只要在手机上点开公众号然后查看公众号信息就可以看到如下爬虫结果爬到了文章的相关信息，文章具体的内容可以通过调用代码中的webdriver.py去爬取。

![Screenshot 2018-08-30 17.56.09](http://otxp3yk5p.bkt.clouddn.com/Screenshot 2018-08-30 17.56.09.png)



## 爬取公众号注意事项

1. Selenium support for PhantomJS has been deprecated, please use headless versions of Chrome or Firefox instead   warnings.warn('Selenium support for PhantomJS has been deprecated, please use headless ' 

   网上很多的文章都还在使用PhantomJS，其实从去年Selenium就已经不支持PhantomJS了，现在使用Selenium初始化浏览器的话需要使用webdriver初始化无头参数的Chrome或者Firefox driver。

   具体可以参考官网链接：https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Headless_mode

2. Can not connect to the Service chromedriver／firefoxdriver

   在开发过程中还遇到这个坑，这个问题一般有两种可能性，一种是没有配置chromedriver或者geckodriver的环境变量，这里需要注意下将chromedriver或者geckodriver文件一定要配置环境变量到PATH下，或者干脆粗暴一点直接将这两个文件复制到/usr/bin目录下；

   还有种可能是没有配置hosts，如果大家发现这个问题检查下自己的hosts文件是不是没有配置`127.0.0.1 localhost`,只要配置上就好了。

   这里还有一点要注意的就是使用chrome浏览器的话，还要注意chrome浏览器版本和chromedriver的对应关系，可以在这篇文章中查看也可以翻墙去google官网查看最新的对应关系。https://www.cnblogs.com/JHblogs/p/7699951.html

3. 防盗链

   微信公众号对文章中的图片做了防盗链处理，所以如果在公众号和小程序、PC浏览器以外的地方是无法显示图片的，这里推荐大家可以看下这篇文章了解下如何处理微信的防盗链。

    https://blog.csdn.net/tjcyjd/article/details/74643521

## 总结

好了上面说了那么多，大家最关心的就是源代码，这里放出github地址: https://github.com/feiweiwei/WeixinSpider.git，好用的话记得strar。


