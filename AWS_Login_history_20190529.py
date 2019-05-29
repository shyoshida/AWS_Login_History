import datetime
import boto3
import pprint
import datetime

#改善

client = boto3.client('iam')
CreateReport = client.generate_credential_report()
GetReport = client.get_credential_report()
GetReport_text = GetReport["Content"].decode().split("\n")
dt_now = datetime.date.today()

#取得したSTR型レポートをdict型に再構築
#listの5と11と3番目をdatatime型に変更
def Create_Report_Dict():
    global GetReport_list_values
    global GetReport_Dict
    i = 1
    GetReport_Dict = {}
    GetReport_list_keys = list(GetReport_text[0].split(","))
    GetReport_list_values = list(GetReport_text[i].split(","))
    for Report_values in GetReport_list_values:
        GetReport_list_values = list(GetReport_text[i].split(","))
        password_last_used = GetReport_list_values[4][0:10]
        ErrorDate1(password_last_used)
        access_key_1_last_used_date = GetReport_list_values[10][0:10]
        ErrorDate2(access_key_1_last_used_date)
        user_creation_time = GetReport_list_values[2][0:10]
        ConversionCreate_Date(user_creation_time)
        GetReport_Dict["userdata"] = dict(zip(GetReport_list_keys, GetReport_list_values))
#        pprint.pprint(GetReport_Dict)
        Compose_Report_Date(GetReport_Dict)
        i = i + 1
    return(GetReport_Dict)

#dict型にしたレポートを使用してAWSグループを移動させる処理
def Compose_Report_Date(GetReport_Dict):
    global Compose_Pass_Used
    global Compose_Key_Used
    global Compose_Create_Date
    Compose_Pass_Used = GetReport_Dict["userdata"]["password_last_used"]
    Compose_Key_Used = GetReport_Dict["userdata"]["access_key_1_last_used_date"]
    Compose_Create_Date = GetReport_Dict["userdata"]["user_creation_time"]
    ErrorCompose_Pass(Compose_Pass_Used)
    ErrorCompose_Keys(Compose_Key_Used)
    if (type(Date_Result_Pass) == int and Date_Result_Pass >= 3 and type(Date_Result_Keys) == int and Date_Result_Keys >= 3):
        #AWSグループを"nologin"に移動させる処理
        pass
    elif (Date_Result_Pass  == "None" and Date_Result_Keys == "None"):
        #CreateDateと今日の日付を計算して90以上か判定
        Create_Date_Result = (dt_now - Compose_Create_Date).days
        if Create_Date_Result >= 90:
            #AWSグループを"nologin"に移動させる処理
            print(GetReport_Dict["userdata"]["user"])
            print(Create_Date_Result)
        else:
            pass
    else:
        pass

#dict型レポート作成時に「password_last_used」がstr型からdatetime型に変更する処理
#N/Aが存在するため例外で"None"を入力
def ErrorDate1(password_last_used):
    try:
        dt = datetime.datetime.strptime(password_last_used, '%Y-%m-%d')
        GetReport_list_values[4] = datetime.date(dt.year, dt.month, dt.day)
    except (ValueError):
        GetReport_list_values[4] = "None"

#dict型レポート作成時に「access_key_1_last_used_date」がstr型からdatetime型に変更する処理
#N/Aが存在するため例外で"None"を入力
def ErrorDate2(access_key_1_last_used_date):
    try:
        dt = datetime.datetime.strptime(access_key_1_last_used_date, '%Y-%m-%d')
        GetReport_list_values[10] = datetime.date(dt.year, dt.month, dt.day)
    except (ValueError):
        GetReport_list_values[10] = "None" 

#dict型レポート作成時に「user_creation_time」がstr型からdatetime型に変更する処理
def ConversionCreate_Date(user_creation_time):
    dt = datetime.datetime.strptime(user_creation_time, '%Y-%m-%d')
    GetReport_list_values[2] = datetime.date(dt.year, dt.month, dt.day)

#366日以上passwordを使用していないユーザーを計算
#"None"の文字列は計算できないので例外で対応
def ErrorCompose_Pass(Compose_Pass_Used):
    try:
        global Date_Result_Pass
        Date_Result_Pass = (dt_now - Compose_Pass_Used).days
    except (TypeError):
        Date_Result_Pass = "None"

#366日以上passwordを使用していないユーザーを計算
#"None"の文字列は計算できないので例外で対応
def ErrorCompose_Keys(Compose_Key_Used):
    try:
        global Date_Result_Keys
        Date_Result_Keys = (dt_now - Compose_Key_Used).days
    except (TypeError):
        Date_Result_Keys = "None"




Create_Report_Dict()




#評価
