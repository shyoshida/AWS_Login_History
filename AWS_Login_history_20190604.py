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
#テスト用SlackURL
slackurl = "https://hooks.slack.com/services/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"
#webhockURLを書いたものをGitにアップしたらいたずらされちゃうよ？

def lambda_handler(event, context):
    client = boto3.client('iam')
    Report_keys = []
    Unused_fields = []
    Nologin_fields = []
    while True:
        response = client.generate_credential_report()
        logger.info("Event: " + str(response))
        #loggingしなくていいの？処理失敗した時になにが起こったのか追えないよ？
        status = response['State']
        if   'COMPLETE' in status :
            break
        else:
            time.sleep(30)
    response = client.get_credential_report()
    Report = (response['Content']).decode('utf-8').split("\n")
    logger.info("Event: " + str(Report)) 
    #loggingしなくていいの？処理失敗した時になにが起こったのか追えないよ？   
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
            if(Pw_diff >= 366 and key_diff >= 366 and not User_diff >= 90):
                #同じ条件式を多重にelifするのは芸がないのでもうちょっと工夫しましょう。
                #root_accountのif文はいいと思うけど入れる場所を変えるともっと良くなる。
                if Target == '<root_account>':
                    pass
                elif User_diff >= 90:
                    user_groups = client.list_groups_for_user(
                        UserName = Target
                    )
                    for j in user_groups["Groups"]:
                        Exc_user = j['GroupName']
                        if Exc_user == "nologin":
                            continue
                        #Add_nologin(Target)
                        temp_Nologin_json = [{
                        'title': 'Username',
                        'value': Target,
                        'short': True
                        }]
                        Nologin_fields = Nologin_fields + temp_Nologin_json
                elif Pw_diff >= 90 and key_diff >= 90:
                    user_groups = client.list_groups_for_user(
                        UserName = Target
                    )
                    for j in user_groups["Groups"]:
                        Exc_user = j['GroupName']
                        if Exc_user == "nologin":
                            continue
                        #Add_nologin(Target)
                        temp_Unused_json = [{
                        'title': 'Username',
                        'value': Target,
                        'short': True
                        }]
                        Unused_fields = Unused_fields + temp_Unused_json
                else:
                    pass
    message_json = {
    'username': 'AWS Account info',
    'icon_emoji': ':awsicon:',
    'text': '1年以上ログインのないユーザーです。',
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
        #ここのlogingはお好み  
        slacknotification(message_json)
    message_json = {
    'username': 'AWS Account info',
    'icon_emoji': ':awsicon:',
    'text': '90日以上ログインのないユーザーです。',
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
        #ここのlogingはお好み       
        slacknotification(message_json)


def DTTransfer(DTTransferDate):
    try:
        DTTransferDate = DTTransferDate[0:10]
        DTTransferDate = datetime.datetime.strptime(DTTransferDate,'%Y-%m-%d')
        return(datetime.date(DTTransferDate.year, DTTransferDate.month, DTTransferDate.day))
    except (ValueError):
        return("DTTransferDate_ERROR")

def DateDiff(CalculationDate):
    Reference_date = datetime.date.today()
    try:
        return((Reference_date - CalculationDate).days)
    except (TypeError):
        return(400)

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
#nologin移動
def Add_nologin(Target):
    user_groups = client.list_groups_for_user(
        UserName = Target
    )
#パスワード初期化
#    client.update_login_profile(
#        UserName = ,
#        Password = ,
#        PasswordResetRequired = True
#    )
    for Remove_User in user_groups['Groups']:
        GroupName = Remove_User['GroupName']
        if GroupName == "nologin":
            pass
        else:
            #ここでGroupName==nologinの判定しているのであれば、else:でtry/exceptの処理をやるべきでは？
        try:
            client.remove_user_from_group(
                GroupName = GroupName,
                UserName = Target
                )
        except:
            client.add_user_to_group(
            GroupName = "nologin",
            UserName = Target
            )
        #try/exceptで書くのはよくない。nologinか否かの判定を事前に実行しているのだから、そのうえで書きましょう。
    client.add_user_to_group(
        GroupName = "nologin",
        UserName = Target
    )
    #nologinGroupへ追加する処理が重複している。工夫しましょう。
"""

event=""
context=""
lambda_handler(event,context)