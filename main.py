# -*- coding: UTF-8 -*-
from source.area.ProvinceSpider import ProvinceSpider
from source.area.WriteExcel import WriteExcel


class Main(object):

    def __init__(self, province_code: str = None, year: str = '2020', encoding: str = 'gb2312'):
        """
        :param province_code: 统计汇总识别码-划分代码 为空时爬取全国一级：省、直辖市、自治区
        :param year: 更改年份只需要更改这里即可
        :param encoding: 编码
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

    def run(self):
        # 获取省、直辖市、自治区
        province_tool = ProvinceSpider(
            province_code=self.province_code, domain_url=self.domain_url,
            encoding=self.encoding, headers=self.headers, is_multi_thread=False
        )
        provinces = province_tool.start_requests()
        print(f"获取省、直辖市、自治区:{provinces}")

        # 写入excel
        excel_tool = WriteExcel(file_name="行政村统计数据.xlsx", data=provinces)
        excel_tool.write()


if __name__ == '__main__':
    province_code = '15'

    main = Main(province_code='15')

    main.run()
