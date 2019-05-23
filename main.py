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
    memento_obj.init_faceset()


def detect_face(threshold):
    memento_obj = memento.Memento()
    last_res = ""
    while True:
        time.sleep(3)
        res = memento_obj.search_faceset(threshold)
        if res == last_res:
            continue
        else:
            URL = URL_PRE + res
            for i in range(0,5):
                requests.get(url = URL, params = PARAMS) 
            print(res)
            last_res = res
        

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == '-init':
        init_faceset()
    elif len(sys.argv) == 3 and sys.argv[1] == '-detect':
        detect_face(float(sys.argv[2]))
    else:
        print('possible parameter:\n -init\n -detect threshold')