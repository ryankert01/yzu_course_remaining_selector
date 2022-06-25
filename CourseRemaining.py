import imp
import time
import requests
from bs4 import BeautifulSoup
import configparser
import os

courseList=['304,CS310A']
            
class Auto:
        def __init__(self, account, password):
            self.account = account
            self.password = password
            self.coursesDB = {}

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
              # download and recognize captch
                with self.session.get(self.captchaUrl, stream= True,allow_redirects=False) as captchaHtml:
                    captcha=captchaHtml.cookies['CheckCode']

                # get login data
                loginHtml = self.session.get(self.loginUrl)
                # use BeautifulSoup to parse html
                parser = BeautifulSoup(loginHtml.text, 'lxml')
                # update login payload
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
                    break

        def Consolelog(self, msg):
            print(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), msg)
            
        def LineNotifyLog(self,token,msg):
            headers = {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/x-www-form-urlencoded"
                }
     
            params = {"message": msg}
            requests.post("https://notify-api.line.me/api/notify",headers=headers, params=params)

        def exec(self):
            file = open('course.html', 'w')
            for i in courseList:
                tempdept = i.split(',')[0]
                html = self.session.get(self.indexURL)
                parser = BeautifulSoup(html.text, 'lxml')
                selPayLoad={
                    "__EVENTTARGET": '',
                    "__EVENTARGUMENT": '' ,
                    "__LASTFOCUS":'',
                    "__VIEWSTATE": parser.select("#__VIEWSTATE")[0]['value'],
                    "__VIEWSTATEGENERATOR":parser.select("#__VIEWSTATEGENERATOR")[0]['value'], 
                    "Q": 'RadioButton1',
                    "DDL_YM": '',  
                    "DDL_Dept": tempdept,
                    "DDL_Degree": "0",
                    "Button1": "確定"
                }


                html = self.session.post(self.indexURL, data=selPayLoad,headers=self.session.headers)
                print(html.text,file=file)
                


if __name__=="__main__":
    configFilename = 'accounts.ini'
    if not os.path.isfile(configFilename):
        with open(configFilename, 'a') as f:
            f.writelines(["[Default]\n", "Account= your account\n", "Password= your password"])
            print('input your username and password in accounts.ini')
            exit()

    config = configparser.ConfigParser()
    config.read(configFilename)
    Account = config['Default']['Account']
    Password = config['Default']['Password']
    bot=Auto(Account, Password)
    bot.login()
    bot.exec()