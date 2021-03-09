# -*- coding: UTF-8 -*-
"""
@description 获取统计用区划代码和城乡划分代码 (一级：省、直辖市、自治区)
@author jxd
"""

import random
import time
from typing import Any

from pyquery import PyQuery

from source.area.CitySpider import CitySpider
from source.area.WriteExcel import WriteExcel
from source.area.util import RequestUtil


class ProvinceSpider(object):

    def __init__(self, domain_url: str, encoding: str, headers: list, province_code_list: list = None, excel_tool: WriteExcel = None,
                 is_multi_thread: bool = False, thread_num: int = 3, sleep: float = 1):
        """
        :param domain_url: 爬取页面链接
        :param encoding: 编码
        :param headers: 请求头列表
        :param province_code_list: 统计代码
        :param excel_tool: excel工具类对象
        :param is_multi_thread: 是否开启多线程
        :param thread_num: 多线程数
        :param sleep: 请求间隔时间
        """
        self.domain_url = domain_url
        self.encoding = encoding
        self.headers = headers
        self.province_code_list = province_code_list
        self.excel_tool = excel_tool
        self.is_multi_thread = is_multi_thread
        self.thread_num = thread_num
        self.sleep = sleep

    def start_requests(self) -> Any:
        """
        开始请求一级：省、直辖市、自治区
        :return:
        """

        provinces = []

        print(f"开始获取一级省、直辖市、自治区信息...")
        headers = random.choice(self.headers)
        time.sleep(self.sleep)
        res = RequestUtil.get(url=self.domain_url, headers=headers, encoding=self.encoding)
        if not res:
            print('首页省份信息获取错误,请求失败...')
            return None

        doc = PyQuery(res, url=self.domain_url, encoding=self.encoding).find('.provincetr')
        if not doc:
            print('首页省份信息获取错误,检查页面变化...')
            return None

        for td in doc('td').items():
            a_tag = td('a')
            if a_tag:
                # 生成URL绝对路径
                a_tag.make_links_absolute()
                code = a_tag.attr('href').split('/')[-1].split('.')[0]

                if self.province_code_list:
                    if str(code) in [str(code) for code in self.province_code_list]:
                        provinces.append({
                            'code': code,  # 统计汇总识别码-划分代码
                            'name': a_tag.text(),  # 省份名称
                            'url': a_tag.attr('href'),  # 下级链接地址
                            'value': [code, a_tag.text()]
                        })
                    else:
                        continue
                else:
                    provinces.append({
                        'code': code,  # 统计汇总识别码-划分代码
                        'name': a_tag.text(),  # 省份名称
                        'url': a_tag.attr('href'),  # 下级链接地址
                        'value': [code, a_tag.text()]
                    })

        # 获取二级地级市
        city_tool = CitySpider(encoding=self.encoding, headers=self.headers, provinces=provinces, excel_tool=self.excel_tool,
                               is_multi_thread=self.is_multi_thread, thread_num=self.thread_num, sleep=self.sleep)

        if self.is_multi_thread:
            city_tool.multi_thread()
        else:
            city_tool.one_thread()

        return provinces
