# area-china

* 这是一个基于Python语言编写的爬虫项目，针对中国省市区以及镇、街道、村、居委会等共5级行政区域数据的获取并写入excel文件
* 级别
  * 一级：省、直辖市、自治区
  * 二级：地级市
  * 三级：市辖区、县（旗）、县级市、自治县（自治旗）、特区、林区
  * 四级：镇、乡、民族乡、县辖区、街道
  * 五级：村、居委会
* 本项目仅做学习交流用途

# 运行程序

* 依赖Python3环境
* 环境安装好后，建议直接导入项目到PyCharm中运行
* 推荐使用单线程爬取，虽然速度慢，但是不容易被反爬
* 运行项目根目录下main.py文件
* Mian类参数说明：

```python
"""
year: 要爬取的年份，默认2020
encoding: 编码，默认gb2312
province_code_list: 可爬取指定的一级行政区数据，为空时爬取全国一级行政区，否则爬取指定代码的一级行政区
is_multi_thread: 是否开启多线程爬取，推荐使用单线程爬取，虽然速度慢，但是不容易被反爬
thread_num: 线程数量，越小越不容易被反爬
sleep: 睡眠间隔时间，越大越不容易被反爬 单线程是推荐0.5-1之间
file_name: excel文件名，默认存储在项目根目录下的result文件夹内，使用时间做区分
"""
file_name = "行政村统计数据.xlsx"
province_code_list = ["15", ]
main = Main(province_code_list=province_code_list, file_name=file_name, year="2020", sleep=0.5)
main.run()
```