import socket  #用套接字编程
import pandas as pd
import numpy as np
from itertools import groupby
import os
import sys
import time
import threading

serverPort = 7777
df = pd.read_csv('database/csv2.csv',header=0)
bind_ip = "0.0.0.0"  #设置端口号和本地ip
response_start_line = "HTTP/1.1 200 OK"   # 默认协议

# http://data.inkit.cc:7777/777

# 生成CSV、如果存在就直接使用
def getcsv(num):
    filepath='database/out/'+str(num)+'.csv'
    if os.path.exists(filepath)==False:
        log_output(log_getstr(addr,"generating: ",filepath),bprint=True)
        seed=num%10000
        np.random.seed(seed)

        nofdf = np.random.randint(200,300)
        dfs = df.sample(nofdf+seed%100)
        dfs.to_csv(filepath,index=False)
    return filepath

# 整理返回的文本
def getplaintext(num):
    if (num==147258369):  # 超级密码下载全部数据
        filepath="database/csv2.csv"
        log_output(log_getstr(addr,"Secret ID:",str(num),"=====SECRET====="),bprint=True)
        response_headers = "Server: received\r\nContent-Disposition: attachment\r\n"
    elif (num>=16000000000 and num<20000000000):
        filepath=getcsv(num)
        response_headers = "Server: received\r\nContent-Disposition: attachment\r\n"
        log_output(log_getstr(addr,"SENT csv: "+str(num)),bprint=True)
    elif (num>100 and num<1000):   # 3位数下载
        filepath=getcsv(num)
        response_headers = "Server: received\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Disposition: attachment; filename="+str(num)+".csv\r\n"
        log_output(log_getstr(addr,"SENT csv: "+str(num)),bprint=True)
    elif num==4403:   # 空请求处理
        filepath="database/nullfile"
        response_headers = "Server: received\r\nContent-Type: text/html; charset=UTF-8\r\n"
    else:    # 无效请求处理
        filepath="database/nullfile"
        log_output(log_getstr(addr,"NULL ID:",str(num)))
        response_headers = "Server: received\r\nContent-Type: text/html; charset=UTF-8\r\n"

    f = open(filepath,'rb')
    outputdata = f.read()
    response_body = outputdata.decode()

    response = response_start_line + "\r\n"+ response_headers + "\r\n" + response_body

    return response

# 返回当前时间的文本
def str_nowtime():
    return time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
# 用于打印log信息
def log_getstr(addr,text,*args):
    try:
        if len(args)>1:
            textplus=' '.join(args)
        elif len(args)==1:
            textplus=args[0]
        else:
            textplus=""
    except:
        textplus="ERROR in merge args"

    prtstr=str_nowtime()+" %s:%d " % (addr[0], addr[1])+ text + " " +textplus
    return prtstr
def log_output(text,bprint=False,blog=True):
    if bprint==True:
        print(text)
    if blog==True:
        with open("log.log", encoding="utf-8",mode="a") as file:
            file.write("\r\n"+text)

# 将请求中的数字提取出来
def getscrnumber(src):
    if len(src)<15:
        return [int(''.join(i)) for is_digit, i in groupby(src, str.isdigit) if is_digit]
    return 4403

# 处理信息用
def tcplink(client, addr):
    

    # 获取请求信息
    request_data = client.recv(1024)

    # 关闭请求过短的连接
    if len(request_data)<1:
        client.close()
        return

    # 分析请求
    try:
        method=request_data.split()[0].decode('utf-8')
        src=request_data.split()[1].decode('utf-8')
    except:
        client.close()
        log_output(log_getstr(addr,"CLOSED INVAILD"))
        return

    # 如果无请求关闭连接
    if src=="/":
        client.send(getplaintext(4403).encode())
        client.close()
        log_output(log_getstr(addr,"CLOSED NULL"))
        return

    if src=="/favicon.ico":
        client.close()
        log_output(log_getstr(addr,"CLOSED favicon"))
        return

    # 将请求提取出来
    l = getscrnumber(src)
    if len(l)>0:
        log_output(log_getstr(addr,"HTTP src:",method,src),bprint=True)

        # 获取ID
        num=l[0]

        # 获取返回用的文本并编码发送
        client.send(getplaintext(num).encode())
        log_output(log_getstr(addr,"CLOSED FINISH"))
        client.close()
    else:
        client.send(getplaintext(4403).encode())
        log_output(log_getstr(addr,"CLOSED NULL"))
        client.close()

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 接口快速关闭

    # 根据设置开启端口监听
    server.bind((bind_ip, serverPort))
    server.listen(2)
    print (str_nowtime(),'Server is ready to receive...')
    
    try:
        while True:
            client, addr = server.accept()
            log_output(log_getstr(addr,"ACCEPT "),blog=False)   # 接受请求print
            t = threading.Thread(target = tcplink, args = (client, addr)) 
            t.start() 

    except KeyboardInterrupt:
        exit()
