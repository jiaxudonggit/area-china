# -*- coding: UTF-8 -*-
"""
@description 写入excel
@author jxd
"""
import os

import openpyxl


class WriteExcel(object):

    def __init__(self, file_path: str):
        """
        :param file_path: 文件名
        """

        # 表头
        self.HEADER = [
            "统计用区划代码",
            "名称",
            "统计用区划代码",
            "名称",
            "统计用区划代码",
            "名称",
            "统计用区划代码",
            "城乡分类代码",
            "名称",
        ]
        self.file_path = file_path

        if os.path.exists(self.file_path):
            self.workbook = openpyxl.load_workbook(self.file_path)
        else:
            self.workbook = openpyxl.Workbook()

    def create_sheet(self, name):
        """
        # 创建sheet
        :param name:
        :return:
        """
        # 创建sheet
        work_sheet = self.workbook.create_sheet(title=name)
        # 插入表头
        work_sheet.append(self.HEADER)

    def append_data(self, sheet_name: str, value: list):
        sheet = self.workbook[sheet_name]
        sheet.append(value)

    def save(self):
        # 判断文件目录是否存在， 不存在则创建
        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))

        # 保存到本地
        self.workbook.save(self.file_path)

