# 重庆爬虫

## 已实现功能
- 使用scrapy-redis，可实现分布式爬取，断点爬取
- 根据规则提取页面链接并保存在redis，稍后爬取
- 根据规则，对特定链接的内容进行处理，处理包括：图片下载并上传oss，页面图片的地址替换，页面内容入库
- random proxy中间件，未使用，如果有反爬虫机制可再开启，需配合 proxy_pool 使用

## TODO
- [ ] 视频下载？
- [ ] 其他分院爬取规则
- [ ] 如果反爬虫需要用到javascript，则搭建splash

## 目录结构
- chongqing
    - chongqing 
        - spiders （爬虫代码）
            - cfl.py （外国语学院爬虫）
        - items.py （scrapy item）
        - middlewares （中间件）
        - pipelines.py （item处理管道）
        - settings.py （scrapy配置文件）
    - scrapy.cfg （项目整体配置文件）

## 开发内容
- 修改scrapy.cfg，如果不使用gerapy，就不用修改
- settings.py中修改 mysql、redis、oss配置信息
- 复制cfl.py，定制规则然后爬取
- 定制settings.py的其他规则

## 部署

### 方法一
- cd chongqing
- scrapy crawl cfl（其他爬虫，则替换cfl为其他名字）

### 方法二
1. 安装scrapyd并运行 ```scrapyd```
2. 安装gerapy并运行 ```gerapy runserver 0.0.0.0:port```
3. 在gerapy面板里添加主机、部署爬虫、管理爬虫