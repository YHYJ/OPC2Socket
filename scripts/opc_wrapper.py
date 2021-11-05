#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: opc_wrapper.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-11-05 08:58:28

Description: 打包OpenOPC包自带的命令`opc`的包装器，在无法部署OPC2Socket的情况下测试用
"""

import subprocess
import time
from collections import Iterable


def wrapper(server_name: str, tag_list: list):
    """OpenOPC包自带命令`opc`的包装

    :server_name: OPC Server名
    :tag_list: OPC Server中的ITEM ID，即所要采集的通道名列表
    :returns: 生成器，OPC Server的解码后的返回数据

    """
    tags = ' '.join(tag_list)
    command = 'opc -s {server} {tag}'.format(server=server_name, tag=tags)

    while True:
        try:
            ores = subprocess.check_output(command)
            res = ores.decode('UTF-8')
            yield res
            time.sleep(1)
        except Exception as e:
            raise e


if __name__ == "__main__":
    server = 'OPC.Server.name'
    tags = ['Group_1.Tag_1']
    gen = wrapper(server_name=server, tag_list=tags)
    if isinstance(gen, (Iterable)):
        for res in gen:
            print(res)
