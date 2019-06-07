import os
import glob
import shutil
from PythonSDK.facepp import API,File
from pprint import pformat


"""
(Copied from Face++ API Demo)
(Used to print Face++ API response)
hit: a tile, usually the request name.
result: the response message.
"""
def print_result(hit, result):
    print(hit)
    print('\n'.join("  " + i for i in pformat(result, width = 75).split('\n')))


"""
(Copied from Face++ API Demo)
(Used to print request name)
title: the request name.
"""
def printFuctionTitle(title):
    return "-" * 60 + title + "-" * 60


"""
result: the response from Face++ API.
thresold: the threshold of new and old person.
n: the number of faces to analyze.
"""
# Analyze the response from Face++ and return accordingly.
# Serve as a helper function of Memento.search_faceset().
"""
# return -1: insufficient faces, i.e. number of faces in result < n
# return 0: first n user_ids are not the same
# return min_confidence: first n user_ids are the same, but min_confidenece < threshold
# return user_id: when user_ids are the same and min_confidence > threshold
"""
def analyze_result(result, threshold, n):
    first_user_id = ''
    min_confidence = 100
    for i in range(0, n):
        confidence = float(get_confidence(str(result)))
        if confidence == -1:
            return -1
        min_confidence = min(min_confidence, confidence)
        print("Debug info: ", min_confidence, end = " ")
        if i == 0:
            user_id_location, first_user_id = get_id(result)
            print(first_user_id)
        else:
            user_id_location, user_id = get_id(result)
            print(user_id)
            if user_id != first_user_id:
                return 0
        result = result[user_id_location+12:]
    if min_confidence >= threshold:
        return first_user_id
    else:
        return min_confidence


"""
result: the response from Face++ API.
"""
# Extract the user_id value from API response.
# Serve as a helper function to analyze_result().
def get_id(result):
    user_id_location = result.find('\'user_id\'')
    if user_id_location == -1:
        return -1
    user_id = result[user_id_location+12:user_id_location+32]
    return user_id_location, user_id.split('\'')[0]


"""
result: the response from Face++ API.
"""
# Extract the value of confidence from API response.
# Serve as a helper function to analyze_result().
def get_confidence(result):
    confidence_location = result.find('\'confidence\'')
    if confidence_location == -1:
        return -1
    confidence = result[confidence_location+14:confidence_location+20]
    return confidence.split('.')[0]


"""
result: the response from Face++ API.
"""
# Extract face_token value from API response.
# Used by several functions of Memento.
def get_token(result):
    face_token_location = result.find('\'face_token\'')
    if face_token_location == -1:
        return -1
    return result[face_token_location+15:face_token_location+47]


"""
result: the response from Face++ API.
"""
# Extract the name from the folder path, which will be used as user_id.
# Used by several functions of Memento.
def get_name(folder_path):
    folder_path = folder_path.replace('\\', '/')
    return folder_path.split('/')[-1]

