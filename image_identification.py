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


def get_confidence(result):
    face_token_location = result.find('\'confidence\'')
    confidence = result[face_token_location+14:face_token_location+20]
    return confidence.split(',')[0]


def get_token(result):
    face_token_location = result.find('\'face_token\'')
    return result[face_token_location+15:face_token_location+47]


def get_name(folder_path):
    return folder_path.split('\\')[-1]


def image_identification(image_path):
    print("Identifying", image_path)
    # 初始化对象，进行api的调用工作
    api = API()

    result = api.detect(image_file = File(image_path), return_attributes = "gender,age,smiling,headpose,facequality,"
                                                                                   "blur,eyestatus,emotion,ethnicity,beauty,"
                                                                                   "mouthstatus,skinstatus")
    face_token_1 = get_token(str(result))

    root_dir = 'images/'

    all_folder_paths = glob.glob(os.path.join(root_dir, '*'))

    max_confidence = 0.0
    max_confidence_name = ''

    for i, folder_path in enumerate(all_folder_paths):
        name = get_name(folder_path)
        token_path = os.path.join(root_dir, name, name+".txt")
        token_file = open(token_path, 'r')
        # get the average confidence of current person
        token_count = 0
        confidence_sum = 0
        while True:
            face_token_2 = token_file.readline()[:-1]
            if not face_token_2:
                break
            result = api.compare(face_token1 = face_token_1, face_token2 = face_token_2)
            confidence = float(get_confidence(str(result)))
            confidence_sum += confidence
            token_count += 1
        token_file.close()
        confidence_avrg = confidence_sum / token_count
        print("confidence of", name, "is", round(confidence_avrg, 2))
        if confidence_avrg > 70.0 and confidence_avrg > max_confidence:
            max_confidence = confidence_avrg
            max_confidence_name = name
    
    if max_confidence:
        print("This person is", max_confidence_name, "\n")
    else:
        print("Not matched!")
        