# def outer(x):
#     def inner(y):
#         return x + y
#     return inner

# print(outer(6)(5))


# from mct_old_device import *
from tools import *

def test_zwgk():
    spyder = Spyderlets()
    url = 'https://zwgk.mct.gov.cn/zfxxgkml/zykf/202303/t20230301_939439.html'
    spyder.get_html(url)
    clear = spyder.parse_html(('//div/div[@class="gsj_htmlcon_bot"]/*[name(.)!="style" and not(contains(@class,"nyb_fj"))]','string(.)'))
    print(clear)
    # spyder.html = clear
    content = spyder.parse_html(('''//div/div[@class="gsj_htmlcon_bot"]/
    *[self::p or self::div or self::span]/text()'''))

    # content = list(map(lambda x:x.remove(''), content))
    content = list(map(lambda x:x.replace(u'\u3000',u'')\
                                .replace('\n', '').replace('\r', '')\
                                .replace(" ","").replace(" ","")\
                                .replace('\t', '').replace("\xa0", ''), content))
    content = [x for x in content if x !=""]
    # print(content)
    content = "\n".join(content)
    print(content)

@time_it
def test_mct(url):
    spyder = Spyderlets()
    spyder.get_html(url)
    # print(spyder.html)
    cmd = 'string(//div[@class="gsj_htmlcon_bot"]/*)'
    cmd1 = 'string(.)'
    # clear = spyder.parse_html(parse_mod(url), for_main_text=True)
    # clear = spyder.parse_html((cmd, cmd1), for_main_text=True)
    clear = etree.HTML(spyder.html).xpath(cmd)
    # res = []
    # for i in clear:
    #     print(i) 
    #     res.append(i.xpath(cmd1))
    # clear = res
    # clear = spyder.parse_html(cmd, for_main_text=True)
    print('Clear: ',clear)
    # if type(clear) == list:
    #     clear = ''.join(clear)
    # print(clear)

url = 'https://zwgk.mct.gov.cn/zfxxgkml/zcfg/gfxwj/202206/t20220627_934100.html'
# test_mct(url)

def test_sql():
     
    conn = sqlite3.connect('db_test.db')
    c = conn.cursor()
    cursor = c.execute("SELECT * FROM Sites")
    rows = cursor.fetchall()
    print(rows)

test_sql()