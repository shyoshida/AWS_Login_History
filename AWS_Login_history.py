import datetime
import boto3
import pprint
import datetime

client = boto3.client('iam')
response = client.list_users()
dt_now = datetime.datetime.now()

#ユーザー一覧から各種データ取得
def Axisuser():
    global Axisuser_UserName
    global Axisuser_CreateDate
    global Axisuser_PasswordLastUsed

    for Axis_list1 in response["Users"]:
        Axisuser_UserName = Axis_list1["UserName"]
        Axisuser_CreateDate_str = getValueFromUser(Axis_list1,"CreateDate")[0:10]
        Axisuser_PasswordLastUsed_str = getValueFromUser(Axis_list1,"PasswordLastUsed")[0:10]
        Axisuser_CreateDate = datetime.datetime.strptime(Axisuser_CreateDate_str, '%Y-%m-%d')
        Axisuser_PasswordLastUsed = datetime.datetime.strptime(Axisuser_PasswordLastUsed_str, '%Y-%m-%d')
        print(Axisuser_UserName)
        dt = dt_now - Axisuser_PasswordLastUsed
        print(dt)
    return ()

#一度もログインされていないアカウントエラー対応
def getValueFromUser(Axis_list1,key):
    try:
        return str(Axis_list1[key])
    except (KeyError):
        return '1000-01-01'



Axisuser()

#評価
#意図としては例外処理のほうが処理が重くならずに書ける。
#エラー構文で'none'を使うと計算ができなくなる。
#それならif文で'none'のときの処理を書いたほうが柔軟に対応できる。