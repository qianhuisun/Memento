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


def get_token(result):
    face_token_location = result.find('\'face_token\'')
    return result[face_token_location+15:face_token_location+47]


def get_name(folder_path):
    return folder_path.split('\\')[-1]


def image_to_token():
    # 初始化对象，进行api的调用工作
    api = API()

    root_dir = 'images/'

    all_folder_paths = glob.glob(os.path.join(root_dir, '*'))

    for i, folder_path in enumerate(all_folder_paths):
        name = get_name(folder_path)
        output_path = os.path.join(root_dir, name, name+".txt")
        output_file = open(output_path, 'w')
        all_image_paths = glob.glob(os.path.join(folder_path, "*.jpg"))
        #print(all_image_paths)
        for j, image_path in enumerate(all_image_paths):
            result = api.detect(image_file = File(image_path), return_attributes = "gender,age,smiling,headpose,facequality,"
                                                                                   "blur,eyestatus,emotion,ethnicity,beauty,"
                                                                                   "mouthstatus,skinstatus")
            #print(str(result))
            face_token = get_token(str(result))
            #print(face_token)
            output_file.write(face_token+'\n')
        output_file.close()
