class NetSpider:

    __userAgent = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
    ]

    def __init__(self, *headers):
        if(headers):
            self.headers = headers
        else:
            self.headers = {}
    
    def __setitem__(self, k, v):
        self.k = v
    
    def safeUrl(self, url):
        from urllib import parse
        import string
        return parse.quote(url, safe= string.printable)

    def log(self, s):
        import time
        log = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' : ' + s
        self.writeFile('log.txt', log)
        print(log)
    
    def mkdir(self, path):
        from functools import reduce
        import os
        p = path
        p = p.split('/')
        if(len(p) > 1):
            p.pop()
        dir_path = reduce(lambda x,y: x+'/'+y, p)

        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(dir_path)
            self.log('创建目录' + path + '成功')
            return True
        else:
            self.log('目录' + path + '已存在')
            return False

    def writeFile(self, path, data): 
        import json
        wf = json.dumps(data, ensure_ascii=False)
        try: 
            f = open(path, 'a', encoding = 'utf-8')
        except IOError:
            self.mkdir(path)
            f = open(path, 'a', encoding = 'utf-8')
        f.write(wf + '\n')
        f.close()
    
    def downloadImg(self, url, path):
        import re
        from urllib import request
        title = re.search(r'\w+?\.(jpg|png|gif)$', url).group()
        request.urlretrieve(url, path + title)

    def get(self, url):
        import random
        from urllib import request,error
        import time
        agent = random.choice(self.__userAgent)
        _headers = self.headers
        _headers['User-Agent'] = agent

        query = request.Request(self.safeUrl(url), headers=_headers)

        while True:

            try:
                self.log('开始请求: ' + url)
                time.sleep(1)
                response = request.urlopen(query)
            except error.HTTPError as e:
                if(e.code > 300 and e.code < 400):
                    self.log('服务器请求重定向，暂停12小时')
                    time.sleep(43200)
                    continue
                if(e.code >= 400):
                    self.log('url请求错误' + e.code + ':跳过此请求')
                    return False
            
            self.log('成功请求: ' + url)
            return response.read().decode('utf-8')
    
    def select(self, selected, doc):
        return doc.select(selected)

    def getLabel(self, tag, label):
        if(label == 'text'):
            return tag.string
        else:
            return tag.get(label)
    

    def resolveData(self, query_data, url, flage):
        from bs4 import BeautifulSoup
        from functools import reduce
        html = self.get(url)
        if(html):
            soup = BeautifulSoup(html,  'html5lib')
            keys = query_data.keys()
            d = {}
            _len = 0
            for key in keys:
                l = []
                query = query_data.get(key)
                # print(query)
                if (query['type'] == 'string'):
                    temp = self.select(query['data'], soup)
                    _len = len(temp)
                    for data in temp:
                        l.append(self.getLabel(data, query['label']))

                elif (query['type'] == 'list'):
                    query_string = query['data']
                    q = query_string.split(' ')
                    query_item = q.pop()
                    query_data = reduce(lambda x, y: x + ' ' + y, q)
                    query_item_temp = self.select(query_data,soup)
                    for query_temp in query_item_temp:
                        items = query_temp.find_all(query_item)
                        for data in items:
                            l.append(self.getLabel(data, query['label']))
                elif (query['type'] == 'dict'):
                    data = query['data']
                    k = query['url']
                    if(k not in keys):
                        self.log('输入参数不存在')
                    else:
                        urls = d[k]
                        for url in urls:
                            temp = self.resolveData(data, url, False)
                            l.append(temp)

                d[key] = l
            if(flage == True):
                c_data = []
                for i in range(_len):
                    temp = {}
                    for key in keys:
                        temp[key] = d[key][i]
                    c_data.append(temp)                       
            else:
                c_data = d

            print(c_data)
            return c_data

                        
