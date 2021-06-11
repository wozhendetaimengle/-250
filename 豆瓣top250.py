import re
from bs4 import BeautifulSoup as BS
import urllib
import xlwt
import sqlite3

if __name__ == "__main__":

    findlink = re.compile(r'<a href="(.*)">')
    findtitle = re.compile(r'<span class="title">(.*?)</span>', re.S)
    findimg = re.compile(r'<img.*src="(.*?)"', re.S)  # re.s 让换行符包含在字符中
    findrating = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
    findjudge = re.compile(r'<span>(.*?)</span>')


    def main():
        baseurl = 'https://movie.douban.com/top250?start='
        # 1、爬取网页
        init_豆瓣()
        datalist = getData(baseurl)
        # savepath = './/豆瓣top250.xls'
        print('get over')
        dbpath = '豆瓣.db'
        saveData_into_database(datalist, dbpath)


    def getData(baseurl):
        datalist = []
        # 2、解析
        for i in range(0, 10):
            url = baseurl + str(i * 25)
            html = ask_url(url)
            # 2\逐一解析
            soup = BS(html, 'html.parser')
            for item in soup.find_all('div', class_='item'):
                data = []
                item = str(item)
                link = re.findall(findlink, item)[0]
                #                 print(link)
                data.append(link)
                title = re.findall(findtitle, item)  # 招到的第一个元素
                #                 print(title)
                if (len(title) == 2):
                    cn_title = title[0]
                    data.append(cn_title)  # 添加中文名
                    other_title = title[1].replace('/', '')
                    data.append(other_title)  # 外国名
                else:
                    data.append(title[0])
                    data.append('')  # 外文名为空
                rating = re.findall(findrating, item)[0]
                #                 print(rating)
                data.append(rating)
                judge = re.findall(findjudge, item)[0]
                #                 print(judge)
                data.append(judge)
                img = re.findall(findimg, item)
                #                 print(img)
                data.append(img)

                datalist.append(data)
                # print(datalist[26])
                # break
            print('爬取第%d页' % (i + 1))
        return datalist


    def saveData_into_excel(datalist, savepath):
        book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建对象
        sheet = book.add_sheet("豆瓣电影top250", cell_overwrite_ok=True)
        col = ('电影链接', '中文名', '外文名', '评分', '评价人数', '图片链接')
        for i in range(6):
            sheet.write(0, i, col[i])  # 列名
        for i in range(250):
            print('保存第%d条' % (i + 1))
            data = datalist[i]
            for j in range(6):
                sheet.write(i + 1, j, data[j])
        book.save(savepath)
        ####################################数据存放到sql


    def saveData_into_database(datalist, dbpath):
        init_top250(dbpath)
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()  # 游标

        for i in range(250):
            data = datalist[i]
            for index in range(len(data)):
                if index == 3:
                    print(data[index])
                    continue
                else:
                    print(data[index])
                    data[index] = '"' + str(data[index]) + '"'
            sql = '''
                insert into top250(电影链接, 中文名, 外文名, 评分, 评价人数, 图片链接)
                values(%s)''' % ','.join(data)
            print('保存好第%d条')
            cursor.execute(sql)
            conn.commit()
        conn.close()


    def init_豆瓣():
        conn = sqlite3.connect('./豆瓣.db')
        print("open database successfully")


    def init_top250(dbpath):
        conn = sqlite3.connect(dbpath)
        print("open database successfully")

        c = conn.cursor()  # 获取游标
        sql = '''
                create table Top250
                    (
                    id integer primary key autoincrement,
                    电影链接 text,
                    中文名 text,
                    外文名 text,
                    评分 integer,
                    评价人数 text,
                    图片链接 text
                  )  
            '''
        c.execute(sql)  # 执行sql
        conn.commit()  # 提交数据
        conn.close()

        print('建表成功')


    def ask_url(url):
        head = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62"
        }
        # 模拟浏览器头部信息
        request = urllib.request.Request(url, headers=head)
        html = ''
        try:
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf-8')
        #             print(html)
        except urllib.error.URLError as e:
            # if hasattr(e,'code'):
            #     print(e,code)
            # if hasattr(e,'reason'):
            #     print(e,reason)
            pass
        return html


    main()
