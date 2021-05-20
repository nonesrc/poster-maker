"""
海报生成中台服务
"""
from flask import Flask, send_file, request
from service.posterMaker import PosterMaker, PosterDto
from io import BytesIO

app = Flask(__name__)

@app.route('/make')
def makePoster():
    dto = PosterDto()
    dto.title = '正宗成都双流橘子12元一斤优惠卖'
    dto.price = 20
    dto.goodsType = 1
    dto.goodsId = 2
    dto.fromUid = 210412001
    dto.imgUrl = "https://img13.360buyimg.com/n7/jfs/t1/133814/24/5163/135204/5f1905e7E09c127cc/f674c331bc1f8191.jpg"
    postMaker = PosterMaker(dto)
    img_data = postMaker.crate()
    return send_file(BytesIO(img_data),
                     attachment_filename='logo.jpg',
                     mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=7002)
