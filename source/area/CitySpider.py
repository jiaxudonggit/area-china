# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (二级：地级市)
@author jxd
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy

from pyquery import PyQuery

from source.area.CountySpider import CountySpider
from source.area.util import RequestUtil


class CitySpider(object):

    def __init__(self, encoding: str, headers: list, provinces: dict, is_multi_thread: bool = False, sleep: int = 3):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param provinces: 一级：省、直辖市、自治区字典
        :param is_multi_thread: 是否开启多线程
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.provinces = provinces
        self.provinces_copy = deepcopy(provinces)
        self.is_multi_thread = is_multi_thread
        self.sleep = sleep

    def start_requests(self, code: str, province: dict) -> dict:
        """
        开始请求二级：地级市
        :param code:
        :param province:
        :return:
        """

        cities = {}

        if not province.get('url'):
            return cities

        print(f"开始获取{province.get('name')}下的地级市信息...")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=province.get('url'), headers=headers, encoding=self.encoding)
        if not res:
            print(province.get('name'), '请求失败...')
            return cities

        doc = PyQuery(res, url=province.get('url'), encoding=self.encoding)
        if not doc:
            print('二级地级市信息获取错误,检查页面变化...')
            return cities

        # 当前一级下的所有二级地级市信息
        for tr in doc('.citytr').items():
            tr.make_links_absolute()
            data = tr('a').text().split()
            cities.setdefault(data[0], {
                'code': data[0],  # 统计汇总识别码-划分代码
                'name': data[1],  # 城市名称
                'province_id': province.get('_id'),  # 省ID
                'province_name': province.get('name'),  # 省名称
                'url': tr('a').attr('href'),  # 下级链接地址
                'searched': False,  # 是否搜索过下级链接地址
                'child': {}  # 三级区县字典
            })
        # 更新省级信息
        self.provinces[code]['searched'] = True

        # 获取三级区县
        county_tool = CountySpider(encoding=self.encoding, headers=self.headers, cities=cities, is_multi_thread=self.is_multi_thread)
        if self.is_multi_thread:
            county_tool.multi_thread()
        else:
            county_tool.one_thread()
        print(f"获取三级区县:{county_tool.cities}")
        self.provinces[code]['child'] = county_tool.cities
        return county_tool.cities

    def multi_thread(self):

        with ThreadPoolExecutor(max_workers=16) as t:  # 创建一个最大容纳数量为6的线程池
            all_task = []
            for code, province in self.provinces_copy.items():
                task = t.submit(self.start_requests, code, province)
                all_task.append(task)

            for future in as_completed(all_task):
                print(f"获取地级市线程结束: {future.result()}")

    def one_thread(self):

        for code, province in self.provinces_copy.items():
            result = self.start_requests(code, province)
            print(f"获取{province.get('name')}地级市结束: {result}")
