# -*- coding: UTF-8 -*-
"""
@description 工具类，requests库二次封装
@author jxd
"""
import re
import time
from urllib.parse import urljoin

import execjs
import requests
from requests.exceptions import InvalidURL


def get(url, timeout=None, headers=None, encoding=None):
    """
    发送GET请求
    :param url: URL
    :param timeout: 超时时间(秒)
    :param headers: 头部信息
    :param encoding: 编码
    :return:
    """
    try:
        # 参数验证,URL不能为空
        if not url:
            raise InvalidURL("Invalid URL %r" % url)

        sess = requests.session()
        response = sess.get(url, headers=headers, timeout=timeout)
        if not response:
            response.close()
            return None
        if encoding:
            response.encoding = encoding
        res_content = response.text
        new_url = get_url(res_content, url, headers, timeout)
        if new_url:
            time.sleep(3)
            return get(url=url, headers=headers, timeout=timeout, encoding=encoding)
        r_text = response.text
        response.close()
        return r_text
    except Exception as e:
        print(f"爬取失败：反爬机制 {e}")
        return None


def prepare_url(url):
    """
    预处理URL连接，规范url
    www.a.com  //www.a.com ==>> http://www.a.com
    :param url: URL
    :return: 处理的URL
    """
    if not url:
        return None
    res = url
    if url.startswith('//'):
        res = 'http:' + url
    elif not url.startswith('http://') and not url.startswith('https://'):
        res = 'http://' + url
    return res


def get_url(html, url, headers, timeout):
    js = re.findall(r'<script type="text/javascript">([\w\W]*)</script>', html)
    if not js:
        return None
    js = js[0]
    js = re.sub(r'atob\(', 'window["atob"](', js)
    js2 = 'function getURL(){ var window = {};' + js + 'return window["location"];}'
    ctx = execjs.compile(js2)
    tail = ctx.call('getURL')
    url2 = urljoin(url, tail)
    print(url2)
    return url2
