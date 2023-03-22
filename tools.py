from functools import wraps
from threading import Thread, Lock
from queue import Queue
from lxml import etree
from urllib import request
import json, re, time, sqlite3, random

def time_it(func):
    '''
    计时装饰器，统计函数运行时间
    '''
    @wraps(func)
    def decorated(*args, **kwargs):
        start_time = time.time()
        r = func(*args, **kwargs)
        duration = time.time() - start_time
        print('Name: ', func.__name__, 'Duration: ', duration)
        return r

    return decorated

ua_list = [
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'User-Agent:Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
]

class DbBot(object):
    def __init__(self) -> None:
        self.db_name = './db_test.db'

    def do_execute(self, cmd):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(cmd)
        conn.commit()
        conn.close()
        return True

    def create_table(self):
        create_table = '''
        CREATE TABLE IF NOT EXISTS Sites 
        (
        Name    TEXT    NOT NULL,
        URL     TEXT    NOT NULL,
        Date    DATE    NOT NULL,
        Content TEXT    ,
        Parse   TEXT
        );
        '''
        self.do_execute(create_table)

class Spyderlets:
    def __init__(self) -> None:
        self.url = None
        self.html = None
        self.parsed_html = None
        self.q = Queue()
        self.i = 0
        self.for_main_text = False
        self.url_list = []
        self.lock = Lock()

    def get_html(self, url=None, file_name=None, read_file=True):
        '''get the html from url'''
        if read_file:
            self.read_html(file_name)
        if not self.html:
            print('getting online html info ...')
            headers = {'User-Agent':random.choice(ua_list)}
            req = request.Request(url=url, headers=headers)
            res = request.urlopen(req)
            self.html = res.read().decode('utf-8')
            if read_file:
                self.save_html(file_name)
        return self.html

    def get_url_batch(self):
        '''get url from queue, saving '''
        while True:
            if not self.q.empty():
                self.url = self.q.get
                return True
                
    def get_html_complex(self):
        while True:
            if not self.q.empty():
                url = self.q.get()
                self.url = url
                self.for_main_text=True
                headers = {'User-Agent':random.choice(ua_list)}
                req = request.Request(url=url, headers=headers)
                res = request.urlopen(req)
                self.html = res.read().decode('utf-8')
                parse = self.parse_mod(url)
                content =self.parse_html(parse, True)
                if isinstance(parse, tuple):
                    parse = ''.join(parse)
                    # print(type(parse))
                db = DbBot()
                cmd = f'''UPDATE Sites SET Content = '{content}', Parse = '{parse}' where URL = '{url}' '''
                db.do_execute(cmd)
                # try:
                #     db.do_execute(cmd)
                # except sqlite3.OperationalError as e:
                #     print('e:', e)
                #     print('Content:', content)
                    
            else:
                break
    
    def parse_mod(self, url):
        # 整理url对应关系
        domain = url.split("/")[2].split(".")
        sub_domain = domain[0]
        host = domain[1]
        cmd1 = None
        if host == "mct":
            if sub_domain == 'zwgk':
                parse = '''//div[@class="gsj_htmlcon_bot" or @class="main_htmlcon"]/*[name(.)!="style" and not(contains(@class,"nyb_fj"))]'''
                cmd1 = 'string(.)'
            else:
                # parse = '//*[@id="zoom"]//div/*[self::p or self::div and name(.)!="style" and name(.)!="script"]'
                parse = '//*[@id="zoom"]//div/*[not(name() = "style") and not(name() = "script") and not(@class="TRS_Editor")]'
                cmd1 = 'string(.)'
        elif host == "nrta":
            parse = '//*[@id="c"]/div'
            cmd1 = 'string(.)'
        elif host == 'gov':
            # parse = '//*[@id="UCAP-CONTENT"]/*[self::p or self::div]/text()'
            parse = '//*[@id="UCAP-CONTENT"]/*[name(.)!="style" and name(.)!="script" and not(contains(@id,"myFlash"))]'
            cmd1 = 'string(.)'
        elif host == 'news':
            parse = '//*[@id="detail"]/p'
            cmd1 = 'string(.)'
        return parse, cmd1

    def parse_html(self, cmd, complex=False, for_main_text=False):
        cmd1 = None
        if type(cmd) is tuple:
            cmd, cmd1 = cmd 
        if not self.html:
            return "html empty"
        # parse_html = etree.tostring(self.html)
        info = etree.HTML(self.html).xpath(cmd)
        # 如果希望匹配出string的效果，走这个
        if complex:   
            if isinstance(info, list):
                # try:
                    res = []
                    for i in info: 
                        res.append(i.xpath(cmd1))
                    info = res
                    info = list(map(lambda x:x.replace(u'\u3000',u'')\
                                    .replace('\n', '').replace('\r', '')\
                                    .replace(" ","").replace(" ","")\
                                    .replace('\t', '').replace("\xa0", ''), info))
                    info = [x for x in info if x !=""]
                    info = "\n".join(info)
                # except TypeError as e:
                #     print("cmd: ", cmd)
                #     print("E: ", e)
                #     print("The url:", self.url)
        if cmd1:
            if type(info) == list:
                res = []
                for i in info: 
                    res.append(i.xpath(cmd1))
                    # info = '\n'.join(res)
                    if self.for_main_text or for_main_text:
                        info = '\n'.join(res)
        return info
    
    
        
        
    def read_html(self, file_name):
        try:
            with open (f'./{file_name}.html', encoding='utf-8') as f:
                self.html = f.read()
        except:
            pass

    def save_html(self, file_name):
        if not file_name:
            file_name = 'result'
        with open(f'./{file_name}.html', 'w', encoding='utf-8') as f:
            f.write(self.html)

    def save_json(self, c_key,c_list, filename=None):
        res_list = []
        if not self.html:
            raise "GET HTML FIRST!"
        for i in range(len(c_list)):
            t = dict(zip(c_key, c_list[i]))
            res_list.append(t)
        
        res_json = json.dumps(res_list, ensure_ascii=False)
        if not filename:
            filename = 'result'
        with open (f'./{filename}.json', 'w', encoding='utf-8') as f:
            json.dump(res_list, f, ensure_ascii=False)
        return res_json

    def run(self):
        html = self.get_html()
        self.save_html('output', html)

    def do_execute(c, self, command):
        c.execute(command)

