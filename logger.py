# -*- coding:utf-8 -*-
import logging.config
import os


class Logger:
    """
    日志类
    """
    @staticmethod
    def init_log(log_path, log_file):
        """
        初始化日志
        :param log_path: 日志目录
        :param log_file: 日志文件名
        :return:
        """
        # 定义日志输出格式 开始

        standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                          '[%(levelname)s][%(message)s]'  # 其中name为getlogger指定的名字


        # 如果不存在定义的日志目录就创建一个
        if not os.path.isdir(log_path):
            os.mkdir(log_path)

        # log文件的全路径
        log_file = os.path.join(log_path, log_file)


        # log配置字典
        LOGGING_DIC = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': standard_format
                }
            },
            'filters': {},
            'handlers': {
                # 打印到终端的日志
                'console': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',  # 打印到屏幕
                    'formatter': 'standard'
                },
                # 打印到文件的日志,收集info及以上的日志
                'default': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
                    'formatter': 'standard',
                    'filename': log_file,  # 日志文件
                    'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                    'backupCount': 10,
                    'encoding': 'utf-8',  # 日志文件的编码，再也不用担心中文log乱码了
                },
            },
            'loggers': {
                # logging.getLogger(__name__)拿到的logger配置
                '': {
                    'handlers': ['default'],
                    'level': 'DEBUG',
                    'propagate': True,  # 向上（更高level的logger）传递
                },
            },
        }

        # 导入上面定义的logging配置
        logging.config.dictConfig(LOGGING_DIC)

    @staticmethod
    def get_logger(log_name):
        """
        返回一个log对像
        :return:
        """
        return logging.getLogger(log_name)
