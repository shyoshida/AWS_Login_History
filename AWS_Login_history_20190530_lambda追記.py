import datetime
import boto3
import pprint
import datetime

#改善

client = boto3.client('iam')
CreateReport = client.generate_credential_report()
GetReport = client.get_credential_report()
dt_now = datetime.date.today()

#認証情報レポート辞書作成（メイン処理）
def lambda_handler(event,context):
    global GetReport_Dict
    i = 1
    GetReport_Dict = {}
    GetReport_text = GetReport["Content"].decode().split("\n")
    GetReport_list_keys = list(GetReport_text[0].split(","))
    GetReport_list_values = list(GetReport_text[i].split(","))
    for Report_values in GetReport_list_values:
        Report_values = list(GetReport_text[i].split(","))
        try:
            dt_password_last_used = datetime.datetime.strptime(Report_values[4][0:10], '%Y-%m-%d')
            Report_values[4] = datetime.date(dt_password_last_used.year, dt_password_last_used.month, dt_password_last_used.day)
        except (ValueError):
            Report_values[4] = "None"
        try:
            dt_key_last_used = datetime.datetime.strptime(Report_values[10][0:10], '%Y-%m-%d')
            Report_values[10] = datetime.date(dt_key_last_used.year, dt_key_last_used.month, dt_key_last_used.day)
        except (ValueError):
            Report_values[10] = "None"
        dt_user_creation_time = datetime.datetime.strptime(Report_values[2][0:10], '%Y-%m-%d')
        Report_values[2] = datetime.date(dt_user_creation_time.year, dt_user_creation_time.month, dt_user_creation_time.day)
        GetReport_Dict["userdata"] = dict(zip(GetReport_list_keys, Report_values))
        Compose_Report_Date(GetReport_Dict)
        i = i + 1        
    return(GetReport_Dict)

#アカウント未使用判定
def Compose_Report_Date(GetReport_Dict):
    global Move_Target
    Compose_Pass_Used = GetReport_Dict["userdata"]["password_last_used"]
    Compose_Key_Used = GetReport_Dict["userdata"]["access_key_1_last_used_date"]
    Compose_Create_Date = GetReport_Dict["userdata"]["user_creation_time"]
    try:
        Date_Result_Pass = (dt_now - Compose_Pass_Used).days
    except (TypeError):
        Date_Result_Pass = "None"
    try:
        Date_Result_Keys = (dt_now - Compose_Key_Used).days
    except (TypeError):
        Date_Result_Keys = "None"
    if (type(Date_Result_Pass) == int and Date_Result_Pass >= 366 and type(Date_Result_Keys) == int and Date_Result_Keys >= 366):
        Move_Target = GetReport_Dict["userdata"]["user"]
        AWS_Group_Add_nologin(Move_Target)
    elif (Date_Result_Pass  == "None" and Date_Result_Keys == "None"):
        Create_Date_Result = (dt_now - Compose_Create_Date).days
        if Create_Date_Result >= 90:
            Move_Target = GetReport_Dict["userdata"]["user"]
            AWS_Group_Add_nologin(Move_Target)
        else:
            pass
    else:
        pass

#AWSグループ移動判定
def AWS_Group_Add_nologin(Move_Target):
    user = client.list_groups_for_user(
        UserName = Move_Target
    )
    for Remove_User in user['Groups']:
        GroupName = Remove_User['GroupName']
        try:
            delete_user_from_group = client.remove_user_from_group(
                GroupName = GroupName,
                UserName = Move_Target
                )
        except:
            Add_User = client.add_user_to_group(
            GroupName = "nologin",
            UserName = Move_Target
            )
    Add_User = client.add_user_to_group(
        GroupName = "nologin",
        UserName = Move_Target
    )


lambda_handler(event,context)