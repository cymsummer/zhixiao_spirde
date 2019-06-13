# -*- coding:utf-8 -*-
from logger import Logger
import requests, json, hashlib, os, time, random,configparser

from urllib.request import urlretrieve
from qiniu import Auth, put_file, etag, urlsafe_base64_encode


class Spirde():
    def __init__(self):
        """
        请求小程序的url
        Parameters:
            url：      地址
            post_url：请求数据添加的接口
        Returns：
            无
        """

        Logger.init_log('logs', 'worker.log')

        self.logger = Logger.get_logger(__name__)

        self.logger.info("日志加载完毕 \n")

        config = configparser.ConfigParser()

        config.read('config.ini')

        self.public_key=config.get('qiniuyun','public_key')

        self.private_key=config.get('qiniuyun','private_key')

        self.bucket=config.get('qiniuyun','bucket')

        self.img = config.get('img', 'img')

        self.url =config.get('sys','url')

        self.post_url = config.get('sys','post_url')

    def down_img(self, img_url, img_name):
        """
        图片下载
        :param img_url:
        :param img_name:
        :return:
        """

        # python图片下载
        photo_url = "http://img.supercr.top/" + img_name + ".jpg"

        # 校验图片是否存在
        response = requests.get(url=photo_url)

        if response.status_code != 200:

            # 如果目录不存在，就创建一下目录

            if not os.path.exists(self.img):
                os.makedirs(self.img)

            urlretrieve(img_url, self.img + "/" + img_name + ".jpg")

            # 文件上传
            img = self.up_img(self.img + "/" + img_name + ".jpg", img_name + ".jpg", )

            self.logger.info('ucloud图片地址： %s \n' % img)

            return img

        else:

            self.logger.info('ucloud图片地址已存在： %s \n' % img_url)

    def up_img(self, img_url, img_name):
        """
        图片上传
        Parameters:
            img_url:图片地址
            img_name:图片名称
        :return:
        """

        access_key = self.public_key
        secret_key = self.private_key

        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 要上传的空间
        bucket_name = self.bucket

        # 上传到七牛后保存的文件名
        key = "zx/" + img_name

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600)

        # 要上传文件的本地路径
        # video_url = 'C:/Users/rwcym/Desktop/农村小鹏777/6572143556763323661-这么小就能看出，以后肯定有出息，这吃相没谁了！.mp4'

        ret, info = put_file(token, key, img_url)

        # 七牛云的url
        qny_name = "http://img.supercr.top/" + ret['key']

        self.logger.info('七牛云上传完毕 %s \n' % qny_name)

        return qny_name

    def deal_data(self, new_info):
        """
        核心数据处理
        Parameters:
            new_info:获取的json数据

        :return:
        """
        data = {}

        # 小程序标题
        data["program_title"] = new_info['name']

        # 小程序作者
        data["program_user_name"] = new_info['created_by']

        # 小程序简介
        data["program_desc"] = new_info["description"]

        # 小程序类型
        if (new_info["tag"][0]["name"] == "游戏"):
            data["program_style"] = "2"
        else:
            data["program_style"] = "1"

        # 小程序icon

        # 请求七牛云进行数据存储 img_url img_name

        icon = self.down_img(new_info["icon"]["image"], self.md5_name(new_info["icon"]["image"]))

        data["program_icon"] = icon

        # 小程序二维码
        qrcode = self.down_img(new_info["qrcode"]["image"], self.md5_name(new_info["qrcode"]["image"]))

        data["program_qrcode"] = qrcode

        content_img = ""

        # 小程序内容图片
        for index in range(len(new_info["screenshot"])):
            img = self.down_img(new_info["screenshot"][index]["image"],
                                self.md5_name(new_info["screenshot"][index]["image"]))

            content_img += img + ","

        end = content_img.rfind(',')  # 结束位置

        data["program_pic"] = content_img[:end]

        # 小程序标签
        tag = ""

        for index in range(len(new_info['tag'])):
            tag += new_info['tag'][index]['name'] + ","

        end = tag.rfind(',')  # 结束位置

        tag = tag[:end]

        #小程序id
        data['zx_id']=new_info['id']

        return data, tag

    def md5_name(self, name):
        """
            对图片地址进行md5加密
        Parameters:
            name:请求的名称
        :return:
        """

        title = hashlib.md5()
        title.update(name.encode(encoding="utf-8"))
        title = title.hexdigest()

        return title

    def get_type(self, offset, limit):
        """
        全量更新数据
        :param offset:页码
        :param limit:每页显示条数
        :return:
        """
        while True:
            url = self.url + "/?tag=&offset=%s&limit=%s" % (offset, limit)

            return_info = requests.get(url)

            # 请求数据判断页码
            html = return_info.text

            info = json.loads(html)

            # 请求总数
            zx_num = offset + limit

            # 总条数
            total = info['meta']['total_count']

            if (total >= zx_num):
                try:
                    #处理数据
                    self.get_content(info)
                except Exception as ex:
                    self.logger.error(ex)
            else:
                return
            offset += 20

    def get_url(self, type, offset, limit):
        """
         爬墙方式
        :param type: 1：检查更新 2：全量更新
        :param offset:页码
        :param limit:每页显示条数
        :return:
        """

        if (type == 1):
            url = self.url + "/?tag=&offset=%s&limit=%s" % (offset, limit)

            return_info = requests.get(url)

            # 请求数据判断页码
            html = return_info.text

            info = json.loads(html)

            # 处理数据
            self.get_content(info)

            # 更新最近内容模式
            self.logger.info("当前是【更新最近内容】模式")
        elif (type == 2):
            self.get_type(offset, limit)
            # 更新全部内容模式
            self.logger.info("当前是【全量更新】模式")
        else:
            # 更新全部内容模式
            self.logger.info("当前是【bug】模式")

    def get_content(self, info):
        """
        接口请求
        Parameters:
            html: 获取的页面json数据
            data:组装的数据
        Returns：
        无
        :return:
        """

        for index in range(len(info['objects'])):
            new_info = info['objects'][index]
            # 数据处理
            data = self.deal_data(new_info)

            # 小程序信息
            new_json = json.dumps(data[0])

            # 标签信息
            tag = data[1]

            # 回调
            r = requests.post(self.post_url, data={"data": new_json, "tag": tag})

            self.logger.info('\n 完成回发数据,返回结果 \n %s \n' % r.text)

            time.sleep(random.uniform(0.8, 3.2))


if __name__ == '__main__':
    spiede = Spirde()

    info = spiede.get_url(1, 0, 2)
