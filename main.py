import sys
import memento


def init_faceset():
    memento_obj = memento.Memento()
    memento_obj.image_to_token()
    memento_obj.set_user_id()
    memento_obj.delete_faceset()
    memento_obj.init_faceset()


def detect_face():
    memento_obj = memento.Memento()
    memento_obj.search_faceset('./test_person_1.jpg')
    memento_obj.search_faceset('./test_person_2.jpg')


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'init':
        init_faceset()
    elif len(sys.argv) == 2 and sys.argv[1] == 'detect':
        detect_face()
    else:
        print('possible parameter: init, detect')
    #memento_obj.image_identification('./test_1.jpg')
    #memento_obj.image_identification('./test_2.jpg')