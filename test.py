class NetSpider:

    __userAgent = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
    ]

    def __init__(self, headers=None):
        if(headers != None):
            self.__headers = headers
        else:
            self.__headers = {}
        self.__getProxy()
        self.__mkdir('log')


    def __setHeaders(self):
        import random
        self.__headers['User-Agent'] = random.choice(self.__userAgent)
        return self.__headers

    def __mkdir(self, path):
        import os
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs(path)

    def writeFile(self, path, data):
        with open(path, 'a', encoding='utf-8') as f:
            f.write(data)

    def __log(self, string):
        import time
        log = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' : ' + string
        print(log)
        self.writeFile('./log/log.txt', log+'/n')

    
    def __safeUrl(self, url):
        from urllib import parse
        import string
        return parse.quote(str(url), safe= string.printable)
    
    def __toDict(self, json_str):
        import json
        return json.loads(json_str)
    
    def __toJson(self, string):
        import json
        return json.dumps(string)
    
    def __getProxy(self):
        proxy_data = self.__toDict(self.__request('http://localhost/api/proxy', False))
        type = proxy_data['type']
        ip = proxy_data['ip']
        port = proxy_data['port']
        ip_str = ip + ':' + port
        if(type == 'http'):
            proxy = {'http': ip_str}
        if(type == 'https'):
            proxy = {'https': ip_str}
        self.__Proxy_IP = proxy

    def __download(self, path, url):
        import requests
        content = requests.get(url, proxies = self.__Proxy_IP)
        if(content.status_code == 200):
            with open(path, 'wb') as f:
                f.write(content.content)

    def __request(self, url, flage):
        import requests
        self.__log('开始请求'+url)
        headers = self.__setHeaders()
        query_url = self.__safeUrl(url)
        while True:
            try:
                if(flage == True):
                    r = requests.get(query_url, headers=headers, proxies=self.__Proxy_IP)
                else:
                    r = requests.get(query_url, headers=headers)
            except requests.exceptions.HTTPError as e:
                print(e)
                return    
            except requests.exceptions.ProxyError:
                self.__getProxy()
                continue 
            return r.text

    def __getDom(self, html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html5lib')
        return soup
    
    def __sleep(self, seconds):
        import time
        time.sleep(seconds)
    
    def select(self, dom, selected):
        return dom.select(selected)

    def __getLabel(self, tag, label):
        if(label == 'text'):
            return tag.string
        else:
            return tag.get(label)

    def test(self, url, flage):
        return self.__request(url, flage)

    def __getString(self, dom, selector, label):
        temp = []
        selected = self.select(dom, selector)
        for s in selected:
            temp.append(self.__getLabel(s, label))
        return temp

    def __getList(self, dom, selector, label):
        from functools import reduce
        temp = []
        _s = selector.split(' ')
        q = _s.pop()
        query = reduce(lambda x,y: x+' '+y, _s)
        parents_tag = self.select(dom, query)
        for tag in parents_tag:
            items = tag.find_all(q)
            for item in items:
                data = self.__getLabel(item, label)
                temp.append(data)
        return temp
    
    def __getDict(self, schema, urls):
        temp = []
        for url in urls:
            temp_list = self.resolvedata(schema, url)
            temp.append(temp_list)
        return temp

    def resolvedata(self, schema, url):
        html = self.__request(url, True)
        domTree = self.__getDom(html)
        schema_keys = schema.keys()
        res = {}
        for key in schema_keys:
            query_item = schema.get(key)
            query_type = query_item['type'].lower()
            query_data = query_item['data']
            if(query_type == 'string'):
                query_label = query_item['label']
                temp = self.__getString(domTree, query_data, query_label)
            elif(query_type == 'list'):
                query_label = query_item['label']
                temp = self.__getList(domTree, query_data, query_label)
            elif(query_type == 'dict'):
                query_url = query_item['url']
                urls = res[query_url]
                temp = self.__getDict(query_data, urls)
            else:
                return
            
            res[key] = temp
        return res
        

if __name__ == '__main__':
    douban = NetSpider()
    data1 = {
        "author": {
            "type": "list",
            "data": "#content #link-report .intro p",
            "label": "text"
        }
    }
    data = {
        "title": {
            "type": "string",
            "data": ".subject-list .subject-item .info h2 a",
            "label": "title"
        },
        "cover": {
            "type": "string",
            "data": ".subject-list .subject-item .pic .nbg img",
            "label": "src"
        },
        "href": {
            "type": "string",
            "data": ".subject-list .subject-item .info h2 a",
            "label": "href"
        },
        "info": {
            "type": "dict",
            "data": data1,
            "url": "href"
        }
    }
    

    data3 = douban.resolvedata(data, 'https://book.douban.com/tag/小说?start=0&type=T')
    print(data3)


