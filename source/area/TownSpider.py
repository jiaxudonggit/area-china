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
from source.area.WriteExcel import WriteExcel
from source.area.util import RequestUtil


class TownSpider(object):

    def __init__(self, encoding: str, headers: list, counties: list, is_multi_thread: bool = False,
                 excel_tool: WriteExcel = None, thread_num: int = 3, sleep: int = 3):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param cities: 三级市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区字典
        :param excel_tool: excel工具类对象
        :param is_multi_thread: 是否开启多线程
        :param thread_num: 多线程数
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.counties = counties
        self.excel_tool = excel_tool
        self.is_multi_thread = is_multi_thread
        self.thread_num = thread_num
        self.sleep = sleep

    def start_requests(self, county):
        """
        开始请求四级：镇、乡、民族乡、县辖区、街
        :param county:
        :return:
        """
        towns = []

        if not county.get('url'):
            # 没有下一步链接就写入excel
            self.excel_tool.append_data(sheet_name=county.get("province_name"), value=county.get("value", []))
            return None

        print(f"开始获取{county.get('province_name')}-{county.get('city_name')}-{county.get('name')}下的四级乡镇信息")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=county.get('url'), timeout=5, headers=headers, encoding=self.encoding)
        if not res:
            print(county.get('name'), '请求失败...')
            return None

        doc = PyQuery(res, url=county.get('url'), encoding=self.encoding)
        if not doc:
            print('四级乡镇信息获取错误,检查页面变化...')
            return None

        for tr in doc('.towntr').items():
            tr.make_links_absolute()
            data = tr('a').text().split()
            towns.append({
                'code': data[0],  # 统计汇总识别码-划分代码
                'name': data[1],  # 镇级名称
                'province_name': county.get('province_name'),  # 省名称
                'city_name': county.get('city_name'),  # 省名称
                'county_name': county.get('name'),  # 省名称
                'url': tr('a').attr('href'),  # 下级链接地址
                'value': county.get('value', []) + [data[0], data[1]]
            })

        # 获取五级村居委会
        town_tool = VillageSpider(encoding=self.encoding, headers=self.headers, towns=towns, excel_tool=self.excel_tool,
                                  thread_num=self.thread_num, sleep=self.sleep)
        if self.is_multi_thread:
            town_tool.multi_thread()
        else:
            town_tool.one_thread()
        print(f"获五级村居委会:{towns}")

        return towns

    def multi_thread(self):
        self.counties_copy = deepcopy(self.counties)
        with ThreadPoolExecutor(max_workers=6) as t:  # 创建一个最大容纳数量为6的线程池
            all_task = []
            for county in self.counties_copy:
                task = t.submit(self.start_requests, county)
                all_task.append(task)

            for future in as_completed(all_task):
                print(f"获取四级乡镇线程结束: {future.result()}")

    def one_thread(self):

        for county in self.counties:
            result = self.start_requests(county)
            print(f"获取{county.get('name')}四级乡镇结束: {result}")
