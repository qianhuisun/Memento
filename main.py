import memento

if __name__ == "__main__":
    memento_obj = memento.Memento()
    #memento_obj.image_to_token()
    #memento_obj.set_user_id()
    #memento_obj.init_faceset()
    memento_obj.search_faceset('./test_1.jpg')
    memento_obj.search_faceset('./test_2.jpg')
    #memento_obj.image_identification('./test_1.jpg')
    #memento_obj.image_identification('./test_2.jpg')