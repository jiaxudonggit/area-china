# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (五级：村、居委会)
@author jxd
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy

from pyquery import PyQuery

from source.area.util import RequestUtil


class VillageSpider(object):

    def __init__(self, encoding: str, headers: list, towns: dict, sleep: int = 3):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param cities: 四级镇、乡、民族乡、县辖区、街字典
        :param is_multi_thread: 是否开启多线程
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.towns = towns
        self.towns_copy = deepcopy(towns)
        self.sleep = sleep

    def start_requests(self, code, town):
        """
        开始请求五级：村、居委会
        :return:
        """

        villages = {}

        if not town.get('url'):
            return villages

        print(f"开始获取{town.get('province_name')}-{town.get('city_name')}-{town.get('county_name')}-{town.get('name')}下的五级村居委会信息")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=town.get('url'), timeout=3, headers=headers, encoding=self.encoding)
        if not res:
            print(town.get('name'), '请求失败...')
            return villages

        doc = PyQuery(res, url=town.get('url'), encoding=self.encoding)
        if not doc:
            print('五级村居委会信息获取错误,检查页面变化...')

        for tr in doc('.villagetr').items():
            data = tr('td').text().split()
            villages.setdefault(data[0], {
                'code': data[0],  # 统计汇总识别码-划分代码
                'code_type': data[1],  # 城乡分类代码
                'name': data[2],  # 村级名称
                'town_id': town.get('_id'),  # 镇级ID
                'town_name': town.get('name'),  # 镇级名称
                'county_id': town.get('county_id'),  # 区县ID
                'county_name': town.get('county_name'),  # 区县名称
                'city_id': town.get('city_id'),  # 市ID
                'city_name': town.get('city_name'),  # 市名称
                'province_id': town.get('province_id'),  # 省ID
                'province_name': town.get('province_name')  # 省名称
            })

        # 更新镇级信息
        self.towns[code]['searched'] = True
        self.towns[code]['villages'] = villages

        return villages

    def multi_thread(self):

        with ThreadPoolExecutor(max_workers=6) as t:  # 创建一个最大容纳数量为6的线程池
            all_task = []
            for code, town in self.towns_copy.items():
                task = t.submit(self.start_requests, code, town)
                all_task.append(task)

            for future in as_completed(all_task):
                print(f"获取五级村居委会线程结束: {future.result()}")

    def one_thread(self):

        for code, town in self.towns_copy.items():
            result = self.start_requests(code, town)
            print(f"获取{town.get('name')}五级村居委会结束: {result}")
