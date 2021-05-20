"""
    @Description 商品海报生成器
    @Time 2021/5/10 10:26
    @Author zuoweiyuan
"""
import qrcode
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import time
import requests

#海报所需展示信息
class PosterDto:

    goodsId = ''
    fromUid = ''
    price = ''
    title = ''
    goodsType = ''
    imgUrl = ''


class PosterMaker:

    #生成跳转URL
    def getRequestUrl(self):
        return 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx56e53ff5ed0b2046' \
               '&redirect_uri=http%3A%2F%2Fwww.hyppgy.com%2Flogin%3Fredirect%3D%2Fgoods%2F{}%26fromUser%3D{}' \
               '&response_type=code' \
               '&scope=snsapi_userinfo' \
               '&state=STATE&connect_redirect=1#wechat_redirect'.format(self.__goodsId, self.__fromUid)

    #商城商品海报生成类
    def makeQrcodeImg(self):
        """
        生成二维码图片数据
        :param data: 用于生成二维码的原数据
        :return: None
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        base_url = self.getRequestUrl()
        qr.add_data(base_url)
        qr.make(fit=True)
        img = qr.make_image()
        return img

    def countGbkLength(self, text):
        """
        计算GBK编码的字符串长度
        :param text: 待计算文本长度
        :return: 计算出来的长度
        """
        return len(text.encode('gbk'))

    def shortenText(self, text, maxLength):
        """
        缩短字符串，超出部分用...表示
        :param text: 待缩短的字符串
        :param maxLength: 最大允许长度
        :return: 缩短后的字符串
        """
        sizeList = list()
        for ch in text:
            sizeList.append(self.countGbkLength(ch))
        totalLength = self.countGbkLength(text)
        charNums = len(text)

        #统计总长度，进行文本显示的一个控制
        if totalLength > maxLength:
            charNums = 0
            cntLength = 0
            while cntLength <= maxLength:
                cntLength += sizeList[charNums]
                charNums += 1

        return text[0:charNums], charNums

    def getImgFromInternet(self, url):
        info = requests.get(url = url)
        imgData = info.content
        return Image.open(BytesIO(imgData))

    #构造函数
    def __init__(self, posterDto):
        self.__goodsId = posterDto.goodsId
        self.__fromUid = posterDto.fromUid
        self.__price = posterDto.price
        self.__goodsType = posterDto.goodsType
        self.__imgUrl = posterDto.imgUrl
        self.__title = posterDto.title

    def crate(self):
        """
        创建海报
        :return:
        """
        s1 = time.time()
        canvas = Image.new(mode="RGB", size=(300, 400), color="white")
        qrcodeImg = self.makeQrcodeImg()
        qrcodeImg = qrcodeImg.resize((120, 120), Image.ANTIALIAS)
        # goodsImg = Image.open('./grape.jpg')
        goodsImg = self.getImgFromInternet(self.__imgUrl)
        goodsImg = goodsImg.resize((300, 280), Image.ANTIALIAS)
        canvas.paste(qrcodeImg, box=(300 - 120, 386 - 100))
        canvas.paste(goodsImg, box=(0, 0))
        draw = ImageDraw.Draw(canvas)

        font = ImageFont.truetype(font='./resource/msyh.ttc', size=16)
        #先判断是否需要进行换行操作, 如果需要进行换行操作的话，获取每一行内的全部字符
        goodsTitle = self.__title
        totalSize = self.countGbkLength(goodsTitle)
        firstLineText = ''
        secondLineText = ''
        if totalSize > 18:
            #首先获取第一行内的文字信息
            firstLineText, nowPosition = self.shortenText(goodsTitle, 18)
            #获取第二行内的文字信息
            secondLineText, endPosition = self.shortenText(goodsTitle[nowPosition:-1], 15)
            #若不能显示所有的文字，则直接省略后面的文字，并且加上...
            if endPosition != len(goodsTitle[nowPosition:-1]) :
                secondLineText += '...'
        else:
            firstLineText = goodsTitle

        draw.text(xy=(10, 298), text=firstLineText, fill=(0, 0, 0), font=font)
        draw.text(xy=(10, 320), text=secondLineText, fill=(0, 0, 0), font=font)

        #进行商品实际价格的显示
        isPointGoods = self.__goodsType == 1
        font = ImageFont.truetype(font='./resource/msyh.ttc', size=25)
        if isPointGoods:
            pointIco = Image.open('./resource/pointIco.JPG')
            canvas.paste(pointIco, box=(8, 353))
            draw.text(xy=(41, 358), text= str(self.__price), fill=(7, 193, 96), font=font)
        else:
            draw.text(xy=(10, 358), text='￥' + self.__price, fill=(7, 193, 96), font=font)

        img_bytes = BytesIO()
        canvas.save(img_bytes, format='JPEG', dpi=(300.0,300.0), quality=95)
        s2 = time.time()
        print(s2 - s1)
        return img_bytes.getvalue()

