#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: logtool.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2020-11-02 15:10:19

Description: 配置logger
"""

import logging
import logging.handlers
import os


def setupLogging(conf):
    """
    Initialize the logging module settings
    :param conf: dict, Initialize parameters
    :return: logger
    """
    level = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    console = conf['console']  # console output
    console_level = conf['console_level']  # choose console log level to print
    file = conf['file']  # local log file output
    file_level = conf['file_level']  # choose log file level to save
    logfile = conf['log_file']  # local log file save position
    backup_count = conf['backup_count']  # count of local log files
    max_size = conf['max_size']  # size of each local log file
    format_string = conf['format_string']  # log message format

    logger = logging.getLogger('OPC2UDP')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')

    if file:
        # 如果 log 文本不存在，创建文本
        dir_path = os.path.dirname(logfile)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # 实例化一个 rotate file 的处理器，让日志文件旋转生成
        fh = logging.handlers.RotatingFileHandler(filename=logfile,
                                                  mode='a',
                                                  maxBytes=max_size,
                                                  backupCount=backup_count,
                                                  encoding='utf-8')
        fh.setLevel(level[file_level])
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if console:
        # 实例化一个流式处理器，将日志输出到终端
        ch = logging.StreamHandler()
        ch.setLevel(level[console_level])
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
