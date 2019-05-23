import os
import glob
import shutil

# get the name of a person
def get_name(image_path):
    image_path = image_path.replace('\\', '/')
    for i in range(2,6):
        image_path = image_path.replace(str(i), '')
    return image_path.split('/')[-1].split('.')[0]

def extend_to_five(src):
    all_image_paths = glob.glob(os.path.join(src, "*.jpg"))
    print(all_image_paths)
    for i, image_path in enumerate(all_image_paths):
        print(image_path)
        name = get_name(image_path)
        print(name)
        for j in range(2,6):
            if os.path.exists(src+name+str(7-j)+".jpg"):
                continue
            else:
                print("Creating"+src+name+str(7-j)+".jpg")
                shutil.copyfile(src+name+".jpg", src+name+str(7-j)+".jpg")


def init_image_folder(src, dst):
    all_image_paths = glob.glob(os.path.join(src, "*.jpg"))
    for i, image_path in enumerate(all_image_paths):
        name = get_name(image_path)
        if not os.path.exists("original_images/"+name):
            os.mkdir("original_images/"+name)
        shutil.copy(image_path, "original_images/"+name)


#extend_to_five("Classmates/")
#init_image_folder("Classmates/", "original_images/")