@time_it
def solve_mct(db):
    url = "https://www.mct.gov.cn/"
    file_name = url.split("/")[2].split(".")[1]

    content_list = []
    spyders = Spyderlets()
    spyders.for_main_text = False
    spyders.get_html(url, file_name)
    
    # 标题
    title_parse = '//div[@class="list_part1"]//li//a/@title'
    c_list = spyders.parse_html(title_parse)
    
    # url
    url_parse = '//div[@class="list_part1"]//li//a[@title]/@href'
    r_list = spyders.parse_html(url_parse)

    # time
    time_parse = '//div[@class="list_part1"]//li//span/text()'
    t_list = spyders.parse_html(time_parse)
    for i in range(len(t_list)):
        if r_list[i][0] == '.':
            r_list[i] = 'https://www.mct.gov.cn/'+r_list[i][1:]
        spyders.q.put(r_list[i])
        content_list.append([c_list[i], r_list[i], t_list[i]])
        cmd = f'''INSERT INTO Sites VALUES ('{c_list[i]}', '{r_list[i]}', '{t_list[i]}', '', '')'''
        db.do_execute(cmd)

    content_key = ('name', 'url', 'date')
    spyders.save_json(content_key, content_list)

    spyders.html = None 
    t_list = []
    for i in range(3):
        t = Thread(target=spyders.get_html_complex)
        t_list.append(t)
        t.start()
    for t in t_list:
        t.join()
    print('finished')

@time_it
def solve_nrta(db):
    content_key = ('name', 'url', 'date')
    content_list = []

    url = "http://www.nrta.gov.cn/"
    file_name = url.split("/")[2].split(".")[1]
    
    title_parse = '//div[@id="barrierfree_container"]//li//a[@title]/@title'
    date_parse = '//div[@id="barrierfree_container"]//li//span/text()'
    url_parse = '//div[@id="barrierfree_container"]//li//a[@title]/@href'
    spyder = Spyderlets()
    spyder.for_main_text=False
    spyder.get_html(url, file_name)
    title_list = spyder.parse_html(title_parse)
    date_list = spyder.parse_html(date_parse)
    url_list = spyder.parse_html(url_parse)
    title_list.reverse()
    date_list.reverse()
    url_list.reverse()


    date_list = date_list + ([""]*(len(title_list)-len(date_list)))
    for i in range(len(url_list)):
        if url_list[i][0] == '/':
            url_list[i] = url+url_list[i][1:]
        mod_date = date_list[i]
        
        # 匹配没有日期的其他网站
        if "www.news.cn" in url_list[i] or "www.gov.cn" in url_list[i]:
            # 使用正则表达式匹配字符串中的日期部分
            match = re.search(r'/(\d{4}-\d{2}/\d{2})/', url_list[i])
            
            # 如果匹配成功，则提取出第一个匹配组中的字符串
            if match:
                mod_date = match.group(1).replace('/', '-')

        elif not date_list[i]:
            match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', url_list[i])
            if match:
                year = match.group(1)
                month = match.group(2)
                day = match.group(3)
                # 格式化日期为 "YYYY/MM/DD" 的形式
                mod_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        spyder.q.put(url_list[i])
        cmd = f'''INSERT INTO Sites VALUES ('{title_list[i]}', '{url_list[i]}', '{mod_date}', '', '')'''
        db.do_execute(cmd)
        content_list.append([title_list[i], url_list[i], mod_date])
    t_list = []
    for i in range(3):
        t = Thread(target=spyder.get_html_complex)
        t_list.append(t)
        t.start()
    for t in t_list:
        t.join()
    print('finished')
    spyder.save_json(content_key, content_list, file_name)


