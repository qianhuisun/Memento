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


"""
:result: the response from FacePlusPlus API.
:thresold: the threshold of new and old person.
:n: the number of faces to analyze.
"""
# return -1: the number of faces in result < n
# return 0: first n user_ids are various
# return min_confidence: first n user_ids are the same, but min_confidenece < threshold
# return user_id: when user_ids are the same and min_confidence > threshold
def analyze_result(result, threshold, n):
    first_user_id = ''
    min_confidence = 100
    for i in range(0, n):
        confidence = float(get_confidence(str(result)))
        if confidence == -1:
            return -1
        min_confidence = min(min_confidence, confidence)
        if i == 0:
            user_id_location, first_user_id = get_id(result)
        else:
            user_id_location, user_id = get_id(result)
            if user_id != first_user_id:
                return 0
        result = result[user_id_location+12:]
    if min_confidence > threshold:
        return first_user_id
    else:
        return min_confidence

# extract user id value from API response
def get_id(result):
    user_id_location = result.find('\'user_id\'')
    if user_id_location == -1:
        return -1
    user_id = result[user_id_location+12:user_id_location+32]
    return user_id_location, user_id.split('\'')[0]

# extract confidence value from API response
def get_confidence(result):
    confidence_location = result.find('\'confidence\'')
    if confidence_location == -1:
        return -1
    confidence = result[confidence_location+14:confidence_location+20]
    return confidence.split(',')[0]

# extract toke value from API response
def get_token(result):
    face_token_location = result.find('\'face_token\'')
    if face_token_location == -1:
        return -1
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
        self.new_root = 'new_images/'

    def image_to_token(self):
        print("Getting tokens of all images")

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
        print("Setting user id for all tokens")

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


    def delete_faceset(self):
        print("Deleting faceset")

        result = self.api.faceset.removeface(outer_id = "memento", face_tokens = "RemoveAllFaceTokens")
        print_result(printFuctionTitle("delete_face_response"), result)

        result = self.api.faceset.delete(outer_id = "memento")
        print_result(printFuctionTitle("delete_response"), result)


    def init_faceset(self):
        print("Initializing faceset")

        result = self.api.faceset.create(outer_id = "memento")
        print_result(printFuctionTitle("create_response"), result)

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
        print("Searching", image_path, "in the faceset")

        result = self.api.search(image_file = File(image_path), outer_id = "memento", return_result_count = 5)
        print_result(printFuctionTitle("response"), result)

        # analyze the result 
        user_id = analyze_result(str(result), 75.0, 3)
        print(printFuctionTitle("conclusion"))
        if user_id == -1:
            print("Error: Attempt to analyze more faces than the API returns!")
        elif user_id == 0:
            print("It's a new face. Please add a new face category into faceset!")
        elif isinstance(user_id, float):
            print("It's probably a new face, because the confidence is only", user_id)
        else:
            print("It's", user_id)
        print('\n')

    
    # e.g. folder_path = images/new_person_1
    def append_faceset(self, folder_path):
        print("Appending new face category into faceset")

        # grab all images, set their face_token and user_id, append them into faceset, and output local token_file
        all_folder_paths = glob.glob(os.path.join(self.new_root, '*'))
        name = get_name(all_folder_paths[0])
        #print(name)
        output_path = os.path.join(self.new_root, name, name+".txt")
        #print(output_path)
        token_file = open(output_path, 'w')
        all_image_paths = glob.glob(os.path.join(all_folder_paths[0], "*.jpg"))
        for i, image_path in enumerate(all_image_paths):
            result = self.api.detect(image_file = File(image_path))
            face_token = get_token(str(result))
            token_file.write(face_token+'\n')
            result = self.api.face.setuserid(face_token = face_token, user_id = name)
            #print(str(result))
            result = self.api.faceset.addface(outer_id = "memento", face_tokens = face_token)
            #print(str(result))
        token_file.close()

        
    def image_identification(self, image_path):
        print("Identifying", image_path)

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
            