# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (五级：村、居委会)
@author jxd
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from typing import Any

from pyquery import PyQuery

from source.area.WriteExcel import WriteExcel
from source.area.util import RequestUtil


class VillageSpider(object):

    def __init__(self, encoding: str, headers: list, towns: list, thread_num: int = 3, sleep: int = 1, excel_tool: WriteExcel = None):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param towns: 四级镇、乡、民族乡、县辖区、街字典
        :param excel_tool: excel工具类对象
        :param thread_num: 多线程数
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.towns = towns
        self.excel_tool = excel_tool
        self.thread_num = thread_num
        self.sleep = sleep

    def start_requests(self, town) -> Any:
        """
        开始请求五级：村、居委会
        :return:
        """

        villages = []

        if not town.get('url'):
            # 没有下一步链接就写入excel
            self.excel_tool.append_data(sheet_name=town.get("province_name"), value=town.get("value", []))
            return None

        print(f"开始获取{town.get('province_name')}-{town.get('city_name')}-{town.get('county_name')}-{town.get('name')}下的五级村居委会信息")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=town.get('url'), timeout=3, headers=headers, encoding=self.encoding)
        if not res:
            print(town.get('name'), '请求失败...')
            return None

        doc = PyQuery(res, url=town.get('url'), encoding=self.encoding)
        if not doc:
            print('五级村居委会信息获取错误,检查页面变化...')
            return None

        for tr in doc('.villagetr').items():
            data = tr('td').text().split()
            villages.append({
                'code': data[0],  # 统计汇总识别码-划分代码
                'code_type': data[1],  # 城乡分类代码
                'name': data[2],  # 村级名称
                'province_name': town.get('province_name'),  # 省名称
                'value': town.get("value", []) + [data[0], data[1], data[2]]
            })

            # 存入excel
            self.excel_tool.append_data(sheet_name=town.get('province_name'), value=town.get("value", []) + [data[0], data[1], data[2]])

        return villages

    def multi_thread(self):
        self.towns_copy = deepcopy(self.towns)
        with ThreadPoolExecutor(max_workers=6) as t:  # 创建一个最大容纳数量为6的线程池
            all_task = []
            for town in self.towns_copy:
                task = t.submit(self.start_requests, town)
                all_task.append(task)

            for future in as_completed(all_task):
                print(f"获取五级村居委会线程结束: {future.result()}")

    def one_thread(self):

        for town in self.towns:
            result = self.start_requests(town)
            print(f"获取{town.get('name')}五级村居委会结束: {result}")
