# 针对该软件的图片处理算法
from mxml import MXml
from utils.fileAlgorithm import *
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import Qt, QRect


class imgAlgorithm:
    def __init__(self):
        pass

    @staticmethod
    def getFilledImage(img, item):
        return img.copy(int(item.scenePos().x()), int(item.scenePos().y()),
                        int(item.width), int(item.height))

    # @staticmethod
    # def cut_picture(img_path, save_path, sceneSize, items): #直接对scene得来的items进行切割
    #     #定义使用的变量
    #     save_path = os_path_join(save_path, 'img')
    #     sceneWidth = sceneSize[0]
    #     sceneHeight = sceneSize[1]
    #     img = QImage(img_path)
    #     ori_width,ori_height = img.width(),img.height()
    #     imgWidth = img.size().width()
    #     imgHeight = img.size().height()
    #     scaled_img = img.scaled(sceneWidth,sceneHeight)
    #     x_proportion = ori_width / sceneSize[0]
    #     y_proportion = ori_height / sceneSize[1]
    #     img_from = get_file_name(img_path)
    #     #条件判断处理
    #     ensure_dir_exist(save_path)
    #     #开始处理
    #     allFile = get_dir_all_file(save_path) #得到某目录下所有的完整文件名
    #     delete_name_image(allFile, img_from)   #删除特定名字的文件
    #     for ii, item in enumerate(items):
    #         path = os_path_join(save_path, item.text)
    #         if not os.path.exists(path):
    #             os.mkdir(path)
    #         index = get_index(path, img_from)
    #         cutImg = imgAlgorithm.getFilledImage(scaled_img,item)
    #         cutImg = cutImg.scaled(int(item.width * x_proportion), int(item.height * y_proportion))
    #         cutImg.save(os_path_join(save_path,item.text,img_from+ '-'+str(index)+'.jpg'))
    #     pass

    @staticmethod
    def cut_one_image(image_path, xml_path, img_root_name, save_root, real_time_cutting):
        """

        Args:
            image_path (str): 要切割的图片的绝对路径
            xml_path (str): 要切割的图片的对应xml文件
            img_root_name (str): 切割的子图片的保存名字的根部分，根部分+index就是切割后图片的名字
            save_root (str): 切割图片保存的根目录，保存结果会自动根据不同类别划分成不同子文件夹
            real_time_cutting (bool): 是否处于实时查重状态

        Returns:
            None
        """

        if real_time_cutting:
            images_info = {}
            img = QImage(image_path)
            xml_information = MXml(xml_path)
            boxes = xml_information.boxes
            img_width, img_height = xml_information.img_width, xml_information.img_height
            for box in boxes:
                x, y, width, height, categories_id, name = box[0], box[1], box[2], box[3], box[4], box[5]
                index = get_index(os_path_join(save_root, name), img_root_name)
                images_info[img_root_name + '_' + name + '_' + str(index) + '.jpg'] = [x, y]
                x *= img_width
                width *= img_width
                y *= img_height
                height *= img_height
                cutImg = img.copy(QRect(x, y, width, height))
                ensure_dir_exist(os_path_join(save_root, name))
                cutImg.save(os_path_join(save_root, name, img_root_name + '_' + name + '_' + str(index) + '.jpg'))

            return images_info

        else:
            img = QImage(image_path)
            all_file = get_dir_all_file(save_root)  # 得到某目录下所有的完整文件名
            # delete_name_image(all_file, img_root_name)  # 删除特定名字的文件
            xml_information = MXml(xml_path)
            boxes = xml_information.boxes
            img_width, img_height = xml_information.img_width, xml_information.img_height
            for box in boxes:
                x, y, width, height, categories_id, name = box[0], box[1], box[2], box[3], box[4], box[5]
                x *= img_width
                width *= img_width
                y *= img_height
                height *= img_height
                index = get_index(os_path_join(save_root, name), img_root_name)
                cutImg = img.copy(QRect(x, y, width, height))
                ensure_dir_exist(os_path_join(save_root, name))
                cutImg.save(os_path_join(save_root, name, img_root_name + '_' + name + '_' + str(index) + '.jpg'))
        pass
