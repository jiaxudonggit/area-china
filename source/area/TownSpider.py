# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (四级：镇、乡、民族乡、县辖区、街道)
@author jxd
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy

from pyquery import PyQuery

from source.area.VillageSpider import VillageSpider
from source.area.util import RequestUtil


class TownSpider(object):

    def __init__(self, encoding: str, headers: list, counties: dict, is_multi_thread: bool = False, sleep: int = 3):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param cities: 三级市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区字典
        :param is_multi_thread: 是否开启多线程
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.counties = counties
        self.counties_copy = deepcopy(counties)
        self.is_multi_thread = is_multi_thread
        self.sleep = sleep

    def start_requests(self, code, county):
        """
        开始请求四级：镇、乡、民族乡、县辖区、街
        :param county:
        :param code:
        :return:
        """
        towns = {}

        if not county.get('url'):
            return towns

        print(f"开始获取{county.get('province_name')}-{county.get('city_name')}-{county.get('name')}下的四级乡镇信息")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=county.get('url'), timeout=5, headers=headers, encoding=self.encoding)
        if not res:
            print(county.get('name'), '请求失败...')
            return towns

        doc = PyQuery(res, url=county.get('url'), encoding=self.encoding)
        if not doc:
            print('四级乡镇信息获取错误,检查页面变化...')

        for tr in doc('.towntr').items():
            tr.make_links_absolute()
            data = tr('a').text().split()
            towns.setdefault(data[0], {
                'code': data[0],  # 统计汇总识别码-划分代码
                'name': data[1],  # 镇级名称
                'county_id': county.get('_id'),  # 区县ID
                'county_name': county.get('name'),  # 区县名称
                'city_id': county.get('city_id'),  # 市ID
                'city_name': county.get('city_name'),  # 市名称
                'province_id': county.get('province_id'),  # 省ID
                'province_name': county.get('province_name'),  # 省名称
                'url': tr('a').attr('href'),  # 下级链接地址
                'searched': False,  # 是否搜索过下级链接地址
                'child': {}  # 五级村居委会字典
            })

        # 更新区县信息
        self.counties[code]['searched'] = True

        # 获取五级村居委会
        town_tool = VillageSpider(encoding=self.encoding, headers=self.headers, towns=towns)
        if self.is_multi_thread:
            town_tool.multi_thread()
        else:
            town_tool.one_thread()
        print(f"获五级村居委会:{town_tool.towns}")
        self.counties[code]['child'] = town_tool.towns
        return town_tool.towns

    def multi_thread(self):

        with ThreadPoolExecutor(max_workers=6) as t:  # 创建一个最大容纳数量为6的线程池
            all_task = []
            for code, county in self.counties_copy.items():
                task = t.submit(self.start_requests, code, county)
                all_task.append(task)

            for future in as_completed(all_task):
                print(f"获取四级乡镇线程结束: {future.result()}")

    def one_thread(self):

        for code, county in self.counties_copy.items():
            result = self.start_requests(code, county)
            print(f"获取{county.get('name')}四级乡镇结束: {result}")
