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


def init_faceset():
    print("Initializing faceset")

    api = API()

    result = api.faceset.create(outer_id = "memento")
    print_result(printFuctionTitle("setuserid"), result)

    root_dir = 'images/'

    all_folder_paths = glob.glob(os.path.join(root_dir, '*'))

    for i, folder_path in enumerate(all_folder_paths):
        name = get_name(folder_path)
        token_path = os.path.join(root_dir, name, name+".txt")
        token_file = open(token_path, 'r')
        # add all tokens into the faceset
        while True:
            face_token = token_file.readline()[:-1]
            if not face_token:
                break
            # NOTE can upload 5 tokens at the same time
            result = self.api.faceset.addface(outer_id = "memento", face_tokens = face_token)
        token_file.close()