#!/usr/bin/python


import misaka
import os
import requests
import uuid
import re
from bs4 import BeautifulSoup


def get_files_list(dir):
    """
    获取一个目录下所有文件列表，包括子目录
    :param dir:
    :return:
    """
    files_list = []
    for root, dirs, files in os.walk(dir, topdown=False):
        for file in files:
            if os.path.splitext(file)[-1][1:] == 'md':
                files_list.append(os.path.join(root, file))

    return files_list


def get_pics_list(md_content):
    """
    获取一个markdown文档里的所有图片链接
    :param md_content:
    :return:
    """
    md_render = misaka.Markdown(misaka.HtmlRenderer())
    html = md_render(md_content)
    soup = BeautifulSoup(html, features='html.parser')
    pics_list = []
    for img in soup.find_all('img'):
        pics_list.append(img.get('src'))

    return pics_list

def md_img_find(md_file):
    '''
    将给定的markdown文件里的图片本地路径转换成网上路径
    '''
    post = None  # 用来存放markdown文件内容
    global total , success , failure , ignore
    with open(md_file, 'r',encoding='utf-8') as f: #使用utf-8 编码打开 by chalkit
        post = f.read()
        matches = re.compile('!\\[.*?\\]\\((.*?)\\)|<img.*?src=[\'\"](.*?)[\'\"].*?>').findall(post)     # 匹配md文件中的图片
        if matches and len(matches) > 0:
            for sub_match in matches:       # 正则里有个或，所以有分组，需要单独遍历去修改   
                for match in sub_match:     # 遍历去修改每个图片
                    #total = total+1
                    if match and len(match) > 0:
                        print("match pic : ", match)
                        if not re.match('((http(s?))|(ftp))://.*', match):  # 判断是不是一个图片的网址
                            print("not image http url : ", match)
                        else:
                            print('markdown文件中的图片用的是网址 ：', match)
                            imagename = match.split('/')[-1]
                            file_url = 'https://cdn.jsdelivr.net/gh/brokge/drawio/img/'+imagename+'.jpg' # transfer_online_img(match)  # 获取上传后的图片地址
                            if file_url:  # 在图片地址存在的情况下进行替换
                                print('图片地址是 ： ', file_url)
                                post = post.replace(match, file_url)  # 替换md文件中的地址
            #new_md_file = os.path.dirname(md_file)+"/"+os.path.basename(md_file)+"ed.md"
            if post: open(md_file, 'w',encoding='utf-8').write(post) #如果有内容的话，就直接覆盖写入当前的markdown文件
                                        #仍然注意用uft-8编码打开
    print ('Complete!')
    #print (' total   :%d' %(total))
    #print (' success :%d' %(success))
    #print (' failure :%d' %(failure))
    #print (' ignore  :%d' %(ignore))

def download_pics(url, file):
    """
    BCOOKIES = {
        "s_uid": "xxxxx",
        "s_exp": "14",
        "server_time": "1487816753"
    }
    ssrequest = requests.session()
    requests.utils.add_dict_to_cookiejar(ssrequest.cookies, BCOOKIES)
    """
    f=open(r'./cookie.txt','r')#打开所保存的cookies内容文件 
    cookies={}#初始化cookies字典变量 
    for line in f.read().split(';'):  #按照字符：进行划分读取 
        #其设置为1就会把字符串拆分成2份 
        name,value=line.strip().split('=',1) 
        cookies[name]=value #为字典cookies添加内容
    
    img_data = requests.get(url,cookies=cookies).content
    filename = os.path.basename(file)
    dirname = os.path.dirname(file)
    targer_dir = os.path.join(dirname, f'{filename}.assets')
    if not os.path.exists(targer_dir):
        os.mkdir(targer_dir)

    """
    with open(os.path.join(targer_dir, f'{uuid.uuid4().hex}.jpg'), 'w+') as f:
        f.buffer.write(img_data)
    """
    imagename = url.split('/')[-1]
    with open(os.path.join(targer_dir, f'{imagename}.jpg'), 'w+') as f:
        f.buffer.write(img_data)


if __name__ == '__main__':
    files_list = get_files_list(os.path.abspath(os.path.join('.', 'md')))

    for file in files_list:
        print(f'正在处理：{file}')

        with open(file, encoding='utf-8') as f:
            md_content = f.read()

        pics_list = get_pics_list(md_content)
        print(f'发现图片 {len(pics_list)} 张')

        for index, pic in enumerate(pics_list):
            print(f'正在下载第 {index + 1} 张图片...')
            download_pics(pic, file)
        print(f'下载处理完成。')
        md_img_find(file)
        print(f'文件替换完成。')


