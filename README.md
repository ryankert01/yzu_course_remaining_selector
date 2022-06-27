# yzu_course_remaining_selector

## Introduction
最近開始搶課，所以就寫了一個可以自己抓課程剩餘人數的程式。

## Depndencies
* requests
* bs4 
* lxmllxml

## Usage 
1. 下載到電腦
 ```shell
 git clone https://github.com/mhy1264/yzu_course_remaining_selector.git
 ```
 
2. 安裝套件
```
pip install requests bs4 lxml
```

3. 新增 accounts.ini 存放Portal帳密、LineNotifyToken 的檔案，格式如下:<br>
Line Notify Token 可以參考 : [自建 LINE Notify 訊息通知](https://www.oxxostudio.tw/articles/201806/line-notify.html)
```
[Default]
Account=
Password=
Token=
```

4.在  中
5.修改 CourseList.txt 中輸入課號
一行一個課號，格式如下
```
'901,LS236A' 
```
901 是系所代碼, LS236A 是課號班別

6. 執行
```
python CourseRemaining.py
```
> **Warning** <br>
> 請斟酌使用本機器人程式，並自行負責使用後所造成的損失!
