#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------
#   程序：xicidaili.py
#   版本：0.1
#   作者：ly
#   日期：编写日期201l/11/16
#   语言：Python 2.7
#   操作：python referer_forge.py
#   功能：从www.xicidaili.com网站采集代理信息并存入数据库
#-------------------------------------------------------------------------
import requests,re,json
import sys,os,time

# --------------------------------------------------
# 中文编码设置
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# 数据库设置
MYSQL_HOST = ''
MYSQL_DBNAME = ''
MYSQL_USER = ''
MYSQL_PASSWD = ''
MYSQL_PORT= 3306

# 此处修改数据库插入修改语句
install_str = '''
INSERT INTO proxy_xici( `proxy_ip`, `proxy_port`, `proxy_country`, `proxy_type`, `addtime`, `Last_test_time`, `proxy_status`, `Remarks`   )
VALUES (%s,%s,%s,%s,%s,%s,%s,%s)  '''

# 此处修改伪造的头字段,
headers = {
    'Host':"www.xicidaili.com",#需要修改为当前网站主域名
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    # "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0",
	#"referer" : '123.123.123.123'#随意的伪造值
}

#发起请求,
def get_request(url,headers):
    '''参数引入及头信息'''
    html=requests.get(url,headers=headers, timeout=20).text.decode('utf8')
    print html
    return html


# 将页面源代码正则匹配并解析,返回列表,其中每一项是json的数据
def re_html_code(html_code,proxy_list_json):

    # re正则取出数据
    try:
        re_list_ip = re.findall(r'<td>\d*\.\d*\.\d*\.\d*</td>',html_code)
        re_list_port = re.findall(r'<td>[\d]*</td>',html_code)
        re_list_live_time = re.findall(u'<td>\d*[小时分钟天]+</td>',html_code)
        print re_list_live_time
        #print type(html_code),type(r'<td>\d*[小时分钟天]+</td>')
        re_list_time = re.findall(r'<td>\d*-\d*-\d* \d*:\d*</td>',html_code)
        #print re_list_ip
        l = len(re_list_ip)
        for i in range(l):
            PROXY_IP = re_list_ip[i].replace('<td>','').replace('</td>',"")
            PROXY_PORT = re_list_port[i].replace('<td>','').replace('</td>',"")
            PROXY_COUNTRY = 'China'
            PROXY_TYPE= 'Elite'
            addtime = re_list_time[i].replace('<td>','').replace('</td>',"")
            Last_test_time = re_list_live_time[i].replace('<td>','').replace('</td>',"")
            #print Last_test_time
            #time.sleep(10)
            proxy_status = '1'
            Remarks = 'ly'
            # `id`, `proxy_ip`, `proxy_port`, `proxy_country`, `proxy_type`, `addtime`, `Last_test_time`, `proxy_status`, `Remarks`
            # list_i = [PROXY_IP,PROXY_PORT,PROXY_COUNTRY,PROXY_TYPE,addtime,Last_test_time,proxy_status,Remarks]
            list_i = (PROXY_IP, PROXY_PORT)
            #print list_i
            proxy_list_json.append(list_i)

        print proxy_list_json
        return proxy_list_json

    except Exception,e:
        print Exception,e
#{'PROXY_STATUS': 'OK', 'PROXY_CITY': '', 'PROXY_TIME': '548', 'PROXY_STATE': '', 'PROXY_REFS': '', 'PROXY_TYPE': 'Transparent', 'PROXY_COUNTRY': 'China', 'PROXY_LAST_UPDATE': '1 59', 'PROXY_UPTIMELD': '105/16', 'PROXY_UID': '', 'PROXY_PORT': '1F90', 'PROXY_IP': '61.158.173.14'}





if __name__ == '__main__':

    proxy_list_json = []
    # for i in range(1,2):
    #     url = "http://www.xicidaili.com/nn/"+str(i)
    #     print 'begin',url
    #     try:
    #         #html_code = get_request(url,headers)
    #         html_code = get_request(url,headers)
    #         proxy_list = []
    #         now_url = url
    #         proxy_list_json = re_html_code(html_code, proxy_list)
    #     except Exception,e:
    #         print Exception,e

    url = "http://3360623093271490.standard.hutoudaili.com/?num=20&area_type=1&ports=8123&anonymity=3&order=1"
    try:
        # html_code = get_request(url,headers)
        html_code = requests.get(url, timeout=20).text.decode('utf8')
        proxy_list = []
        now_url = url
        proxy_list_json = html_code.split()
    except Exception, e:
        print Exception, e
    with open("cnproxy.py", 'w') as f:
        f.write("PROXIES = [\n")
        for model in proxy_list_json:
            print model
            f.write("\t\t\t{\"ip_port\":\"%s\"},\n" % model)
        f.write("]\n")