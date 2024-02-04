# -*- coding: UTF-8 -*-
import atexit
import datetime
import os

from source.area.ProvinceSpider import ProvinceSpider
from source.area.WriteExcel import WriteExcel


class Main(object):

    def __init__(self, province_code_list: list = None, year: str = '2020', encoding: str = 'gb2312', file_name: str = "",
                 sleep: float = 1, is_multi_thread: bool = False, thread_num: int = 3):
        """
        :param province_code_list: 统计汇总识别码-划分代码 为空时爬取全国一级：省、直辖市、自治区
        :param year: 更改年份只需要更改这里即可
        :param encoding: 编码
        :param file_name: excel文件名
        """

        # 请求头 可添加不同的请求头
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

        # 2024-02-04 地址由 http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/{year}/index.html 变更为 https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/{year}/index.html
        self.domain_url = f'https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/{year}/index.html'
        self.province_code_list = province_code_list
        self.year = year
        self.encoding = encoding
        self.sleep = sleep
        self.is_multi_thread = is_multi_thread
        self.thread_num = thread_num
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
            province_code_list=self.province_code_list, domain_url=self.domain_url, encoding=self.encoding, headers=self.headers,
            sleep=self.sleep, excel_tool=self.excel_tool, is_multi_thread=self.is_multi_thread, thread_num=self.thread_num
        )
        province_tool.start_requests()

    def save(self):
        self.excel_tool.save()


if __name__ == '__main__':
    """
    year: 要爬取的年份，默认2020
    encoding: 编码，默认gb2312
    province_code_list: 可爬取指定的一级行政区数据，为空时爬取全国一级行政区，否则爬取指定代码的一级行政区
    is_multi_thread: 是否开启多线程爬取，推荐使用单线程爬取，虽然速度慢，但是不容易被反爬
    thread_num: 线程数量，越小越不容易被反爬
    sleep: 睡眠间隔时间，越大越不容易被反爬 单线程是推荐0.5-1之间
    file_name: excel文件名，默认存储在项目根目录下的result文件夹内，使用时间做区分
    """
    file_name = "行政统计数据.xlsx"
    _province_code_list = []
    main = Main(province_code_list=_province_code_list, file_name=file_name, year="2023", sleep=1, is_multi_thread=True, thread_num=8, encoding='utf-8')
    main.run()
