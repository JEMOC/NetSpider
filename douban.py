from NetSpider import *
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
    

    data3 = douban.resolveData(data, 'https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start=0&type=T', True)
    douban.writeFile('a.json', data3)




        
