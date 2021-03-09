# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (二级：地级市)
@author jxd
"""
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from pyquery import PyQuery

from source.area.CountySpider import CountySpider
from source.area.WriteExcel import WriteExcel
from source.area.util import RequestUtil


class CitySpider(object):

    def __init__(self, encoding: str, headers: list, provinces: list, is_multi_thread: bool = False, excel_tool: WriteExcel = None,
                 thread_num: int = 3, sleep: float = 1):
        """
        :param encoding: 编码
        :param headers: 请求头列表
        :param provinces: 一级：省、直辖市、自治区字典
        :param excel_tool: excel工具类对象
        :param is_multi_thread: 是否开启多线程
        :param thread_num: 多线程数
        :param sleep: 请求间隔时间
        """
        self.encoding = encoding
        self.headers = headers
        self.provinces = provinces
        self.excel_tool = excel_tool
        self.is_multi_thread = is_multi_thread
        self.thread_num = thread_num
        self.sleep = sleep

    def start_requests(self, province: dict) -> Any:
        """
        开始请求二级：地级市
        :param province:
        :return:
        """

        cities = []

        if not province.get('url'):
            return None

        print(f"开始获取{province.get('name')}下的地级市信息...")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=province.get('url'), headers=headers, encoding=self.encoding)
        if not res:
            print(f'{province.get("name")}二级地级市信息获取错误, 请求失败...')
            return None

        doc = PyQuery(res, url=province.get('url'), encoding=self.encoding)
        if not doc:
            print('二级地级市信息获取错误,检查页面变化...')
            return None

        # 当前一级下的所有二级地级市信息
        for tr in doc('.citytr').items():
            tr.make_links_absolute()
            data = tr('a').text().split()
            cities.append({
                'code': data[0],  # 统计汇总识别码-划分代码
                'name': data[1],  # 城市名称
                'province_name': province.get('name'),  # 省名称
                'url': tr('a').attr('href'),  # 下级链接地址
                'value': [data[0], data[1]]
            })

        # 创建sheet
        work_sheet_detail = self.excel_tool.workbook.active
        if "Sheet" not in work_sheet_detail.title:
            self.excel_tool.create_sheet(province.get("name", ""))
        else:
            work_sheet_detail.title = province.get("name", "")
            # 插入表头
            work_sheet_detail.append(self.excel_tool.HEADER)

        # 获取三级区县
        county_tool = CountySpider(encoding=self.encoding, headers=self.headers, cities=cities, excel_tool=self.excel_tool,
                                   is_multi_thread=self.is_multi_thread, thread_num=self.thread_num, sleep=self.sleep)
        if self.is_multi_thread:
            county_tool.multi_thread()
        else:
            county_tool.one_thread()

        return cities

    def multi_thread(self):
        with ThreadPoolExecutor(max_workers=self.thread_num) as t:  # 创建一个最大容纳数量为n的线程池
            for result in t.map(self.start_requests, self.provinces):
                print(f"获取{result[0].get('province_name')}地级市线程结束: length={len(result)}")

    def one_thread(self):
        for province in self.provinces:
            result = self.start_requests(province)
            print(f"获取{province.get('name')}地级市结束: length={len(result)}")
