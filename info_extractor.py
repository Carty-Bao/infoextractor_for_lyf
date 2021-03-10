#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : sentencesplit.py
# @Author: bjd
# @Date  : 2021/3/09
# @Desc  :关键词获取

import os
import json
import csv
import pandas as pd
import requests

#百度智能云的Key
#可以自己简历账号，发送url请求，百度智能云提供500000次免费分析
APIKey='Hxb5emqvWQ2m8GLm5bV2U7f5'
SecretKey='b07f4c3WWVH4HLrTLNQucylU44SK4Ef3'

def uni_list():
    '''
    将大学分成两个列表，分别存储985大学和211大学
    考虑到简历中可能不写括号的情况，所以将有括号的211学校中的括号删除
    例如：中国矿业大学（北京）->中国矿业大学

    函数返回值为两个列表，uni985和uni211
    '''
    uni985 = []
    uni211 = []
    with open('985211.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0]:
                uni985.append(row[0])
            if row[1]:
                uni211.append(row[1])
    return uni985, uni211

def delete_nb(filename):
    '''
    本函数的功能为将过于牛逼的删除，例如独立董事

    输入参数：后缀为csv的文件名
    '''
    data = pd.read_csv(filename)

    row_indexs = data[data["职位_Position"]=="独立董事"].index

    data.drop(row_indexs, inplace=True)

    data.to_csv("maninfo.csv",sep=',', index=False, header=False)

def save_json(json_data, name):
    '''
    为了多次测试某一样本，将baiduapi返回的json文件转换为字符串保存
    输入参数1:返回好的json_data
    输入参数2:保存的文件名，一般采用人名来保存
    '''
    name = 'names/'+name + '.json'             #当前目录下简历 /names 文件夹，将json文件保存到该文件夹中
    f2 = open(name, 'w')                    #打开一个只写文件
    f2.write(json.dumps(json_data))         #这句话的功能是将json文件默认的字典结构转换为字符串，否则保存不上
    f2.close()

def read_json(name):
    '''
    读取保存好的json文件，返回值为一个人的个人简介
    输入参数：文件名，一般采用人名
    输出：读取好的json_data
    '''
    name = 'names/'+name + '.json'
    f = open(name, 'r')                             #只读
    json_data = f.read()
    json_data = json.loads(json_data)               #这句话的功能是将字符串转换为json文件默认的字典结构
    return json_data
#创建请求url
def get_url():
    '''
    创建url请求，利用词法分析，将句子拆分
    返回：url的地址
    '''
    url=0
    #通过API Key和Secret Key获取access_token
    AccessToken_url='https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(APIKey,SecretKey)
    res = requests.post(AccessToken_url)#推荐使用post
    json_data = json.loads(res.text)

    if not json_data or 'access_token' not in json_data:
        print("获取AccessToken的json数据失败")
    else:
        accessToken=json_data['access_token']
        #将得到的access_token加到请求url中
        url='https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?charset=UTF-8&access_token={}'.format(accessToken)
    return url
#创建请求，获取数据
def get_tag(url,text):
    '''
    给url发送简介，之后url以json文件的形式返回这个句子的词法分析
    输入参数1:使用get_url得到的url地址
    输入参数2:大佬的个人简介文本
    返回：词法分析的json文件
    '''
    #创建Body请求
    body={
        "text" : text
    }
    body2 = json.dumps(body)#将字典形式的数据转化为字符串,否则报错
    #创建Header请求
    header={
        'content-type': 'application/json'
    }
    res = requests.post(url,headers=header,data=body2)# 推荐使用post
    json_data = json.loads(res.text)
    if not json_data or 'error_code' in json_data:
        print("获取关键词的Json数据失败")
    else:
        return json_data

def detect_uni_level(pure_words):
    '''
    在文本中查找大学的名字

    基本逻辑为：先从词中找到关键字“毕业”，在关键词附近进行搜索，搜索方式为顺序搜索，找到”大学“”学院“关键字，即为毕业院校

    输入：拆分好的个人简介，存入列表
    输出1:大学名字
    输出2:是不是985
    输出3:是不是211
    '''
    scholar = ''
    uni985, uni211 = uni_list()
    #查找大学
    for index, word in enumerate(pure_words):
        if "毕业" in word:
            for uni in pure_words[index-2:index+5]:
                if ("大学" in uni) or ("学院" in uni):
                    scholar = uni
                    break
    if scholar == '':
        degrees = ['学士', '硕士', '博士']
        for index, word in enumerate(pure_words):
            for degree in degrees:
                if degree in word:
                    for uni in pure_words[index-2:index+5]:
                        if ("大学" in uni) or ("学院" in uni):
                            scholar = uni  
                            break
    if scholar == '':
        scholar = 'Unknown'
                    
    #查找985211
    level_985 = scholar in uni985
    level_211 = scholar in uni211
    return scholar, level_985, level_211
    
def mba_expeience(pure_words):
    '''
    判断mba和emba，管理学学习经历
    基本逻辑为，在文本中找到MBA，EMBA字眼
    找到“管理”字眼，并临近匹配学位，顺序匹配
    输入：pure_words
    输出1:是否有mba
    输出2:是否有emba
    输出3:是否有管理学学习经历
    '''
    mba_tf = ("MBA" in pure_words) or ("mba" in pure_words)
    emba_tf =  ("EMBA" in pure_words) or ("emba" in pure_words)
    man_tf = False
    for index, word in enumerate(pure_words):
        if "管理" in word:
            for title in pure_words[index-2:index+3]:
                if ("硕士" in title) or ("博士" in title) or ("工商" in title):
                    man_tf = True
                    break
    return mba_tf, emba_tf, man_tf

def manage_exp(pure_words):
    '''
    判断是否有管理经验
    在简介中检测下面词汇，如果存在，则认为有该经历
    可以在列表中添加相关职位的词汇
    输入：pure_words
    输出：是否有管理经验
    '''
    management_experience = False
    management_words = ["董事", "经理", "总裁", "部长", "主席", "监事", "主任", "总监"]
    for index, word in enumerate(pure_words):
        for position in management_words:
            if position in word:
                management_experience = True
                break
    return management_experience

def clean_sentence(json_data):
    '''
    清洗无关词汇
    将delete_list里面的词汇清洗掉
    输入：json_data
    输出1:pure_words,列表里存放分割好的，清洗好的词汇
    输出2:clean_words,存放词汇的其他信息
    '''
    clean_words = []#存放词汇的完整信息
    pure_words = []#只存放相关词汇
    delete_list = ['f', 's', 't', 'a', 'ad', 'q', 'r', 'p', 'c', 'u', 'w', 'vn', 'd']
    info_list = json_data['items']
    for index, item in enumerate(info_list):
        if item["pos"] not in delete_list:
            clean_words.append(item)
            pure_words.append(item['item'])
    return clean_words, pure_words

if __name__ == '__main__':
    
    count = 1

    f = open("extract_info.csv", 'w', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(["姓名", "毕业学校", "是否985", "是否211", "是否mba", "是否emba", "是否管理学经历", "是否有管理经验"])

    with open('maninfo.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            count+=1
            ###########################################################
            #打开文件，只保存名字和简介信息
            #由于文件太大，一次只保存一个人的名字和信息
            name = row[0]
            text = row[2]
            print(name)

            ###########################################################
            #发送url并获取json文件，使用人名保存json文件
            url=get_url()
            json_data = get_tag(url, text)
            save_json(json_data, name)

            ###########################################################
            #初始化列表
            json_data = read_json(name)

            ##########################################################
            #清洗无关词汇
            clean_words, pure_words = clean_sentence(json_data)

            ###########################################################
            #查找大学,  查找985211
            scholar, level_985, level_211 = detect_uni_level(pure_words)
            print(scholar)
            print("是否985:")
            print(level_985)
            print("是否211:")
            print(level_211)

            ###########################################################
            #工商管理经历
            mba_tf, emba_tf, man_tf = mba_expeience(pure_words)
            print("mba经历： ")
            print(mba_tf)
            print("emba经历： ")
            print(emba_tf)
            print("管理学位： " )
            print(man_tf)

            ############################################################
            #管理经历
            management_experience = manage_exp(pure_words)
            print("管理经历： ")
            print(manage_exp)

            #############################################################
            #将判断结果写入新的csv
            writer.writerow([name, scholar, level_985, level_211, mba_tf, emba_tf, man_tf, management_experience])
            if count>5:
                break

