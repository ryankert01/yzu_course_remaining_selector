import time
import requests
from bs4 import BeautifulSoup
import configparser
import os

from urllib3 import Retry

courseList=['304,CS380B']
            
class Auto:
    def __init__(self, info):
        self.account = info[0]
        self.password = info[1]
        self.token = info[2]
        self.coursesDB = {}
        self.deptdb=['300', '302', '303', '305', '309', '322', '323', '325', '329', '330', '352', '353', '355', '500', '505', '530', '531', '532', '554', '600', '601', '602', '603', '604', '608', '621', '622', '623', '624', '656', '700', '304', '701', '702', '705', '721', '722', '723', '724', '725', '751', '754', '800', '310', '311', '312', '313', '331', '332', '333', '359', '360', '361', '301', '307', '308', '326', '327', '328', '356', '357', '358', 'A00', 'A21', '901', '903', '904', '906', '907']
        # for requests
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        self.baseURL="https://portalfun.yzu.edu.tw/cosSelect/"
        self.loginUrl = '{}login.aspx'.format(self.baseURL)
        self.captchaUrl='{}ImageCode.aspx'.format(self.baseURL)
        self.indexURL='{}index.aspx'.format(self.baseURL)

        self.loginPayLoad = {
            '__VIEWSTATE': '',
            '__VIEWSTATEGENERATOR': '',
            '__EVENTVALIDATION': '',
            'uid': self.account,
            'pwd': self.password,
            'Code': '',
            'Button1': '登入'
        }

    def login(self):
        while True:
            self.session.cookies.clear()
            with self.session.get(self.captchaUrl, stream= True,allow_redirects=False) as captchaHtml:
                captcha=captchaHtml.cookies['CheckCode']

            loginHtml = self.session.get(self.loginUrl)
            parser = BeautifulSoup(loginHtml.text, 'lxml')
            self.loginPayLoad['__VIEWSTATE'] = parser.select("#__VIEWSTATE")[0]['value']
            self.loginPayLoad['__VIEWSTATEGENERATOR'] = parser.select("#__VIEWSTATEGENERATOR")[0]['value']
            self.loginPayLoad['__EVENTVALIDATION'] = parser.select("#__EVENTVALIDATION")[0]['value']
            self.loginPayLoad['Code'] = captcha

            result = self.session.post(self.loginUrl, data= self.loginPayLoad)

            if ("parent.location='index.aspx'" in result.text):
                self.Consolelog('Login Successful! {}'.format(captcha))
                break
            else:
                self.Consolelog("Login Failed, Re-try!")

    def Consolelog(self, msg):
        temp = "{} {} ".format(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), msg)
        print(temp)
        self.LineNotifyLog(temp)
        
    def LineNotifyLog(self,msg):
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        temp = "{} {} ".format(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), msg)
        params = {"message": temp}
        requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)

    def remove(self,item):
        if(item in courseList):
            courseList.remove(item)
        
    def setDelay(self, delay):
        self.delay = delay

    def exec(self):
        while(len(courseList)>0):
            for course in courseList:
                courseDept = course[0:3] # 304
                courseId = course[3:] # CS380B
                
                if(courseDept in self.deptdb): # detect if the dept is valid
                    self.Consolelog("{} is not in the department list".format(courseDept))
                    self.remove(course)
                    continue

                #get info on the net 

                result = "" # result of the request

                #get forall class info in this Department
                coursedb = self.getCourseDB(result)     # coursedb => [courseId]
                self.Consolelog("Get {} course db Success".format(courseDept))
                courseinfo = self.getCourseInfo(result) # courseinfo => [[courseId, Teacher, Remain, Total]]
                self.Consolelog("Get {} course info Success".format(courseDept))
                
                if(courseId not in coursedb):
                    self.Consolelog("Can't get course in {}".format(courseDept))
                    self.remove(course)
                else:
                    index = coursedb.index(course)
                    self.Consolelog("{} ==> {}/{}".format(courseinfo[index][0],courseinfo[index][2],courseinfo[index][3]))
                    if(courseinfo[index][2]-courseinfo[index][3]!=0):
                        self.LineNotifyLog("{} is avail for {} people",format(courseinfo[index][0],courseinfo[index][2]-courseinfo[index][3]))
                
                time.sleep(self.delay) # prevent from being banned by insys

    def getCourseDB(self,soup):
        result = soup.select("#Table1")[0].select("tr")
        num = 0
        coudb=[]
        for i in result:
            num+=1
            if(num%2==1):
                continue
            else:
                tempCode = i.select("td")[1].text.split(' ')
                couID = "{}{}".format(tempCode[0],tempCode[1])
                coudb.append(couID)
        return coudb
        
    def getCourseInfo(self,soup):
        result = soup.select("#Table1")[0].select("tr")
        num = 0
        couinfo=[]
        for i in result:
            num+=1
            if(num%2==1):
                continue
            else:
                tempCode = i.select("td")[1].text.split(' ')
                couID = "{}{}".format(tempCode[0],tempCode[1])
                temp =[couID,i.select("td")[6].text,i.select("td")[7].text.split('/')[0][2:],i.select("td")[7].text.split('/')[0][2:]]
                couinfo.append(temp)
        return couinfo

if __name__=="__main__":
    configFilename = 'accounts.ini'
    if not os.path.isfile(configFilename):
        with open(configFilename, 'a') as f:
            f.writelines(["[Default]\n", "Account= your account\n", "Password= your password\n","Token= your LineNotifyToken"])
            print('input your info in accounts.ini')
            exit()

    config = configparser.ConfigParser()
    config.read(configFilename)
    info=[config['Default']['Account'],config['Default']['Password'],config['Default']['Token']]
    bot=Auto(info)
    bot.login()
    bot.setDelay(3)
    bot.exec()