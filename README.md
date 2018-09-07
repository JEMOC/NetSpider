# #NetSpider

------

## #创建实例

```python
NetSpider(*header)
```

## #创建数据模型

```python
data  = {
    "query-string": {
        "type": "(string|list|dict)",
        "data": "[css selector]",
        *"label": "(text|title|src|href)",
        *"url": "(this.data[key])"
    }
}
```

## #爬取数据入口

```python
NetSpider.resolveData(data, url, flage)
```

## #内置方法

```python
NetSpider.get(url) string<html>
NetSpider.select(selected, doc) list<tag>


```

