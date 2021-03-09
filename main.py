# -*- coding: UTF-8 -*-
import atexit
import datetime
import os

from source.area.ProvinceSpider import ProvinceSpider
from source.area.WriteExcel import WriteExcel


class Main(object):

    def __init__(self, province_code: list = None, year: str = '2020', encoding: str = 'gb2312', file_name: str = ""):
        """
        :param province_code: 统计汇总识别码-划分代码 为空时爬取全国一级：省、直辖市、自治区
        :param year: 更改年份只需要更改这里即可
        :param encoding: 编码
        :param file_name: excel文件名
        """

        self.headers = [
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'www.stats.gov.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
                              'Safari/537.36'
            },
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'www.stats.gov.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
                              'Safari/537.36'
            },
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'www.stats.gov.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
                              'Safari/537.36'
            },
        ]

        self.domain_url = f'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/{year}/index.html'
        self.province_code = province_code
        self.year = year
        self.encoding = encoding
        stem, suffix = os.path.splitext(file_name)
        self.file_name = f"{stem}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{suffix}"

        # 写入excel
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'result', self.file_name)
        self.excel_tool = WriteExcel(file_path=file_path)

        # 注册退出事件
        atexit.register(self.save)

    def run(self):
        # 获取5级政区域数据
        province_tool = ProvinceSpider(
            province_code=self.province_code, domain_url=self.domain_url, encoding=self.encoding, headers=self.headers,
            sleep=3, excel_tool=self.excel_tool, is_multi_thread=True, thread_num=3
        )
        province_tool.start_requests()

    def save(self):
        self.excel_tool.save()


if __name__ == '__main__':
    file_name = "行政村统计数据.xlsx"
    province_code_list = ["15", ]
    main = Main(province_code=province_code_list, file_name=file_name, year="2020")
    main.run()
