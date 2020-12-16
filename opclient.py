#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: opclient.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2020-10-26 14:13:11

Description: 适用于Windows(DCOM)/Linux(Open)的OPC客户端

# TODO:  <10-12-20> #
1. 计划支持Linux + Python3（当前Windows支持正常，Linux只支持Python2）
"""

import argparse
import json
import os
import platform
import socket
import time

import OpenOPC
import toml

from utils.log_wrapper import setupLogging

_version = 0.4

system = platform.system()


class OPC2UDP(object):
    """OPC Server --> {data} --> UDP Client"""
    def __init__(self, conf):
        """init

        :conf: configuration, dict

        """
        # OPC configuration
        opc_conf = conf.get('opc', dict())
        self.opc_server_host = opc_conf.get('opc_server_host', 'localhost')
        self.opc_server_port = opc_conf.get('opc_server_port', 7766)
        self.opc_server_name = opc_conf.get('opc_server_name', None)
        self.opc_tag_list = opc_conf.get('opc_tag_list', list())
        self.opc_tag_id = opc_conf.get('opc_tag_id', 2)
        self.opc_get_way = opc_conf.get('opc_get_way', 'iproperties')

        # UDP configuration
        udp_conf = conf.get('udp', dict())
        self.udp_client_host = udp_conf.get('udp_client_host', '127.0.0.1')
        self.udp_client_port = udp_conf.get('udp_client_port', 8090)

        # sleep parameter
        self.sleep = conf.get('sleep', 1)

        self.logger = setupLogging(conf['log'])

        # Create OPC Client
        self.opc = None
        self._opc_client()

    def _opc_client(self):
        """Create OPC client"""
        if system == 'Linux':
            self.opc = OpenOPC.open_client(self.opc_server_host,
                                           self.opc_server_port)
            self.opc.connect(opc_server=self.opc_server_name)
        elif system == 'Windows':
            try:
                self.opc = OpenOPC.client()
                self.opc.connect(opc_server=self.opc_server_name,
                                 opc_host=self.opc_server_host)
            except Exception as e:
                raise e

        self.logger.info('OPC client created successfully')

    def _udp_client(self):
        """Create UDP client"""
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger.info('UDP client created successfully')

        return udp

    def get_server_info(self):
        """Get a list of available OPC Servers
        :returns: list

        [
            'Matrikon.OPC.Simulation.1',
            'Kepware.KEPServerEX.V4',
            ... ...
        ]
        """
        servers_list = list()

        if self.opc:
            try:
                servers_list = self.opc.servers()
            except Exception as e:
                self.logger.error(e)
        else:
            self.logger.error('Not connected to OPC Server')

        return servers_list

    def get_opc_info(self):
        """Retrieving OPC server information
        :returns: list

        [
            ('Host', 'localhost'),
            ('Server', 'Matrikon.OPC.Simulation'),
            ('State', 'Running'),
            ('Version', '1.1 (Build 307)'),
            ... ...
        ]
        """
        servers_info = list()

        if self.opc:
            try:
                servers_info = self.opc.info()
            except Exception as e:
                self.logger.error(e)
        else:
            self.logger.error('Not connected to OPC Server')

        return servers_info

    def get_data(self):
        """Get data from OPC Server
        :returns: {tag: value}

        """
        datas = dict()

        if self.opc:
            try:
                if self.opc_get_way == 'iproperties':
                    # iproperties()
                    values = self.opc.iproperties(tags=self.opc_tag_list,
                                                  id=self.opc_tag_id)
                    datas = dict(
                        zip(self.opc_tag_list, [value[1] for value in values]))
                elif self.opc_get_way == 'iread':
                    # iread
                    values = self.opc.iread(tags=self.opc_tag_list)
                    datas = dict(
                        zip(self.opc_tag_list, [value[0] for value in values]))
                else:
                    self.logger.error('Error get way: {}'.format(
                        self.opc_get_way))
            except Exception as e:
                raise e
        else:
            self.logger.error('Not connected to OPC Server')

        return datas

    def udp_send(self):
        """Send data via UDP"""
        udp = self._udp_client()
        while True:
            data = self.get_data()
            self.logger.info('Get data: {}'.format(data))
            data_jsonb = json.dumps(data).encode('utf-8')
            udp.sendto(data_jsonb,
                       (self.udp_client_host, self.udp_client_port))
            self.logger.info('Send data via UDP({}:{})'.format(
                self.udp_client_host, self.udp_client_port))

            time.sleep(self.sleep)


if __name__ == "__main__":
    # 构建默认配置文件路径
    name = os.path.basename(__file__).split('.')[0]  # 文件名
    ext = 'toml'  # 配置文件后缀
    filename = '{name}.{ext}'.format(name=name, ext=ext)  # 完整配置文件名

    # 定义参数范围
    # parser是正常参数，group是互斥参数
    parser = argparse.ArgumentParser(prog='opclient',
                                     description='An Open OPC Client')
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('-c',
                        '--config',
                        help=('Specify configuration file, '
                              'default is {}').format(filename))
    group.add_argument('-i',
                       '--info',
                       action='store_true',
                       help='Get OPC information')
    group.add_argument('-l',
                       '--list',
                       action='store_true',
                       help='Get a list of available OPC Servers')
    group.add_argument('-d',
                       '--data',
                       action='store_true',
                       help=('Get data from OPC Server.'
                             ' (Does not support Linux temporarily)'))
    group.add_argument('-u',
                       '--udp',
                       action='store_true',
                       help=('Get data from OPC Server and forward it via UDP.'
                             ' (Does not support Linux temporarily)'))
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        default=None,
                        version='%(prog)s {}'.format(_version))

    # 获取参数列表
    args = parser.parse_args()

    # 尝试获取配置信息
    confile = args.config if args.config else os.path.join(
        '.{}conf{}'.format(os.sep, os.sep), filename)
    conf = toml.load(confile)

    # 根据参数判断是否创建OPC2UDP对象
    if True in [args.info, args.list, args.data, args.udp]:
        opc2udp = OPC2UDP(conf)

    # 不同参数对应的操作
    if args.info:  # -i. --info
        opc_info = opc2udp.get_opc_info()
        print('OPC info: {}'.format(opc_info))
    elif args.list:  # -l. --list
        servers_list = opc2udp.get_server_info()
        print('Available OPC Server: {}'.format(servers_list))
    elif args.data:  # -d, --data
        data = opc2udp.get_data()
        print('Get data: {}'.format(data))
    elif args.udp:  # -u, --udp
        opc2udp.udp_send()
