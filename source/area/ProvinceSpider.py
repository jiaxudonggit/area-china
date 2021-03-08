# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (一级：省、直辖市、自治区)
@author jxd
"""

import random
import time

from pyquery import PyQuery

from source.area.CitySpider import CitySpider
from source.area.util import RequestUtil


class ProvinceSpider(object):

    def __init__(self, domain_url: str, encoding: str, headers: list, province_code: list = None, is_multi_thread: bool = False, sleep: int = 3):
        """
        :param domain_url: 爬取页面链接
        :param encoding: 编码
        :param headers: 请求头列表
        :param province_code: 统计代码
        :param is_multi_thread: 是否开启多线程
        :param sleep: 请求间隔时间
        """
        self.domain_url = domain_url
        self.encoding = encoding
        self.headers = headers
        self.province_code = province_code
        self.provinces = {}
        self.is_multi_thread = is_multi_thread
        self.sleep = sleep

    def start_requests(self) -> dict:
        """
        开始请求一级：省、直辖市、自治区
        :return:
        """

        provinces = {}

        print(f"开始获取一级省、直辖市、自治区信息...")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=self.domain_url, headers=headers, encoding=self.encoding)
        if not res:
            print('请求失败...')
            return provinces

        doc = PyQuery(res, url=self.domain_url, encoding=self.encoding).find('.provincetr')
        if not doc:
            print('首页省份信息获取错误,检查页面变化...')
            return provinces

        for td in doc('td').items():
            a_tag = td('a')
            if a_tag:
                # 生成URL绝对路径
                a_tag.make_links_absolute()
                code = a_tag.attr('href').split('/')[-1].split('.')[0]

                if self.province_code:
                    if str(code) in [str(code) for code in self.province_code]:
                        provinces.setdefault(code, {
                            'code': code,  # 统计汇总识别码-划分代码
                            'name': a_tag.text(),  # 省份名称
                            'url': a_tag.attr('href'),  # 下级链接地址
                            'searched': False,  # 是否搜索过下级链接地址
                            'child': {}  # 地级市字典
                        })
                        break
                else:
                    provinces.setdefault(code, {
                        'code': code,  # 统计汇总识别码-划分代码
                        'name': a_tag.text(),  # 省份名称
                        'url': a_tag.attr('href'),  # 下级链接地址
                        'searched': False,  # 是否搜索过下级链接地址
                        'child': {}  # 地级市字典
                    })

        # 获取三级区县
        city_tool = CitySpider(encoding=self.encoding, headers=self.headers, provinces=provinces, is_multi_thread=self.is_multi_thread)
        city_tool.multi_thread()
        print(f"获取地级市:{city_tool.provinces}")
        self.provinces = city_tool.provinces

        return city_tool.provinces
