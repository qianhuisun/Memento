import os
import shutil
import sys
import memento
import time
import requests

URL_PRE = "http://eecs338.herokuapp.com/setname/"
PARAMS = {'address':'Northwestern'} 


# Train a model on Face++ server with the training image data.
def init_faceset():
    memento_obj = memento.Memento()
    memento_obj.image_to_token()
    memento_obj.set_user_id()
    memento_obj.delete_faceset()
    memento_obj.create_faceset()


# (must be run after “-init”) Delete all the new face categories in the model on Face++ server.
def rollback_faceset():
    memento_obj = memento.Memento()
    memento_obj.delete_faceset()
    memento_obj.create_faceset()


# Delete all the new face images locally.
def clean_new_images():
    memento_obj = memento.Memento()
    memento_obj.clean_new_images()


# Detect faces in images periodically and try to return names they belong to.
def detect_face(threshold):
    memento_obj = memento.Memento()
    new_person_counter = 0
    last_res = ""
    while True:
        time.sleep(5)
        print("Debug info: Fetch a picture and search for a face...")
        res = memento_obj.search_faceset(threshold)
        if res == last_res:
            print("Debug info: Same as the last one")
            continue
        else:
            URL = URL_PRE + res
            # post detection result to web server 5 times
            for i in range(0,5):
                requests.get(url = URL, params = PARAMS) 
            print("Debug info: " + res)
            last_res = res


# Detect faces periodically and appends new face categories into our database and model on Face++ server.
def detect_face_with_append(threshold):
    memento_obj = memento.Memento()
    new_person_counter = 0
    last_res = ""
    while True:
        time.sleep(5)
        print("Debug info: Fetch a picture and search for a face...")
        res = memento_obj.search_faceset(threshold)
        if res == last_res:
            print("Debug info: Same as the last one")
            continue
        else:
            if res == "new_face" and new_person_counter < 20:
                new_person_counter += 1
                new_name = "new_person_"+ str(new_person_counter)
                URL = URL_PRE + "adding_" + new_name
                # post detection result to web server 5 times
                for i in range(0,5):
                    requests.get(url = URL, params = PARAMS) 
                print("Debug info: adding_" + new_name)
                memento_obj.fetch_images(new_name)
                memento_obj.append_faceset(new_name)
                URL = URL_PRE + new_name + "_added"
                # post detection result to web server 5 times
                for i in range(0,5):
                    requests.get(url = URL, params = PARAMS) 
                print("Debug info: " + new_name + "_added")
            else:
                URL = URL_PRE + res
                # post detection result to web server 5 times
                for i in range(0,5):
                    requests.get(url = URL, params = PARAMS) 
                print("Debug info: " + res)
                last_res = res
        

if __name__ == "__main__":
    # Train a model on Face++ server with the training image data.
    if len(sys.argv) == 2 and sys.argv[1] == '-init':
        init_faceset()
    # (must be run after “-init”) Delete all the new face categories in the model on Face++ server.
    elif len(sys.argv) == 2 and sys.argv[1] == '-rollback':
        rollback_faceset()
    # Delete all the new face images locally.
    elif len(sys.argv) == 2 and sys.argv[1] == '-clean':
        clean_new_images()
    # Detect faces in images periodically and try to return names they belong to.
    elif len(sys.argv) == 3 and sys.argv[1] == '-d':
        detect_face(float(sys.argv[2]))
    # Detect faces periodically and add new face categories into our database and model on Face++ server.
    elif len(sys.argv) == 3 and sys.argv[1] == '-d' and sys.argv[2] == '-a':
        detect_face_with_append(float(sys.argv[2]))
    else:
        print('possible parameter:\n -init\n -rollback\n -clean\n -d x    (x stands for threshold of confidence [0,100])\n -d -a x (x stands for threshold of confidence [0,100])')