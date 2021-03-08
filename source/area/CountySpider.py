# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (三级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区)
@author jxd
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from pyquery import PyQuery

from source.area.TownSpider import TownSpider
from source.area.WriteExcel import WriteExcel
from source.area.util import RequestUtil


class CountySpider(object):

    def __init__(self, encoding: str, headers: list, cities: list, is_multi_thread: bool = False, excel_tool: WriteExcel = None,
                 thread_num: int = 3, sleep: int = 1):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param cities: 二级地级市字典
        :param excel_tool: excel工具类对象
        :param is_multi_thread: 是否开启多线程
        :param thread_num: 多线程数
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.cities = cities
        self.excel_tool = excel_tool
        self.is_multi_thread = is_multi_thread
        self.thread_num = thread_num
        self.sleep = sleep

    def start_requests(self, city: dict) -> Any:
        """
        开始请求三级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区
        :param city:
        :return:
        """
        counties = []

        if not city.get('url'):
            # 没有下一步链接就写入excel
            self.excel_tool.append_data(sheet_name=city.get("province_name"), value=city.get("value", []))
            return None

        print(f"开始获取{city.get('province_name')}-{city.get('name')}下的三级区县信息...")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=city.get('url'), headers=headers, encoding=self.encoding)
        if not res:
            print(city.get('name'), '请求失败...')
            return None

        doc = PyQuery(res, url=city.get('url'), encoding=self.encoding)
        if not doc:
            print('三级区县信息获取错误,检查页面变化...')
            return None

        # 当前二级下的所有三级区县信息
        for tr in doc('.countytr').items():
            tr.make_links_absolute()
            data = tr('a').text().split()
            if not tr('a') or not data:
                # 当非直辖市的区县有一个市辖区无下级链接
                data = tr('td').text().split()
            item = {
                'code': data[0],  # 统计汇总识别码-划分代码
                'name': data[1],  # 区县名称
                'province_name': city.get('province_name'),  # 省名称
                'city_name': city.get('name'),  # 省名称
                'value': city.get('value', []) + [data[0], data[1]]
            }
            if not tr('a') or not data:
                item.setdefault('url', None)
            else:
                item.setdefault('url', tr('a').attr('href'))  # 下级链接地址
            counties.append(item)

        # 获取四级乡镇
        town_tool = TownSpider(encoding=self.encoding, headers=self.headers, counties=counties, excel_tool=self.excel_tool,
                               is_multi_thread=self.is_multi_thread, thread_num=self.thread_num, sleep=self.sleep)
        if self.is_multi_thread:
            town_tool.multi_thread()
        else:
            town_tool.one_thread()
        print(f"获取四级乡镇:{counties}")

        return counties

    def multi_thread(self):
        with ThreadPoolExecutor(max_workers=self.thread_num) as t:  # 创建一个最大容纳数量为n的线程池
            all_task = []
            for i in range(len(self.cities)):
                task = t.submit(self.start_requests, self.cities.pop(i))
                all_task.append(task)

            for future in as_completed(all_task):
                print(f"获取三级区县线程结束: {future.result()}")

    def one_thread(self):

        for i in range(len(self.cities)):
            city = self.cities.pop(i)
            result = self.start_requests(city)
            print(f"获取{city.get('name')}三级区县结束: {result}")
