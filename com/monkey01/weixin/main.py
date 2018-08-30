# coding: utf8
import spider_weixun_by_sogou


if __name__ == '__main__':

    gongzhonghao = raw_input(u'input weixin gongzhonghao:')
    if not gongzhonghao:
        gongzhonghao = 'spider'
    text = " ".join(spider_weixun_by_sogou.run(gongzhonghao))

    print text