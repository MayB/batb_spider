#-*- encoding:utf-8 -*-
import urllib
import urllib2
import re
import MySQLdb

#帮助类
class Tool:
    #删除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n  ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        return x.strip()


#百度贴吧类
class bdtb:
    #构造函数，传入baseUrl和seeLz确定是否查看楼主
    def __init__(self, baseUrl, seeLz):
        self.baseUrl = baseUrl
        self.seeLz = '?see_lz=' + str(seeLz)
        self.tool = Tool()
        self.file = None
        self.floor = 1
        self.conn = MySQLdb.connect('localhost','root','root','mysql',144654)
    #获取某一个页面的数据
    def getPage(self, page):
        try:
            url = self.baseUrl + self.seeLz + '&pn=' + str(page)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            #print response.read()
            return response.read()
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"链接百度失败，失败原因", e.reason
                return None
    #获取标题
    def getTitle(self, page):
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
        result = re.search(pattern,page)
        if result:
            return result.group(1).strip()
        else:
            return None
    #获取总页数 
    def getPageNum(self, page):
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>',re.S)
        result = re.search(pattern,page)
        if result:
            print result.group(1)
            return result.group(1).strip()
        else:
            return None
    #获取每层楼内容
    def getContent(self,page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        results = re.findall(pattern,page)
        contents = []
        for result in results:
            content = "\n" + self.tool.replace(result) + "\n"
            contents.append(content)
        return contents
    #设置文件名
    def setFileTitle(self, title):
       if title is not None:
            self.file = open(title + ".txt", "w+")
       else:
            self.file = open("默认文件.txt", "w+")
            
    def writeData2File(self, contents):
        for item in contents:
            floorline = "\n" + str(self.floor) + u"----------------------------------------------------------------------------------------------------------------------------------\n"
            self.file.write(floorline)
            self.file.write(item)
            self.floor += 1
    def openDB(self):
        try:
            conn = MySQLdb.connect('localhost','root','root','test2',144654)
            print conn
            return
            return conn
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    #添加写数据库方法
    def write2DB(self,value1,value2):
        try:
            conn = self.conn
            cur=conn.cursor()
            values = [i,value1,value2]
            conn.set_character_set('utf8')
            cur.execute('SET NAMES utf8;')
            cur.execute('SET CHARACTER SET utf8;')
            cur.execute('SET character_set_connection=utf8;')
            cur.execute('insert into test2(pageNum,contents) values(%s,%s)',values)
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        if pageNum == None:
            print "url已经失效"
            return
        try:
            print "该帖子一共有" + str(pageNum) + "页"
            for i in range(1, int(pageNum) + 1):
                print "正在写第" + str(i) + "页数据"
                page= self.getPage(i)
                contents = self.getContent(page)
                self.write2DB(pageNum,contents)
 #               self.writeData2File(contents)
        except IOError,e:
            print '写入异常'+ e.message
        finally:
            print '写入完毕'
            
#需要爬虫的链接地址        
baseUrl = 'http://tieba.baidu.com/p/3138733512'
#新建爬虫类
BDTB = bdtb(baseUrl, 1)
BDTB.start()
