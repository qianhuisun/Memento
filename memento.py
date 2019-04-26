import os
import glob
# import PythonSDK
from PythonSDK.facepp import API,File
from pprint import pformat


# print FacePlus Plus API response
def print_result(hit, result):
    print(hit)
    print('\n'.join("  " + i for i in pformat(result, width = 75).split('\n')))

# format the headerline
def printFuctionTitle(title):
    return "-" * 60 + title + "-" * 60


# extract confidence value from API response
def get_confidence(result):
    face_token_location = result.find('\'confidence\'')
    confidence = result[face_token_location+14:face_token_location+20]
    return confidence.split(',')[0]

# extract toke value from API response
def get_token(result):
    face_token_location = result.find('\'face_token\'')
    return result[face_token_location+15:face_token_location+47]

# get the name of a person by the folder path
def get_name(folder_path):
    return folder_path.split('\\')[-1]


class Memento(object):

    def __init__(self):  
        """
        :api: An object of FacePlusPlus API.
        :root: The relative path of images repositery.
        """
        self.api = API()
        self.root = 'images/'

    def image_to_token(self):
        print("\nGetting tokens of all images")

        all_folder_paths = glob.glob(os.path.join(self.root, '*'))

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            output_path = os.path.join(self.root, name, name+".txt")
            output_file = open(output_path, 'w')
            all_image_paths = glob.glob(os.path.join(folder_path, "*.jpg"))
            #print(all_image_paths)
            for j, image_path in enumerate(all_image_paths):
                #result = self.api.detect(image_file = File(image_path), return_attributes = "gender,age,smiling,"
                #                                                                    "emotion,ethnicity,beauty,"
                #                                                                    "mouthstatus,skinstatus")
                result = self.api.detect(image_file = File(image_path))
                #print(str(result))
                face_token = get_token(str(result))
                #print(face_token)
                output_file.write(face_token+'\n')
            output_file.close()


    def set_user_id(self):
        print("\nSetting user id for all tokens")

        all_folder_paths = glob.glob(os.path.join(self.root, '*'))

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            token_path = os.path.join(self.root, name, name+".txt")
            token_file = open(token_path, 'r')
            # set user id for all tokens
            while True:
                face_token = token_file.readline()[:-1]
                if not face_token:
                    break
                result = self.api.face.setuserid(face_token = face_token, user_id = name)
            token_file.close()


    def init_faceset(self):
        print("\nInitializing faceset")

        result = self.api.faceset.create(outer_id = "memento")
        print_result(printFuctionTitle("setuserid"), result)

        all_folder_paths = glob.glob(os.path.join(self.root, '*'))

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            token_path = os.path.join(self.root, name, name+".txt")
            token_file = open(token_path, 'r')
            # add all tokens into the faceset
            while True:
                face_token = token_file.readline()[:-1]
                if not face_token:
                    break
                # NOTE can upload 5 tokens at the same time
                result = self.api.faceset.addface(outer_id = "memento", face_tokens = face_token)
            token_file.close()


    def search_faceset(self, image_path):
        print("\nSearching", image_path, "in the faceset")

        result = self.api.search(image_file = File(image_path), outer_id = "memento", return_result_count = 5)
        print_result(printFuctionTitle("search"), result)


    def image_identification(self, image_path):
        print("\nIdentifying", image_path)

        result = self.api.detect(image_file = File(image_path), return_attributes = "gender,age,smiling,headpose,facequality,"
                                                                                    "blur,eyestatus,emotion,ethnicity,beauty,"
                                                                                    "mouthstatus,skinstatus")
        face_token_1 = get_token(str(result))

        all_folder_paths = glob.glob(os.path.join(self.root, '*'))

        max_confidence = 0.0
        max_confidence_name = ''

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            token_path = os.path.join(self.root, name, name+".txt")
            token_file = open(token_path, 'r')
            # get the average confidence of current person
            token_count = 0
            confidence_sum = 0
            while True:
                face_token_2 = token_file.readline()[:-1]
                if not face_token_2:
                    break
                result = self.api.compare(face_token1 = face_token_1, face_token2 = face_token_2)
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
            