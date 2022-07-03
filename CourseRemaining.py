import time
import requests
from bs4 import BeautifulSoup as bs
import configparser
import os


            
class Auto:
    def __init__(self, info):
        self.courseList=[]
        self.account = info[0]
        self.password = info[1]
        self.token = info[2]
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
            parser = bs(loginHtml.text, 'lxml')
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
    #    self.LineNotifyLog(temp)
        
    def LineNotifyLog(self,msg):
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/x-www-form-urlencoded"
            }
        temp = "{} {} ".format(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), msg)
        params = {"message": temp}
        requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)

    def remove(self,item):
        if(item in self.courseList):
            self.courseList.remove(item)
        
    def setDelay(self, delay):
        self.delay = delay

    def exec(self):
        while(len(self.courseList)>0):
            for course in self.courseList:
                courseDept = course[0:3] # 304
                courseId = course[4:] # CS380B
                
                if(courseDept not in self.deptdb): # detect if the dept is valid
                    self.Consolelog("{} is not in the department list".format(courseDept))
                    self.remove(course)
                    continue

                html = self.session.get(self.indexURL)
                if "login.aspx?Lang=TW" in html.text:
                    self.login()
                    
                #get info on the net 
                html = self.session.get(self.indexURL)

                parser = bs(html.text, 'lxml')
                PrePayLoad={
                    '__EVENTTARGET': 'DDL_Dept',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE':  parser.select("#__VIEWSTATE")[0]['value'],
                    '__VIEWSTATEGENERATOR': parser.select("#__VIEWSTATEGENERATOR")[0]['value'],
                    '__EVENTVALIDATION': parser.select("#__EVENTVALIDATION")[0]['value'],
                    'Q': 'RadioButton1',
                    'DDL_YM': parser.select('option')[0]['value']  ,
                    'DDL_Dept': courseDept,
                    'DDL_Degree': '0'
                }

                prePost = self.session.post(self.indexURL,data=PrePayLoad)
                parser = bs(prePost.text, 'lxml')

                PostPayLoad={
                    '__EVENTTARGET':'',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE':  parser.select("#__VIEWSTATE")[0]['value'],
                    '__VIEWSTATEGENERATOR': parser.select("#__VIEWSTATEGENERATOR")[0]['value'],
                    '__EVENTVALIDATION': parser.select("#__EVENTVALIDATION")[0]['value'],
                    'Q': 'RadioButton1',
                    'DDL_YM': parser.select('option')[0]['value'],
                    'DDL_Dept': courseDept,
                    'DDL_Degree': '0',
                    'Button1': '確定'
                }
                
                postPost = self.session.post(self.indexURL,data=PostPayLoad)
                result =  bs(postPost.text,"lxml")     # result of the request

                info = self.getCourseInfo(result)
                #get forall class info in this Department
                coursedb = info[0]    # coursedb => [[courseId]...]
                courseinfo = info[1] # courseinfo => [['id', 'Tname', 'CName', 'Remain', 'Total']...]
                self.Consolelog("Get {} infos Success".format(courseDept))
                
                if(courseId not in coursedb):
                    self.Consolelog("Can't get course in {}".format(courseDept))
                    self.remove(course)
                else:
                    index = coursedb.index(courseId)
                    self.Consolelog("{} {} ==> {}/{}".format(courseinfo[index][0],courseinfo[index][2],courseinfo[index][3],courseinfo[index][4]))
                    remain = int(courseinfo[index][4])-int(courseinfo[index][3])
                    if(remain>0):
                        # courseinfo => [['id', 'Tname', 'CName', 'Remain', 'Total']...]
                        self.LineNotifyLog("{} {} is avail for {} people".format(courseinfo[index][0],courseinfo[index][2],remain))
                        self.Consolelog("{} {} is avail for {} people".format(courseinfo[index][0],courseinfo[index][2],remain))
        
    def getCourseInfo(self,soup):
        result = soup.select("#Table1")[0].select("tr")
        num = 0
        couinfo=[]
        coudb=[]
        for i in result:
            num+=1
            if(num%2==1):
                continue
            else:
                tempCode = i.select("td")[1].text.split(' ')
                couID = "{}{}".format(tempCode[0],tempCode[1])  
                coudb.append(couID)
                temp =[couID,i.select("td")[6].text,i.select("td")[3].select_one('a').text,i.select("td")[7].text.split('/')[0][2:],i.select("td")[7].text.split('/')[1]] 
                couinfo.append(temp)
        return [coudb,couinfo]

    def setCourseList(self):
        with open("CourseList.txt","r") as f:
            courses = f.readlines()
        f.close()

        for course in courses:
            if(course[-1] == "\n"):
                course = course[:-1]
            self.courseList.append(course)
        self.courseList.sort()
        print(self.courseList)
        self.Consolelog("Set CourseList Success")

if __name__=="__main__":
    configFilename = 'accounts.ini'
    if not os.path.isfile(configFilename):
        with open(configFilename, 'a') as f:
            f.writelines(["[Default]\n", "Account= your account\n", "Password= your password\n","Token= your LineNotifyToken"])
            print('input your info in accounts.ini')
            f.close()
            exit()
    
    classFilename = 'CourseList.txt'
    if not os.path.isfile(configFilename):
        with open(configFilename, 'a') as f:
            print('input your info in CourseList.txt')
            f.close()
            exit()   
    config = configparser.ConfigParser()
    config.read(configFilename)
    info=[config['Default']['Account'],config['Default']['Password'],config['Default']['Token']]
    bot=Auto(info)
    bot.login()
    bot.setCourseList()
    bot.setDelay(3)
    bot.exec()
