import sys
import memento
import time


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
        time.sleep(2)
        res = memento_obj.search_faceset('./test_person_2.jpg', threshold)
        if res == last_res:
            continue
        else:
            print(res)
            last_res = res
        


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == '-init':
        init_faceset()
    elif len(sys.argv) == 3 and sys.argv[1] == '-detect':
        detect_face(float(sys.argv[2]))
    else:
        print('possible parameter:\n -init\n -detect threshold')