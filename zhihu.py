import requests
import get_data
import time
import datetime
import random
import math
import locale
import re
import json
import pymysql

id = 0
date = ''
title = ''
ans_link = ''
looked = 0
followers = 0
totals = 1 # 获取当下话题的总回答数
rank = 1 # 小鹿回答的排名，初始化为第1名，每次爬取完一个时需要再次初始化

final_data = [] # 最终数据
comment = [] # 用来存放数据
comments = [] # 用来存放数据
flag = 0 # 爬取小鹿排名时，需要flag来判断是否抓取到了小鹿的回答

today = datetime.datetime.today().strftime('%Y_%m_%d')

# 创建一个数据库表来保存信息
## 连接数据库
def mysql_conn():
    conn = pymysql.connect(
        host = "localhost",
        port = 3306,
        user = "root",
        passwd = "izhiqundata",
        db="izhiqunDB",
        charset = "utf8"
    )
    return conn

## 建表
def create_table():
    create_sql = f'''
    CREATE TABLE `探长{today}`(
    id INT,
    编辑时间 VARCHAR(255),
    话题名称 VARCHAR(255),
    回答链接 VARCHAR(255),
    话题浏览量 INT,
    话题关注量 INT,
    回答总数 INT,
    当前排名 INT,
    PRIMARY KEY (`话题名称`)
    )ENGINE=INNODB DEFAULT CHARSET =utf8
    '''
    conn = mysql_conn()
    cursor = conn.cursor()
    cursor.execute(create_sql)
    conn.commit()
    conn.close()

## 插入记录
def insert(item):
    sql = f"insert ignore `探长{today}`(id, 编辑时间, 话题名称, 回答链接, 话题浏览量, 话题关注量, 回答总数, 当前排名) " \
          "values (%s, %s, %s, %s, %s, %s, %s, %s)"
    params = (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7])
    conn = mysql_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        cursor.connection.commit()

    except BaseException as e:
        print(u"错误在这里>>>>", e, u"<<<<错误在这里")

    conn.commit()
    conn.close()

# 获取话题下回答者的用户信息，顺便获得排名，可以和parse_ansajax()函数合在一起，但是太混乱了所以拆开并用了全局变量来处理
def get_user_data(html_ans_json):

    global id
    global rank
    global flag
    global comment
    global comments
    flag = 0
    comments = []

    json_data = json.loads(html_ans_json)['data']
    #print(json_data)

    for item in json_data:
        comment = []
        comment_tanzhang = []  # 判断是否循环到了探长，如果判定是探长，则停止循环并且返回rank
        comment_tanzhang.append(item['author']['url_token'])  # 姓名，找中文名字容易出现乱码，所以使用url的信息
        comment_tanzhang.append(item['author']['name'])
        # comment.append(item['author']['gender'])  # 性别
        # comment.append(item['author']['url'])     # 个人主页
        # comment.append(item['voteup_count'])  # 点赞数
        # comment.append(item['comment_count'])  # 评论数
        # comment.append(item['url'])               # 回答链接
        # comments.append(comment)
        print(comment_tanzhang[0], comment_tanzhang[1])
        if comment_tanzhang[0] == "sujiankuan" or comment_tanzhang[1] == "探长" or comment_tanzhang[1] == "æ�¢é•¿" or rank > 99:  # 如果小鹿回答的排名掉出100名以外变直接返回rank=100
            flag = 1
            id = id + 1

            comment.append(id)
            comment.append(date)
            comment.append(title)
            comment.append(ans_link)
            comment.append(looked)
            comment.append(followers)
            comment.append(totals)
            comment.append(rank)
            comments.append(comment)
            print(comments)
            break
        else:
            rank += 1

    return comments


# 获得从【探长的回答界面】进入的探长的话题回答中的json数据，主要是获得next的json
def parse_ansajax(ans_json):

    global totals
    global rank
    global final_data
    global comment
    global comments
    global id

    print('====' * 30)

    html_ans_json = get_data.get_data(ans_json)

    #######################用来判断处理网页不返回请求信息#######################
    if isinstance(html_ans_json, str) != True:
        print("giao 这一条拒绝了我的访问1 giao")

        comment = []
        comments = []
        id = id + 1
        comment.append(id)
        comment.append(date)
        comment.append(title)
        comment.append(ans_link)
        comment.append(looked)
        comment.append(followers)
        comment.append(totals)
        comment.append('')  # 有多少个其他变量（除了title和ans_link）就要多少个这个命令来占位
        comments.append(comment)
        final_data.extend(comments)
        print(comments)
        return
    ######################################################################

    totals = json.loads(html_ans_json)['paging']['totals']
    print(f"当下回答总数数量：{totals}")

    rank = 1  # 重新初始化rank
    ans_page = 0

    while (ans_page <= totals):  # 遍历某话题下的每一条回答(用来获取回答者信息)(第二层循环)

        print("现在是多少页了：" + str(ans_page))
        html_ans_json_next = get_data.get_data(ans_json)

        #######################用来判断处理网页不返回请求信息#######################
        if isinstance(html_ans_json_next, str) != True:

            print("giao 这一条拒绝了我的访问2 giao")

            comment = []
            comments = []
            id = id + 1
            comment.append(id)
            comment.append(date)
            comment.append(title)
            comment.append(ans_link)
            comment.append(looked)
            comment.append(followers)
            comment.append(totals)
            comment.append('') # 有多少个其他变量（除了title和ans_link）就要多少个这个命令来占位
            comments.append(comment)
            final_data.extend(comments)
            print(comments)
            return
        ######################################################################

        commentsss = get_user_data(html_ans_json_next)  # 获取探长的用户的信息，以及回答的rank

        ans_page += 5          #话题下面每个问题打开自动会加载5条回答

        if (flag != 0): # 如果已经抓取到了探长的排名，跳出函数
            break

        ans_json = json.loads(html_ans_json_next)['paging']['next']  # 获取某一个话题中的下一页回答（ps：每一页有5个回答，即offset=0，5，10...）

    ################################################
    # 没有抓取到探长，意味着本条信息有问题，比如回答侵权被下架，或者被拒绝了请求，那么就跳出循环开始下一个回答的抓取
    if (flag == 0):
        id = id + 1
        # print(rank)
        comment = []
        commentsss = []
        comment.append(id)
        comment.append(date)
        comment.append(title)
        comment.append(ans_link)
        comment.append(looked)
        comment.append(followers)
        comment.append(totals)
        comment.append(-1)
        commentsss.append(comment)
        print(commentsss)
    ################################################

    final_data.extend(commentsss)  # 将所有获得的数据输入一个数组中

    return


