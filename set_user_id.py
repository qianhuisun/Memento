import os
import glob
# import PythonSDK
from PythonSDK.facepp import API,File
# 导入系统库并定义辅助函数
from pprint import pformat


# 此方法专用来打印api返回的信息
def print_result(hit, result):
    print(hit)
    print('\n'.join("  " + i for i in pformat(result, width=75).split('\n')))


def printFuctionTitle(title):
    return "\n"+"-"*60+title+"-"*60


def get_name(folder_path):
    return folder_path.split('\\')[-1]


def set_user_id():
    print("Setting user id for all tokens")
    # 初始化对象，进行api的调用工作
    api = API()

    root_dir = 'images/'

    all_folder_paths = glob.glob(os.path.join(root_dir, '*'))

    max_confidence = 0.0
    max_confidence_name = ''

    for i, folder_path in enumerate(all_folder_paths):
        name = get_name(folder_path)
        token_path = os.path.join(root_dir, name, name+".txt")
        token_file = open(token_path, 'r')
        # set user id for all the tokens
        while True:
            face_token = token_file.readline()[:-1]
            if not face_token:
                break
            result = api.face.setuserid(face_token = face_token, user_id = name)
        token_file.close()