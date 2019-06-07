import os
import shutil
import sys
import memento
import time
import requests

URL_PRE = "http://eecs338.herokuapp.com/setname/"
PARAMS = {'address':'Northwestern'} 

def init_faceset():
    memento_obj = memento.Memento()
    memento_obj.image_to_token()
    memento_obj.set_user_id()
    memento_obj.delete_faceset()
    memento_obj.create_faceset()


def rollback_faceset():
    memento_obj = memento.Memento()
    memento_obj.delete_faceset()
    memento_obj.create_faceset()


def clean_new_images():
    new_root = 'new_images/'
    if os.path.exists(new_root):
        shutil.rmtree(new_root)
    os.mkdir(new_root)


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
    if len(sys.argv) == 2 and sys.argv[1] == '-init':
        init_faceset()
    elif len(sys.argv) == 2 and sys.argv[1] == '-rollback':
        rollback_faceset()
    elif len(sys.argv) == 2 and sys.argv[1] == '-clean':
        clean_new_images()
    elif len(sys.argv) == 3 and sys.argv[1] == '-d':
        detect_face(float(sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == '-dwa':
        detect_face_with_append(float(sys.argv[2]))
    else:
        print('possible parameter:\n -init\n -rollback\n -clean\n -d threshold\n -dwa threshold')