# 获得从【探长的回答界面】进入的探长的话题回答中的直观数据：编辑日期、关注人数、浏览量
def parse_anslink(ans_link):

    global date
    global looked
    global followers

    # 转化 str型且含有逗号 的数字为int型
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    ########### 请求过于频繁可能会遇到【('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))】这个问题，忽略掉 ###########
    try:
        # 获取话题的关注人数,浏览量和编辑日期
        html_ans_link = get_data.get_data(ans_link)

        date = re.findall('<span data-tooltip="(.*?)</span></a></div></div>', html_ans_link)[0].replace('">', ' > ')
        followers = locale.atoi(re.findall('关注者</div><strong class="NumberBoard-itemValue" title="(.*?)"', html_ans_link)[0])
        looked = locale.atoi(re.findall('被浏览</div><strong class="NumberBoard-itemValue" title="(.*?)"', html_ans_link)[0])

    except requests.exceptions.ConnectionResetError:
        print(ans_link)
        print('Handle Exception1')

    except requests.exceptions.ConnectionError:
        print(ans_link)
        print('Handle Exception2')

    return


# 获取【探长的回答界面】中的最基本信息：回答名称、回答链接、回答中的json
def get_answer(text):

    global title
    global ans_link

    result_list = re.findall('\{"suggestEdit":.*?"question","id":.*?\}', text)

    for data in result_list:

        title = re.findall('"title":"(.*?)"', data)[1]  # 回答话题名称
        link_id1 = re.findall('"type":"question","id":(.*?)\}', data)[0]
        link_id2 = re.findall('"id":(.*?),', data)[0]

        #ques_link = 'https://www.zhihu.com/question/' + link_id1  # 话题总链接

        # 获得探长的回答链接
        ans_link = 'https://www.zhihu.com/question/' + link_id1 + '/answer/' + link_id2

        # 获得探长回答的话题的json
        # 知乎页面有时候会改后面的limit=5&offset=0&platform=desktop&sort_by=default，有时候会将limit改成3，一直用5就好，limit=5的json中的[pagging][next]中也是limit=5
        ans_json = 'https://www.zhihu.com/api/v4/questions/' + str(link_id1) + \
                    '/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bsettings.table_of_content.enabled%3B&limit=5&offset=0&platform=desktop&sort_by=default'

        # 分析探长的回答链接
        parse_anslink(ans_link)

        # 分析探长的ajax的回答链接
        parse_ansajax(ans_json)


def ans_tanzhang(page):
    print(f"======知乎关注的问题爬取第{page}页======")

    # 1、确定数据所在的url地址
    link = 'https://www.zhihu.com/people/sujiankuan/answers?page={}'.format(str(page))

    # 2、发送url地址对应的请求（你要的数据/不要的数据）
    html_data = get_data.get_data(link)  # 返回的就是response.text

    # 3、解析你要的数据（不要的数据排查出去）
    ## {"author":{"avatarUrlTemplate":"https:\u002F\u002Fpic1.zhimg.com\u002F85d2fe422c461502ced66225564ab9f4.jpg?source=c8b7c179","badge":[],"name":"apin","url":"http:\u002F\u002Fwww.zhihu.com\u002Fapi\u002Fv4\u002Fpeople\u002Fbc51b4f9dcb0d1a2c7bc45264f487d36","gender":1,"userType":"people","urlToken":"apin","isAdvertiser":false,"avatarUrl":"https:\u002F\u002Fpic4.zhimg.com\u002F85d2fe422c461502ced66225564ab9f4_l.jpg?source=c8b7c179","isOrg":false,"headline":"产品设计师","type":"people","id":"bc51b4f9dcb0d1a2c7bc45264f487d36"},"url":"http:\u002F\u002Fwww.zhihu.com\u002Fapi\u002Fv4\u002Fquestions\u002F19932946","title":"对于“无UI是UI设计的最高境界”这句话你怎么看？","answerCount":44,"created":1322297069,"questionType":"normal","followerCount":112,"updatedTime":1322297069,"type":"question","id":19932946}
    get_answer(html_data)

    ## 循环小鹿的回答，每一页中含有20条小鹿的回答
    answer_totals = re.findall('<meta itemProp="zhihu:answerCount" content="(.*?)"', html_data)[0]  # 探长的回答总数量
    answer_totals = locale.atoi(answer_totals)
    if math.ceil(answer_totals / 20) != page:
        print("第" + str(page) + "页数据爬取完毕！")
        page += 1
        time.sleep(random.randint(4, 8))
        ans_tanzhang(page)
    else:

    # 4、数据保存，此时直接使用final_data即可，因为是全局变量，而且已经在get_final_data中已经获得到了数据
        create_table()
        for info in final_data:
            insert(info)
        print("所有数据爬取完毕！")

    return