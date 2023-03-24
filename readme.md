# 爬取文旅部和广电总局新闻信息
### 动因及吐槽

---


领导却让我每周整理文旅部和广电总局发布的有商业价值的消息。要把网站里的新闻都看个遍，一条一条点开实在是浪费时间。~~已经30多岁了，可怎么看都像是个实习生的活儿，光劳神没什么实际价值和提升。 ~~于是尝试用爬虫将所有的新闻合并到一个页面下，既能一目十行还能顺便学习下爬虫和类的用法。

---

### 功能

使用xpath进行解析并保存至sqlite数据库，并由网页展示所有新闻内容
### 使用方法
环境准备 python > 3.7  

```
pip install lxm, flask-sqlalchemy 
```

(虽然sqlalchemy目前还没用上……)

1、运行main.py  \(这将生成数据库文件)  
2、运行web.py,按输出打开浏览器窗口   \(比如地址：http://127.0.0.1:5000）  
3、enjoy！
### TODO
1、优化获取全文和展示的方法，目前是全部都显示，未使用异步获取拿到。  
2、尝试使用Vue框架实现一些前端功能  
3、学习SQL语句的同时使用SQLAlchemy进行数据的获取，并比较二者时间。  
4、学习celery做定时任务
### 主要方法
DbBot 管理数据库相关的方法\
Spyderlets 爬虫特工们的相关功能



