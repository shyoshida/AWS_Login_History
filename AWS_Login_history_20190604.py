import datetime
import boto3
import pprint
import time
import logging
import json
import os
import zlib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#slackurl = os.environ['slackurl']

#メイン処理
def lambda_handler(event, context):
    client = boto3.client('iam')
    Report_keys = []
    Unused_fields = []
    Nologin_fields = []
    while True:
        response = client.generate_credential_report()
        logger.info("Event: " + str(response))
        status = response['State']
        if   'COMPLETE' in status :
            break
        else:
            time.sleep(30)
    response = client.get_credential_report()
    Report = (response['Content']).decode('utf-8').split("\n")
    logger.info("Event: " + str(Report))
    for i in Report:
        if Report_keys == []:
            Report_keys = i.split(",")
        else:
            Report_dict = dict(zip(Report_keys, i.split(",")))
            Pw_lastused = DTTransfer(Report_dict['password_last_used'])
            Ak1_lastused = DTTransfer(Report_dict['access_key_1_last_used_date'])
            User_CreteTime = DTTransfer(Report_dict['user_creation_time'])
            Target = Report_dict['user']
            Pw_diff = DateDiff(Pw_lastused)
            key_diff = DateDiff(Ak1_lastused)
            User_diff = DateDiff(User_CreteTime)
            #rootアカウントの場合は次のループ
            if (Target == '<root_account>'):
            #if <root_account> not in Target:じゃだめ？continueもいらないきがするんだけど
            # 目的がなにか、となったときにroot_account以外を動かしたいならroot_accountを正とするよりもそれ以外をtureと見なすほうが良いかと。   
                continue
            else:
                #「nologin」所属している場合は次のループ
                user_groups = client.list_groups_for_user(
                    UserName = Target
                )
                for j in user_groups["Groups"]:
                    Exc_user = j['GroupName']
                    logger.info("Event: " + str(Exc_user))
                    if Exc_user == "nologin":
                        continue
                    #同上。
                    #1年以上ログインしていないアカウント判定
                    elif(Pw_diff >= 366 and key_diff >= 366  and User_diff >= 90):
                        #Add_nologin(Target)
                        temp_Nologin_json = [{
                        'title': 'Username',
                        'value': Target,
                        'short': True
                        }]
                        Nologin_fields = Nologin_fields + temp_Nologin_json
                    #作成してから90日以上ログインしていないアカウント判定
                    elif (Pw_diff >= 90 and key_diff >= 90 and User_diff >= 90):
                    #ログインが100日以上前でかつ利用していなくて90日経過したアカウントも対象になるからこのロジックはだめでしょ
                        #Add_nologin(Target)
                        temp_Unused_json = [{
                        'title': 'Username',
                        'value': Target,
                        'short': True
                        }]
                        Unused_fields = Unused_fields + temp_Unused_json
                    #それ以外のアカウントは何も処理しない
                    else:
                        pass
    #jsonテンプレート(1年以上利用のないユーザー)
    message_json = {
    'username': 'AWS Account info',
    'icon_emoji': ':awsicon:',
    'text': '1年以上利用のないユーザーです。',
    'attachments': [
    {
    'fallback': 'AWS Account Info',
    'color': 'warning',
    'fields': Nologin_fields
    }]}
    if Nologin_fields == []:
        pass
    else:
        logger.info("Event: " + str(message_json))
        slacknotification(message_json)
    #jsonテンプレート(90日以上利用のないユーザー)
    message_json = {
    'username': 'AWS Account info',
    'icon_emoji': ':awsicon:',
    'text': '90日以上利用のないユーザーです。',
    'attachments': [
    {
    'fallback': 'AWS Account Info',
    'color': 'warning',
    'fields': Unused_fields
    }]}
    if Unused_fields == []:
        pass
    else:
        logger.info("Event: " + str(message_json))
        slacknotification(message_json)

#Date変換処理
def DTTransfer(DTTransferDate):
    try:
        DTTransferDate = DTTransferDate[0:10]
        DTTransferDate = datetime.datetime.strptime(DTTransferDate,'%Y-%m-%d')
        return(datetime.date(DTTransferDate.year, DTTransferDate.month, DTTransferDate.day))
    except (ValueError):
        return("DTTransferDate_ERROR")

#日付差分計算
def DateDiff(CalculationDate):
    Reference_date = datetime.date.today()
    try:
        return((Reference_date - CalculationDate).days)
    except (TypeError):
        return(400)

#Slack通知処理
def slacknotification(message_json):
    req = Request(slackurl, json.dumps(message_json).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted.")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)

"""
#対象アカウントを「nologin」のみにする
def Add_nologin(Target):
    client = boto3.client('iam')
    user_groups = client.list_groups_for_user(
        UserName = Target
    )
    Pass_Reset(Target)
    for Remove_User in user_groups['Groups']:
        GroupName = Remove_User['GroupName']
        logger.info("Event: " + str(GroupName))
        client.remove_user_from_group(
            GroupName = GroupName,
            UserName = Target
        )
    client.add_user_to_group(
        GroupName = "nologin",
        UserName = Target
    )

#対象アカウントパスワード初期化
def Pass_Reset(Target)
    client = boto3.client('iam')
    client.update_login_profile(
        UserName = Target,
        Password = "Axis@User",
        PasswordResetRequired = True
    )
"""
event=""
context=""
lambda_handler(event,context)