"""
High level functionalities:
1. manage image data and face tokens locally;
2. interact with Face++ APIs to train models, get names of faces, and update models;
3. send result of recognition to  web server.
"""
class Memento(object):

    def __init__(self):  
        """
        api: An object of FacePlusPlus API.
        original_root: The relative directory path of training images.
        new_root: The relative directory path of new face images.
        webcam_root: The relative directory path of images taken by Rpi.
        """
        self.api = API()
        self.original_root = 'original_images/'
        self.new_root = 'new_images/'
        self.webcam_root = '../webcam/'


    # Get face_token for all training images
    def image_to_token(self):
        print("Getting tokens for images...")

        all_folder_paths = glob.glob(os.path.join(self.original_root, '*'))

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            #print(name)
            output_path = os.path.join(self.original_root, name, name+".txt")
            #print(output_path)
            output_file = open(output_path, 'w')
            all_image_paths = glob.glob(os.path.join(folder_path, "*.jpg"))
            #print(all_image_paths)
            for j, image_path in enumerate(all_image_paths):
                result = self.api.detect(image_file = File(image_path))
                #print(str(result))
                face_token = get_token(str(result))
                #print(face_token)
                output_file.write(face_token+'\n')
            output_file.close()

        print("Getting tokens done.")


    # Combine user_id and face_token for all training images
    def set_user_id(self):
        print("Setting user_id for images...")

        all_folder_paths = glob.glob(os.path.join(self.original_root, '*'))

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            token_path = os.path.join(self.original_root, name, name+".txt")
            token_file = open(token_path, 'r')
            # set user_id for all face_token
            while True:
                face_token = token_file.readline()[:-1]
                if not face_token:
                    break
                result = self.api.face.setuserid(face_token = face_token, user_id = name)
            token_file.close()

        print("Setting user_id done.")


    # Delete the new face images stored locally
    def clean_new_images(self):
        print("Cleaning new images...")

        if os.path.exists(self.new_root):
            shutil.rmtree(self.new_root)
        os.mkdir(self.new_root)

        print("Cleaning new images done.")


    # Delete the faceset (trained model) in Face++ server
    def delete_faceset(self):
        print("Deleting faceset...")

        if os.path.exists(self.new_root):
            shutil.rmtree(self.new_root)
        os.mkdir(self.new_root)

        result = self.api.faceset.removeface(outer_id = "memento", face_tokens = "RemoveAllFaceTokens")
        #print_result(printFuctionTitle("delete_face_response"), result)

        result = self.api.faceset.delete(outer_id = "memento")
        #print_result(printFuctionTitle("delete_faceset_response"), result)

        print("Deleting faceset done.")


    # Create a faceset (train a model) in Face++ server with face_tokens of training images
    def create_faceset(self):
        print("Creating faceset...")

        result = self.api.faceset.create(outer_id = "memento")
        #print_result(printFuctionTitle("create_faceset_response"), result)

        all_folder_paths = glob.glob(os.path.join(self.original_root, '*'))

        for i, folder_path in enumerate(all_folder_paths):
            name = get_name(folder_path)
            token_path = os.path.join(self.original_root, name, name+".txt")
            token_file = open(token_path, 'r')
            # Add all face_tokens into the faceset
            tokens = ""
            while True:
                face_token = token_file.readline()[:-1]
                if not face_token:
                    break
                tokens = tokens + face_token + ","
            if tokens != "":
                tokens = tokens[:-1]
            print("Debug info: Adding Person", i)
            print(tokens)
            # NOTE can upload 5 tokens at the same time
            result = self.api.faceset.addface(outer_id = "memento", face_tokens = tokens)
            token_file.close()

        print("Creating faceset done.")


    # Search for faces in images from Rpi camera writing folder.
    """
    # return "no_face": when helper function analyze_result() returns -1
    # return "new_face": when helper function analyze_result() returns 0 or a float
    # return user_id: when helper function analyze_result() returns a string
    """
    def search_faceset(self, threshold):
        #print("Searching", image_path, "in the faceset...")

        # Read the first file in the Rpi camera folder.
        # Avoid reading temporary image file end with "~"
        image_path = ""
        while True:
            image_path = sorted(glob.glob(os.path.join(self.webcam_root, '*')))[0]
            if image_path[-1] == '~':
                print("Debug info: File ends with ~. Read again...")
            else:
                break 

        # Make a copy to ../backup directory.
        if not os.path.exists('../backup'):
            #print("creating folder")
            os.mkdir('../backup')
        shutil.copy(image_path, '../backup/tmp.jpg')

        print("Debug info: Detecting " + image_path)

        # Use search() of Face++ API
        # Can get at most 5 most similar face_tokens in the response message.
        result = self.api.search(image_file = File('../backup/tmp.jpg'), outer_id = "memento", return_result_count = 5)
        #print_result(printFuctionTitle("response"), result)

        # Analyze the response message.
        # (the 3rd '2' parameter indicates the first 2 face's user_id must be the same)
        user_id = analyze_result(str(result), threshold, 2)
        #print(printFuctionTitle("conclusion"))
        if user_id == -1:
            #print("Error: Attempt to analyze more faces than the API returns!")
            return "no_face"
        elif user_id == 0:
            #print("It's a new face.")
            #name = input("Please give a name: ")
            #self.fetch_images(name)
            #self.append_faceset(name)
            return "new_face"
        elif isinstance(user_id, float):
            #print("It's probably a new face, confidence: ", user_id)
            #name = input("Please give a name: ")
            #self.fetch_images(name)
            #self.append_faceset(name)
            return "new_face"
            #return "new_face_confidence_" + str(user_id)
        else:
            #print("It's", user_id)
            return user_id

        #print("Searching done.")


    """
    name: the new person's name
    """
    # Fetch images from Rpi camera folder and save them in folder (named by 'name') within new face images directory
    def fetch_images(self, name):
        if not os.path.exists(self.new_root):
            os.mkdir(self.new_root)
        dirName = self.new_root + name
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        image_path = glob.glob(os.path.join('../backup', "*.jpg"))[0]
        for j in range(1,6):
            shutil.copyfile(image_path, dirName+"/"+str(j)+".jpg")


    """
    name: the new person's name
    """
    # Append a new face category with 'name' as user_id into the faceset (trained model) in Face++ server.
    def append_faceset(self, name):
        #print("Appending new face category into faceset...")

        # Grab all images, set their face_token and user_id, append them into faceset, and output local token_file
        dirName = self.new_root + name
        output_path = os.path.join(dirName, name+".txt")
        token_file = open(output_path, 'w')
        all_image_paths = glob.glob(os.path.join(dirName, "*.jpg"))
        tokens = ""
        for i, image_path in enumerate(all_image_paths):
            result = self.api.detect(image_file = File(image_path))
            face_token = get_token(str(result))
            token_file.write(face_token+'\n')
            result = self.api.face.setuserid(face_token = face_token, user_id = name)
            #print(str(result))
            tokens = tokens + face_token + ","
        if tokens != "":
            tokens = tokens[:-1]
        # NOTE can upload 5 tokens at the same time
        result = self.api.faceset.addface(outer_id = "memento", face_tokens = tokens)
        token_file.close()
        
        #print("Appending done.")
