import os.path
import shutil
import time
from mxml import MXml
from ui.mainwindow import Ui_MainWindow
from ui.bloodcellcount import bloodcellcountUI
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QPen, QColor, QTransform, QDropEvent, QDragEnterEvent, QIcon, QScreen
from PyQt5.QtWidgets import *
from utils.imgAlgorithm import imgAlgorithm
from utils.patientdataload import *
from itemBase.sceneBase import SceneBase
from itemBase.lastImageSceneBase import LastImageSceneBase
from itemBase.wholeImageSceneBase import WholeImageSceneBase
from itemBase.itemBase import ItemBase
from itemBase.listWidgetItem import ListWidgetItem
from threadBase.cameraBase import CameraThread
from threadBase.recheckBase import RecheckThread
from threadBase.splicingBase import SplicingThread
from threadBase.realTimeBase import RealTimeAlgorithm
from config import *
from utils.utils import cv_imread, countFile
from utils import get_code
from getCutImgDialog import CutImgDialog

import logging

logger = logging.getLogger("root.mainWindow")

class Mainwindow(QMainWindow):
    def __init__(self, parent=None):
        super(Mainwindow, self).__init__(parent)
        # 初始化ui、config
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.config = Config(os.path.join(os.getcwd(), 'setting.ini'))
        self.config.parent = self
        self.ui.scene = SceneBase(self)  # 为了统一ui的widget，全放在uItemBasei里面，这里是动态赋属性
        self.ui.last_img_scene = LastImageSceneBase(self)
        self.ui.whole_img_scene = WholeImageSceneBase(self)
        self.image_recheck = RecheckThread()
        self.image_splicing = SplicingThread()
        self.current_image = None
        self.set_mode_changeable_flag(True)
        # 自动检测导入
        self.intelligent_algorithm = None
        try:
            from intelligent import Intelligent
            self.intelligent_algorithm = Intelligent()
        except BaseException:
            logger.error("load intelligent algorithm error")
            pass
        # 设置可以接受拖入，同时graphics设为不可接受
        self.setAcceptDrops(True)
        self.ui.graphicsView.setAcceptDrops(False)
        # 全局链接函数
        self.connetever()
        pass

    def register(self):
        flag = False
        self.config.now_time = int(time.time())
        now_time = str(self.config.now_time)
        self.config.load_code()
        if self.config.register_code is not None:
            try:
                inf = get_code.des_decrypt('scnuscnu', b''.join([bytes([int(i)]) for i in self.config.register_code]))
                inf = str(inf)[2:-1].split('_')
            except :
                pop_warning_dialog(self, '密匙被非法更改！请重置软件！')
                self.config.legal_flag = False
            else:
                [password, register_time, limit_time, last_time] = inf
                if int(last_time) > int(now_time):
                    pop_prompt(self, '非法更改时间，软件重置')
                    self.reply_to_factory_settings()
                    self.config.legal_flag = False
                else:
                    if int(register_time) + int(limit_time)*24*3600 > int(now_time):
                        flag = get_code.check_the_password(password, register_time)
                    else:
                        pop_prompt(self, '软件激活时间过期，请重新激活！')
                        self.config.legal_flag = False
        else:
            result = pop_register_dialog(self, get_code.get_base_code(now_time))
            if result is not None:
                [password, limit_time] = result
                if int(limit_time) >= 100 :
                    pop_prompt(self, '试用期软件上限为100天，请重新设置！')
                    flag = self.register()
                else:
                    flag = get_code.check_the_password(password, now_time)
                    if flag:
                        inf = '_'.join([password, now_time, limit_time, now_time])
                        secret_bytes = get_code.des_encrypt('scnuscnu', inf)
                        secret_list = []
                        for each in secret_bytes:
                            secret_list.append(int(each))
                        self.config.register_code = secret_list
        return flag

    def showMaximized_and_iocn(self):
        desktop = QApplication.desktop()
        rect = desktop.frameSize()
        self.resize(QSize(rect.width(),rect.height()))
        self.setWindowIcon(QIcon('1.ico'))

    def connetever(self):
        # 所有的文件树操作
        self.file_tree_set()
        # 所有的信号链接操作
        self.connect_signal()
        # 所有的点击操作
        self.connect_clicked()
        # graphics设置
        self.graphics_setting()
        pass

    def connect_signal(self):
        # scene信号连接函数
        self.ui.scene.wheelSignal.connect(self.wheel_slot)
        self.ui.scene.createItemSignal.connect(self.create_item_slot)
        self.ui.scene.changeItemSignal.connect(self.change_item_slot)
        self.ui.scene.endItemSignal.connect(self.end_item_slot)

        # 连接listWidget里面用户使用菜单进行新增、重命名、删除操作时候的信号到这里的函数，达到响应处理
        self.ui.nameList.append_item_signal.connect(self.list_widget_append_item_slot)
        self.ui.nameList.rename_item_signal.connect(self.list_widget_rename_item_slot)
        self.ui.nameList.delete_item_signal.connect(self.list_widget_delete_item_slot)
        self.ui.nameList.currentItemChanged.connect(self.list_widget_current_item_change_slot)

        self.ui.fileTreeWidget.show_item_signal.connect(self.file_tree_show_item_slot)
        self.ui.fileTreeWidget.star_items_signal.connect(self.file_tree_star_items_slot)
        self.ui.fileTreeWidget.remove_item_signal.connect(self.file_tree_remove_item_slot)
        self.ui.fileTreeWidget.rename_item_signal.connect(self.file_tree_rename_item_slot)

        self.ui.findTreeWidget.show_item_signal.connect(self.file_tree_show_item_slot)
        self.ui.findTreeWidget.star_items_signal.connect(self.file_tree_star_items_slot)
        self.ui.findTreeWidget.remove_item_signal.connect(self.file_tree_remove_item_slot)
        self.ui.findTreeWidget.rename_item_signal.connect(self.file_tree_rename_item_slot)
        self.ui.starTreeWidget.show_item_signal.connect(self.file_tree_show_item_slot)

        # 摄像机（image_thread）的信号连接在“开始记录”按钮函数中
        # self.image_thread.imageSignal.connect(self.image_callback)
        # self.image_thread.cameralabelSignal.connect(self.set_camera_label)

        # 查重和自动拼接完成信号连接
        self.image_recheck.finishSignal.connect(self.recheck_finish)
        self.image_splicing.finishSignal.connect(self.splicing_finish)

        # 切换模式信号连接
        self.ui.comboBox.currentTextChanged.connect(self.mode_change_slot)
        pass

    def connect_clicked(self):
        # 所有的按键连接
        self.ui.pushButton_start_end.clicked.connect(self.record_botton)
        self.ui.pushButton_stop.clicked.connect(self.stop_save_botton)
        self.ui.find_file_enter_button.clicked.connect(self.find_file_button_slot)
        self.ui.detect_button.clicked.connect(self.auto_detect_slot)
        self.ui.import_star_action.triggered.connect(self.import_star_slot)
        self.ui.export_star_action.triggered.connect(self.export_star_slot)
        self.ui.open_dir_action.triggered.connect(self.open_dir_slot)
        self.ui.fresh_button.clicked.connect(lambda: self.mode_change_slot('Fresh'))
        self.ui.open_img_action.triggered.connect(self.open_image_slot)
        self.ui.root_directory_act.triggered.connect(self.open_root_slot)
        self.ui.set_save_file_act.triggered.connect(self.set_record_save_path)
        self.ui.back_to_start_act.triggered.connect(self.reply_to_factory_settings)
        self.ui.generate_repoter_act.triggered.connect(self.open_report_slot)
        self.ui.export_cutting_act.triggered.connect(self.cut_img_slot)
        self.ui.create_new_patient_act.triggered.connect(self.create_new_patient_dir_slot)
        self.ui.camera_setting_action.triggered.connect(self.open_camera_setting_slot)
        self.ui.observe_mode_action.toggled.connect(lambda checked: setattr(self.config, 'observe_check', checked))
        self.ui.whole_map_action.toggled.connect(lambda checked: setattr(self.config, 'whole_map_check', checked))
        self.ui.real_time_recheck_action.toggled.connect(
            lambda checked: setattr(self.config, 'real_time_recheck', checked))
        self.ui.pre_button.clicked.connect(lambda: self.turn_page_slot(-1))
        self.ui.next_button.clicked.connect(lambda: self.turn_page_slot(1))

        self.ui.detect_button.setShortcut('x')
        pass

    #######################################################文件树的操作#################################################

    def file_tree_set(self):
        self.ui.fileTreeWidget.set_other_tree_widgets([self.ui.starTreeWidget, self.ui.findTreeWidget])
        pass

    def file_tree_init(self, root_path):
        # 根据root_path重置文件树tabWidget，只能综合模式用
        if root_path is not None:
            self.ui.fileTreeWidget.clear()
            self.ui.findTreeWidget.clear()
            self.ui.starTreeWidget.clear()
            self.ui.fileTreeWidget.reset()
            self.ui.findTreeWidget.reset()
            self.ui.starTreeWidget.reset()
            self.ui.fileTreeWidget.load_project_structure(root_path)
        else:
            pass
        pass

    def file_tree_refresh(self):
        # 刷新子树，主要是根据病人目录刷新filetree,只能记录模式用
        self.ui.fileTreeWidget.clear()
        self.ui.findTreeWidget.clear()
        self.ui.starTreeWidget.clear()
        self.ui.fileTreeWidget.reset()
        self.ui.findTreeWidget.reset()
        self.ui.starTreeWidget.reset()

        record_save_path = self.config.record_save_path
        if record_save_path is None:
            pop_prompt(self, '未选择病人目录')
        else:
            self.ui.fileTreeWidget.load_project_structure(record_save_path)
        pass

    def file_tree_show_item_slot(self, img_path):
        if not Path(img_path).suffix in get_image_extensions():
            pop_warning_dialog(self, '选择的文件不是图片')
            return
        self.show_one_image(img_path)
        pass

    def find_file_button_slot(self):
        text = self.ui.find_file_line_edit.text()
        res = self.ui.findTreeWidget.show_find_items([text])
        if not res:
            pop_warning_dialog(self, "未找到符合的图片")
        pass

    def show_all_file_slot(self):
        self.ui.fileTreeWidget.show_extensions_files(None)
        pass

    def file_tree_star_items_slot(self, current_indexes):
        self.ui.starTreeWidget.add_items_by_indexes(current_indexes)
        pass

    def file_tree_remove_item_slot(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        pass

    def file_tree_rename_item_slot(self, old_path: str, new_path: str, img_new_name: str):
        # 将xml文件也跟着改名
        root = self.config.file_tree_root
        rel_image_path = os_path_relpath(old_path, root)
        rel_xml_path = rel_image_path.replace('images', 'xmls', 1).rsplit('.', maxsplit=1)[-2] + '.xml'
        old_xml_path = os_path_join(root, rel_xml_path)
        xml_new_name = img_new_name.rsplit('.')[0] + '.xml'
        new_xml_path = os_path_join(os_path_dirname(old_xml_path), xml_new_name)

        os.rename(old_path, new_path)
        os.rename(old_xml_path, new_xml_path)
        # scene的img也要变
        scene = self.ui.scene
        scene.img_path = new_path
        self.show_one_image(new_path)
        # 把xml里面的file_path改成新的
        MXml.change_file_path(new_xml_path)
        pass

    def export_star_slot(self):
        # 导出收藏文件
        xml_save_path = pop_save_file_dialog(self)
        if xml_save_path is None:
            return
        img_paths = self.ui.starTreeWidget.current_star_items_path()
        MXml.export_star_xml(xml_save_path, img_paths)
        pass

    def import_star_slot(self):
        # 导入收藏文件
        # TODO 目前可能会导入重名文件，因此需要更改导入形式
        xml_path = pop_file_dialog(self, 'file', 'import xml file')
        if xml_path is None:
            return
        paths = MXml.import_star_xml(xml_path)
        find_indexes = self.ui.fileTreeWidget.find_items_by_paths(paths)
        self.ui.starTreeWidget.add_items_by_indexes(find_indexes)
        self.config.file_tree_import_xml = xml_path

        # 手动遍历切换到收藏tab
        for i in range(self.ui.fileTreeTabWidget.count()):
            text = self.ui.fileTreeTabWidget.tabText(i)
            if text == '收藏':
                self.ui.fileTreeTabWidget.setCurrentIndex(i)
                break
        pass

    def list_widget_delete_item_slot(self, class_name):
        # 接收到删除信号后删除config里面的对应类别
        self.config.delete_cls(class_name)
        pass

    def list_widget_append_item_slot(self, class_name, RGB, row):
        # 接收到增加信号后在config里面新增类别
        self.config.add_cls(class_name, RGB, row)
        pass

    def list_widget_rename_item_slot(self, old_name, new_name):
        # 接收到重命名信号后在config里面重命名类别
        self.config.rename_cls(old_name, new_name)
        pass

    def list_widget_current_item_change_slot(self, current: QListWidgetItem, previous: QListWidgetItem):
        # 接收到当前选择更改信号后更新被选择的框的类别显示
        text = current.text()
        color = self.config.info_dict.get_color_by_clsName(text)
        items = self.ui.scene.selectedItems()
        self.ui.scene.change_item_attributes(items, text=text, pen=QPen(QColor(color[0], color[1], color[2])))
        pass

    def recovery_list_widget(self):
        # 从config恢复退出保存的数据
        color_set = self.config.info_dict.clsName2color
        cls_name2id = self.config.info_dict.clsName2id
        for cls in cls_name2id:
            color = QColor(color_set[cls][0], color_set[cls][1], color_set[cls][2])
            item = ListWidgetItem.create_item(cls, color)
            self.ui.nameList.add_item(item)
        pass

    ###################################################菜单栏操作#########################################################

    def open_root_slot(self):
        # 点击选择根目录那个action的槽函数
        root_path = pop_file_dialog(self, 'dir', '选择根目录')
        if root_path is None:
            return

        if pop_question(self, '是否创建新的病人目录？'):
            inf = pop_get_patient_inf_dialog(self)
            if inf is not None:
                create_new_patient(root_path, inf)
                pass

        self.config.file_tree_root = root_path
        mode = self.ui.comboBox.currentText()
        if mode == '综合模式':
            self.file_tree_init(root_path)
        # if self.config.index is not None:
        #     self.update_scene_image()
        pass

    def create_new_patient_dir_slot(self):
        # 创建新病人
        root_path = self.config.file_tree_root
        mode = self.ui.comboBox.currentText()
        if root_path is None:
            pop_prompt(self, '请先选择根目录')
        else:
            patient_inf = pop_get_patient_inf_dialog(self)
            if patient_inf is not None:
                [patient_name, patient_gender, patient_age, patient_bed, patient_take_pack, patient_picture_number] = patient_inf
                if (patient_name is '') or (patient_gender is '') or (patient_age is '') or (patient_bed is '') or (patient_take_pack is '') or (patient_picture_number is ''):
                    pop_prompt(self, '请输入病人的完整信息！')
                    return
                inf = "".join([patient_name, '-', patient_gender, '-', patient_age, '-', patient_bed, '-', patient_take_pack, '-', patient_picture_number])
                # 根据根目录和病人信息创建新病人
                create_new_patient(root_path, inf)
                if mode == '综合模式':
                    self.file_tree_init(root_path)
                else:
                    return

    def open_camera_setting_slot(self):
        inf= pop_camera_setting_dialog(self)
        if inf is not None:
            self.config.camera_inf = inf
            pop_prompt(self, '相机设置成功')
        pass

    def set_record_save_path(self):
        # 选择病人目录
        if self.config.file_tree_root is None:
            pop_prompt(self, '请先选择根目录')
        else:
            _record_patient = pop_file_dialog(self, 'dir', '选择图像保存文件夹')
            if _record_patient is None:
                return

            record_patient = path_preprocess(_record_patient)
            if self.config.file_tree_root in record_patient:
                record_save_path = os_path_join(record_patient, 'images')
                if 'images' in record_patient:
                    mode = self.ui.comboBox.currentText()
                    self.config.record_save_path = record_patient
                    self.config.process_save_path = self.config.record_save_path.replace('images', 'process')
                    if not os.path.exists(self.config.process_save_path):
                        os.mkdir(self.config.process_save_path)
                    information = record_patient.split('/')[-2]
                    if information == 'images':
                        information = record_patient.split('/')[-3]
                    text = "".join(['当前保存路径：', information])
                    self.ui.label_current_save.setText(text)
                    self.config.inf = information
                    if mode == '记录模式':
                        self.file_tree_refresh()
                elif os.path.exists(record_save_path):
                    mode = self.ui.comboBox.currentText()
                    self.config.record_save_path = record_save_path
                    self.config.process_save_path = self.config.record_save_path.replace('images', 'process')
                    information = record_save_path.split('/')[-2]
                    text = "".join(['当前保存路径：', information])
                    self.ui.label_current_save.setText(text)
                    self.config.inf = information
                    if mode == '记录模式':
                        self.file_tree_refresh()
                else:
                    pop_prompt(self, '选择的文件不合规范，请选择病人文件夹或者病人文件夹下的"images"文件夹')
                    return
            else:
                pop_warning_dialog(self, '图片保存路径必须在根目录下，请重新选择')

        pass

    def reply_to_factory_settings(self):
        ####清空ini文件####
        self.config.__init__()
        if os.path.exists("setting.ini"):
            os.remove('setting.ini')
        # self.config.legal_flag = False
        pass

    def open_report_slot(self):
        # 生成检测报告
        if self.config.inf is None or self.config.record_save_path is None:
            pop_prompt(self, '未选择病人')
        else:
            category_path = self.config.record_save_path.replace('images', 'categories')
            category_path_is_exists = os.path.exists(category_path)
            if not category_path_is_exists:
                pop_prompt(self, '该病人没有类别文件夹，请创建类别文件')
                return
            inf = self.config.inf.split('-')
            inf.append(get_time())
            patient_info = inf
            if len(os.listdir(category_path)) == 0 :
                pop_prompt(self, '请先切割图片')
                return

            arr_info = get_arr(category_path)
            # cell_number是一个36乘2的二维数组，包含36种细胞的血片、髓片的数量
            # 其中36种细胞按照表格上的顺序，31种需要计数的细胞，4种巨核细胞，还有退化细胞的血片、髓片的数量，退化细胞和细胞总数自动计算
            cell_number = arr_info[0]
            # cell_percent是一个31乘2的二维数组，包含31种需要计数的细胞的血片髓片的百分比,需要乘100的
            cell_percent = arr_info[1]
            self.bcsgui = bloodcellcountUI(patient_info)
            # self.bcsgui.left_button_2.clicked.connect(self.save_report)
            self.bcsgui.show()
            self.bcsgui.update_countdata(cell_number, cell_percent)

    pass

    def save_report(self):
        save_path = self.config.record_save_path.replace('/images', '')
        name = '检测报告.jpg'
        path = os.path.join(save_path,name)
        if os.path.exists(path):
            i = 1
            while True:
                if i == 1:
                    path = path[:-4] + str(i) + path[-4:]
                else:
                    if i == 10:
                        pop_prompt(self, '只能保存9个检测报告')
                        return
                    path = path[:-5] + str(i) + path[-4:]
                flag = os.path.exists(path)
                if flag:
                    i += 1
                    continue
                else:
                    break
        QScreen.grabWindow(QApplication.primaryScreen(), QApplication.desktop().winId()).save(path)
        pop_prompt(self, '保存成功')

    def cut_img_slot(self):
        # 打开选择切割图片的窗口进行手动选择切割
        if self.config.file_tree_root is None:
            pop_warning_dialog(self, "当前根目录为空")
            return

        dialog = CutImgDialog(self.ui.fileTreeWidget, self)
        if dialog.exec() == QDialog.Accepted:
            image_paths = dialog.result_paths
            save_root = dialog.ui.save_root_line_edit.text()
            if save_root == "默认保存于所选病人的categories文件夹，如需改动点击右边的按键选择路径" :
                save_root = os.path.join(self.config.file_tree_root,
                                        image_paths[0].split('/')[-3],
                                        "categories") 
                pass
            self.cut_images(image_paths, save_root)
            pop_prompt(self, "切割完成")
            self.recheck(save_root, mode='普通查重')
            self.mode_change_slot('Fresh')
        else:
            return

    def recheck(self, path, mode: str):
        # 所有查重都要经过这个函数
        self.image_recheck.path = path
        self.image_recheck.mode = mode
        self.image_recheck.start()
        pass

    # TODO 优化代码待做
    def recheck_finish(self, repeat_imgaes: list, mode):
        if mode == '自动识别查重':
            error_images = []
            for pair in repeat_imgaes:
                cat = set()
                for i in range(len(pair)):
                    cat.add(pair[i].split('/')[-2])
                    if len(cat) == 2:
                        error_images.append(pair)
            self.change_scence_items(error_images)
            self.config.cell_sum -= len(repeat_imgaes)
            self.image_recheck.sum = 0
            pass

        elif mode == '普通查重':
            show_in_find_widget = []
            for pair in repeat_imgaes:
                cat = set()
                for i in range(len(pair)):
                    cat.add(pair[i].split('/')[-2])
                if len(cat) == 1:
                    for i in range(len(pair) - 1):
                        if os.path.exists(pair[i]):
                            os.remove(pair[i])
                else:
                    for item in pair:
                        show_in_find_widget.append(item.split('/')[-1])
                    text = ''.join(['以下图片重复！请检查类别(已显示在查找栏)', '\n', '\n'
                                       , '\n————————————————————————————————————————\n'.join(pair)])
                    pop_prompt(self, text)
            self.ui.findTreeWidget.show_find_items(show_in_find_widget)

    # TODO 代码优化
    def change_scence_items(self, error_images):
        # 实时改变当前显示的框和xml文件
        real_time = str(self.config.real_time)
        images_info = self.config.images_info
        image_path = self.config.real_time_image_path
        xml_path = self.get_save_xml_path(image_path)
        process_path = self.config.process_save_path

        for pair in error_images:
            QApplication.processEvents()
            if real_time in pair[0]:
                new_class = pair[1].split('/')[-2]
                new_id = self.get_key_form_id2cls_name(new_class)
                basename = os.path.basename(pair[0])
                idx = images_info[basename]
                RealTimeAlgorithm.change_error_xml(new_id, new_class, idx, xml_path)
            elif real_time in pair[1]:
                new_class = pair[0].split('/')[-2]
                new_id = self.get_key_form_id2cls_name(new_class)
                basename = os.path.basename(pair[1])
                idx = images_info[basename]
                RealTimeAlgorithm.change_error_xml(new_id, new_class, idx, xml_path)

        RealTimeAlgorithm.delete_image_by_time(process_path, real_time)
        # 改变xml文件
        self.new_items_load(xml_path)

        os.remove(image_path)
        os.remove(xml_path)
        pass

    def get_key_form_id2cls_name(self, value):
        # 根据类别名倒回id
        id2cls_name = self.config.info_dict.get_id2cls_name()
        return list(id2cls_name.keys())[list(id2cls_name.values()).index(value)]

    def new_items_load(self, xml_path):
        scene = self.ui.scene
        id2cls_name = self.config.info_dict.get_id2cls_name()
        color_set = self.config.info_dict.clsName2color
        scene_width = scene.width()
        scene_height = scene.height()

        scene.clear()
        result_items = []
        result_items_list = []
        xml = MXml(xml_path)
        for ii, box in enumerate(xml.boxes):
            x, y, width, height, categories_id, name = box
            x, width = map(lambda i: int(i * scene_width), [x, width])
            y, height = map(lambda i: int(i * scene_height), [y, height])
            if not categories_id in id2cls_name.keys():
                pop_prompt(self, "缺少类别:{}，已删除该类别的标注".format(name))
                continue
            cls_name = id2cls_name[categories_id]
            pen = QPen(QColor(color_set[cls_name][0], color_set[cls_name][1], color_set[cls_name][2]))
            return_item = ItemBase.make_item((x, y), (width, height), pen, cls_name, None)
            return_item_list = [(x, y), (width, height), cls_name]
            result_items.append(return_item)
            result_items_list.append(return_item_list)
        scene.add_item(result_items)
        pass

    def splicing_finish(self, image_path):
        self.ui.whole_img_scene.whole_set_img(image_path)
        pass

    def open_image_slot(self):
        # 点击打开单张图片action的槽函数
        if self.check_path():
            return
        img_name = pop_file_dialog(self, 'file', '请选择图片的位置', filter="Image Files(*.jpg *.png *.bmp);;所有文件(*.*)")
        if img_name is None:
            return
        file_path = os_path_dirname(os.path.abspath(img_name))
        all_img = get_image_files(file_path, recurse=False)
        self.config.file_path = file_path
        self.config.all_file = all_img
        self.config.index = all_img.index(img_name)
        self.update_scene_image()
        pass

    def open_dir_slot(self):
        if self.check_path():
            return
        file_path = pop_file_dialog(self, 'dir', '选择图像保存文件夹')
        if file_path is None:
            return
        else:
            if self.config.file_tree_root == file_path:
                pop_warning_dialog(self, '图片保存路径不能与根目录一致')
                return
            elif not self.config.file_tree_root in file_path:
                pop_warning_dialog(self, '图片保存路径必须在根目录下，请重新选择')
            else:
                all_img = get_image_files(file_path, recurse=False)
                if len(all_img) == 0:  # 确定有图片
                    pop_prompt(self, '该文件夹无图片,请重新选择')
                    return
                self.config.file_path = file_path
                self.config.all_file = all_img
                self.config.index = 0
                self.update_scene_image()
        pass

    #########################################graphicsView的相关操作#####################################################

    def graphics_setting(self):
        # 主界面的scene
        self.ui.graphicsView.setScene(self.ui.scene)
        self.ui.graphicsView.setSceneRect(0, 0, self.ui.scene.width(), self.ui.scene.height())
        self.ui.graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        # 设置隐藏滚动条
        self.ui.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 最近保存图片的scene
        self.ui.graphicsView_current.setScene(self.ui.last_img_scene)
        self.ui.graphicsView_current.setSceneRect(0, 0, self.ui.last_img_scene.width(), self.ui.last_img_scene.height())
        self.ui.graphicsView_current.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.ui.graphicsView_current.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.graphicsView_current.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 全图的scene
        self.ui.graphicsView_whole.setScene(self.ui.whole_img_scene)
        self.ui.graphicsView_whole.setSceneRect(0, 0, self.ui.whole_img_scene.width(), self.ui.whole_img_scene.height())
        self.ui.graphicsView_whole.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.ui.graphicsView_whole.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.graphicsView_whole.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheel_slot(self, event: QGraphicsSceneWheelEvent):
        # 滑轮的槽函数
        current_row = self.ui.nameList.currentRow()
        current_row = 0 if current_row is None else current_row
        if event.delta() < 0:
            if current_row + 1 != self.ui.nameList.count():
                self.ui.nameList.set_current_item(current_row + 1)
        else:
            if current_row != 0:
                self.ui.nameList.set_current_item(current_row - 1)
        scene = self.ui.scene
        items = scene.selectedItems()
        if len(items) == 0:
            cursor_item = scene.itemAt(event.scenePos(), QTransform())
            if cursor_item is None:
                return
            cursor_item.setSelected(True)  # 直接设置为选中
            items = [cursor_item]
        current_item = self.ui.nameList.currentItem()
        if current_item:
            text = current_item.text()
        else:
            return
        for item in items:
            if isinstance(item, ItemBase):
                color_set = self.config.info_dict.clsName2color
                pen = QPen(QColor(color_set[text][0], color_set[text][1], color_set[text][2]))
                self.ui.scene.change_item_attributes(items, text=text, pen=pen)
        pass

    def create_item_slot(self, event: QGraphicsSceneMouseEvent):
        ui = self.ui
        x, y = event.scenePos().x(), event.scenePos().y()
        if ui.nameList.count() != 0:
            if ui.nameList.currentItem():
                current_item = ui.nameList.currentItem()
            else:
                current_item = ui.nameList.item(0)
            cls_name = current_item.text()
            categories_id = self.config.info_dict.clsName2id[cls_name]
            item = ItemBase.make_item((x, y), (0, 0), current_item.color, cls_name)
            self.ui.scene.add_item(item)
            self.ui.scene.set_focus(item)
        else:
            pop_prompt(self, '请先创建类别')
        pass

    def change_item_slot(self, event: QGraphicsSceneMouseEvent):
        scene = self.ui.scene
        if scene.hasFocus():
            x, y = event.scenePos().x(), event.scenePos().y()
            item = scene.focusItem()
            self.ui.scene.change_item_attributes(item, size=(x - item.scenePos().x(), y - item.scenePos().y()))
        pass

    def end_item_slot(self):
        scene = self.ui.scene
        if scene.hasFocus():
            item = scene.focusItem()
            if item.size[0] <= 10 or item.size[1] <= 10:
                scene.removeItem(item)
                scene.clearFocus()
                scene.update()
        pass

    ############################################按键与BOX操作############################################################

    def stop_save_botton(self):
        # 保存更改按钮
        if self.mode_changeable_flag:
            pop_prompt(self, '请先开始记录')
            return
        img_path, self.config.new_time = self.save_current_image()
        if img_path is None:
            return
        process_path = self.config.process_save_path
        last_files = get_dir_all_file(process_path)
        for file in last_files:
            os.remove(file)
        xml_path = self.get_save_xml_path(img_path)
        image_root_name = img_path_to_cut_img_name_root(img_path, self.config.file_tree_root)
        imgAlgorithm.cut_one_image(img_path, xml_path, image_root_name, process_path, real_time_cutting=False)

        now_files = get_dir_all_file(process_path)
        self.config.cell_sum += len(now_files)
        self.update_interface(img_path)
        pass

    def update_interface(self, img_path):
        # 文件树更新
        self.file_tree_refresh()
        # 带动最近保存更新
        self.config.last_img_save_path = img_path
        self.last_img_show(self.config.last_img_save_path)
        # 带动细胞总数更新
        self.ui.label_cell_sum.setText(''.join(['已标注细胞数量：', str(self.config.cell_sum)]))
        # 带动全图拼接更新
        if self.config.whole_map_check == 1:
            self.image_splicing.insert_image(img_path)
            self.image_splicing.start()
        pass

    def save_current_image(self):
        # 保存当前显示的图
        image = self.current_image
        if image is None:
            pop_prompt(self, '未检测到图片输入，请稍等')
            return None, None

        record_save_path = self.config.record_save_path
        scene = self.ui.scene
        items = scene.items()
        tmp = countFile(record_save_path)
        if tmp == 0:
            tmp = '00000'
        else:
            file_max_num = 0
            for root, dirs, files in os.walk(record_save_path):
                for file in files:
                    file_num = int(file.split('.')[0].split('-')[-1])
                    if file_num > file_max_num:
                        file_max_num = file_num
                    pass
            tmp = str(file_max_num+1)
            if len(tmp) == 1:
                tmp = "0000" + tmp
            elif len(tmp) == 2:
                tmp = "000" + tmp
            elif len(tmp) == 3:
                tmp = "00" + tmp
            elif len(tmp) == 4:
                tmp = "0" + tmp

        base_name = record_save_path.split('/')[-1]
        if base_name == 'images':
            Name = self.config.inf
            list = '-'.join([Name, tmp])
            pass
        else:
            list = ''.join([base_name, tmp])

        img_path = os_path_join(record_save_path, ''.join([list, ".jpg"]))
        cv2.imencode('.jpg', image)[1].tofile(img_path)

        for item in items:
            # TODO 这里统一设置id
            item.categories_id = self.config.info_dict.clsName2id[item.text]
        path = self.get_save_xml_path(img_path)
        MXml.get_xml(img_path, items, scene, path)
        scene.clear()

        return img_path, list
        pass

    def record_botton(self):
        # 开始记录按钮，根据mode_changeable_flag来判断处于未开始记录还是正在记录中
        if self.mode_changeable_flag:
            if self.config.observe_check == 1:
                pop_prompt(self, '观察者模式下不能开始记录')
                return
            if not self.check_path():
                return
            if self.config.camera_inf is None:
                pop_prompt(self, '请先设置相机参数')
                return
            self.image_thread = CameraThread()
            self.image_thread.camera_inf = self.config.camera_inf
            self.image_thread.imageSignal.connect(self.image_callback)
            self.image_thread.cameralabelSignal.connect(self.set_camera_label)
            if self.image_thread.check_out():
                if pop_question(self, '是否开始记录？若选择开始则不能切换模式直至本轮标注结束,而且中途退出可能导致数据丢失'):
                    self.camera_flag = False
                    self.start_record()
            pass
        else:
            _txet = ['是否结束本轮标注？', '进程仍在继续，是否结束本轮标注？']
            text = _txet[0] if self.image_thread.isFinished() else _txet[1]
            if pop_question(self, text):
                self.camera_flag = True
                self.end_record()
            pass

    def start_record(self):
        # 开始记录按钮，此时必须保证根目录、病人文件夹、摄像机接口等等一切正常才能用
        whole_path = self.config.record_save_path.replace('/images', '')
        self.image_splicing.whole_dir_path = whole_path
        self.image_splicing.is_First = True

        self.ui.scene.clear()
        self.image_thread.start()
        self.set_mode_changeable_flag(False)
        self.file_tree_refresh()
        self.ui.pushButton_start_end.setText('结束本轮标记')
        pass

    def end_record(self):
        # 结束本轮标记
        self.image_thread.camera_flag = False
        self.image_thread.exit_thread()
        self.current_image = None

        files = get_dir_all_file(self.config.process_save_path)
        for file in files:
            os.remove(file)

        self.set_mode_changeable_flag(True)
        self.ui.pushButton_start_end.setText('开始记录')

        if pop_question(self, '是否自动对本轮图片进行切割并查重？'):
            image_paths = get_all_file_path(self.config.record_save_path)
            categories_path = self.config.record_save_path.replace('images', 'categories')
            if not os.path.exists(categories_path):
                os.mkdir(categories_path)
            self.cut_images(image_paths, categories_path)
            # 查重
            self.recheck(categories_path, mode='普通查重')

        self.config.cell_sum = 0
        self.ui.label_cell_sum.setText(''.join(['已标注细胞数量：', str(self.config.cell_sum)]))
        pass

    def check_time(self):
        now_time = time.time()
        if self.config.now_time > now_time:
            self.reply_to_factory_settings()
            pop_warning_dialog(self, '非法更改时间！请重新激活软件！')
            self.config.legal_flag = False
        else:
            self.config.now_time = int(now_time)
        pass


    def auto_detect_slot(self):
        # 自动检测模块
        self.check_time()
        if self.intelligent_algorithm is None:
            logger.warning("intelligent algorithm can't use")
            return
        scene = self.ui.scene
        scene.clear()
        image = self.current_image
        if image is None:
            image_path = scene.img_path
            if not image_path:
                logger.warning("empty image")
                return
            image = cv_imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        ori_width, ori_height = image.shape[:2][::-1]
        x_proportion = scene.width() / ori_width
        y_proportion = scene.height() / ori_height
        detect_result = self.intelligent_algorithm.detect(image)

        items = []
        id2cls_name = {k: v for v, k in self.config.info_dict.clsName2id.items()}
        for center_x, center_y, width, height, conf, class_id in detect_result:
            x, y, width, height = (center_x - width // 2) * x_proportion, (
                    center_y - height // 2) * y_proportion, width * x_proportion, height * y_proportion
            cls_name = self.config.info_dict.get_clsName_by_id(class_id)
            color = self.config.info_dict.get_color_by_clsName(cls_name)
            items.append(ItemBase.make_item((x, y), (width, height), QPen(QColor(*color)), id2cls_name[class_id]))
        self.ui.scene.add_item(items)

        if self.config.real_time_recheck == 1:
            self.real_time_rechecking()
        pass

    def real_time_rechecking(self):
        # 实时查重，只在自动检测完成之后调用
        mode = self.ui.comboBox.currentText()
        if mode == '记录模式' and self.mode_changeable_flag == False:
            img_path, self.config.real_time = self.save_current_image()
            if img_path is None:
                return
            self.config.real_time_image_path = img_path
            process_path = self.config.process_save_path

            if not os.path.exists(process_path):
                os.mkdir(process_path)
            if img_path is not None:
                xml_path = self.get_save_xml_path(img_path)
                image_root_name = img_path_to_cut_img_name_root(img_path, self.config.file_tree_root)
                self.config.images_info = imgAlgorithm.cut_one_image(img_path, xml_path, image_root_name, process_path,
                                                                     real_time_cutting=True)
                self.recheck(process_path, mode='自动识别查重')
        pass

    def cut_images(self, image_paths, save_path):
        # 切割图片
        xml_paths = [self.get_save_xml_path(i) for i in image_paths]
        category_path_is_exists = os.path.exists(save_path)
        if not category_path_is_exists:
            pop_prompt(self, '该病人没有类别文件夹，请创建类别文件')
            return
        if not os.path.isdir(save_path):
            pop_warning_dialog(self, "保存路径未选择，切割失败")
            return
        
        for root, dirs, files in os.walk(save_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))


        img_xml_dict = {}
        error_image_paths = []
        for image_path, xml_path in zip(image_paths, xml_paths):
            if os.path.exists(image_path) and os.path.exists(xml_path):
                img_xml_dict[image_path] = xml_path
            else:
                error_image_paths.append(image_path)

        # 开始逐一切割图片
        for ii, (image_path, xml_path) in enumerate(img_xml_dict.items()):
            QApplication.processEvents()
            image_root_name = img_path_to_cut_img_name_root(image_path, self.config.file_tree_root)
            imgAlgorithm.cut_one_image(image_path, xml_path, image_root_name, save_path, real_time_cutting=False)
        pass

    def turn_page_slot(self, direction):
        # 翻页的槽函数
        all_file = self.config.all_file
        if all_file is None:
            pop_prompt(self, '无图片可读')
            return
        if self.config.index + direction == len(all_file) or self.config.index + direction == -1:
            if direction == 1:
                pop_prompt(self, "这是最后一张图片")
            elif direction == -1:
                pop_prompt(self, "这是第一张图片")
            # direction = 0  # 重新加载为了自动用scene的改变图片信号处理
            return
        # 更新图片
        self.config.index = self.config.index + direction
        file_path = self.config.all_file[self.config.index]
        self.set_scene_image(file_path)
        pass

    def mode_change_slot(self, text):
        # 模式的comboBox切换的槽函数,兼容刷新按钮的特殊响应
        if text == "Fresh":
            mode = self.config.mode
            if mode == '记录模式':
                self.file_tree_refresh()
            elif mode == '综合模式':
                self.file_tree_init(self.config.file_tree_root)
            return

        self.set_mode(text)
        pass

    def set_mode(self, mode):
        # 切换模式
        self.config.mode = mode
        if mode == '记录模式':
            self.ui.pushButton_stop.setEnabled(True)
            self.ui.pushButton_start_end.setEnabled(True)
            self.ui.open_img_action.setEnabled(False)
            self.ui.open_dir_action.setEnabled(False)
            self.file_tree_refresh()
            pass
        elif mode == '综合模式':
            self.ui.pushButton_stop.setEnabled(False)
            self.ui.pushButton_start_end.setEnabled(False)
            self.ui.open_img_action.setEnabled(True)
            self.ui.open_dir_action.setEnabled(True)
            # 自带更新文件树，是除了初始化和新增病人文件夹外，唯一能更新文件树的地方
            self.file_tree_init(self.config.file_tree_root)
            pass
        else:
            logger.error("模式名字错误")
        pass

    def set_mode_changeable_flag(self, flag: bool):
        # 根据是否开始记录来选择一些工具栏和按钮的是否可用情况
        self.mode_changeable_flag = flag
        if not flag:
            # 不可变
            self.ui.menubar.setEnabled(False)
            self.ui.fileTreeWidget.show_action.setEnabled(False)
            self.ui.fileTreeWidget.star_action.setEnabled(False)
            self.ui.findTreeWidget.setEnabled(False)
            self.ui.starTreeWidget.setEnabled(False)
            self.ui.pre_button.setEnabled(False)
            self.ui.next_button.setEnabled(False)
            self.ui.comboBox.setEnabled(False)
        else:
            self.ui.menubar.setEnabled(True)
            self.ui.fileTreeWidget.show_action.setEnabled(True)
            self.ui.fileTreeWidget.star_action.setEnabled(True)
            self.ui.findTreeWidget.setEnabled(True)
            self.ui.starTreeWidget.setEnabled(True)
            self.ui.pre_button.setEnabled(True)
            self.ui.next_button.setEnabled(True)
            self.ui.comboBox.setEnabled(True)
        pass

    ################################################功能性函数#########################################################

    def last_img_show(self, last_path):
        if last_path is None:
            pass
        else:
            self.ui.last_img_scene.lp_set_img(last_path)
            self.ui.last_label.setText("最近一次保存图片：" + os.path.basename(last_path))
            self.ui.last_label.setToolTip(last_path)
            # 加载新图片
            mod = 'last'
            self.new_img_load(mod)
        pass

    def get_save_xml_path(self, img_path):
        # 根据当前配置情况获得当前图片保存的路径
        root = self.config.file_tree_root
        rel_image_path = os_path_relpath(img_path, root)
        rel_xml_path = rel_image_path.replace('images', 'xmls', 1).rsplit('.', maxsplit=1)[-2] + '.xml'
        save_xml_path = os_path_join(root, rel_xml_path)
        # else:
        #     logger.error("模式名字错误")
        return save_xml_path

    def new_img_load(self, mod: str):
        if mod == 'new':
            scene = self.ui.scene
        elif mod == 'last':
            scene = self.ui.last_img_scene

        img_path = scene.img_path
        id2cls_name = self.config.info_dict.get_id2cls_name()
        color_set = self.config.info_dict.clsName2color
        scene_width = scene.width()
        scene_height = scene.height()
        xml_file = self.get_save_xml_path(img_path)

        scene.clear()
        if os.path.exists(xml_file):
            result_items = []
            result_items_list = []
            xml = MXml(xml_file)
            for ii, box in enumerate(xml.boxes):
                x, y, width, height, categories_id, name = box
                x, width = map(lambda i: int(i * scene_width), [x, width])
                y, height = map(lambda i: int(i * scene_height), [y, height])
                if not categories_id in id2cls_name.keys():
                    pop_prompt(self, "缺少类别:{}，已删除该类别的标注".format(name))
                    continue
                cls_name = id2cls_name[categories_id]
                pen = QPen(QColor(color_set[cls_name][0], color_set[cls_name][1], color_set[cls_name][2]))
                return_item = ItemBase.make_item((x, y), (width, height), pen, cls_name, None)
                return_item_list = [(x, y), (width, height), cls_name]
                result_items.append(return_item)
                result_items_list.append(return_item_list)
            scene.add_item(result_items)
            scene.xml_path = xml_file
            if mod == 'new':
                self.config.new_load_items = result_items_list

            # 设置显示
            # self.ui.xml_path_label.setText(os.path.basename(xml_file))
            # self.ui.xml_path_label.setToolTip(xml_file)
        pass

    def items_had_changed(self, new_items):
        result_items = self.config.new_load_items
        if result_items is not None:
            if len(new_items) != len(result_items):
                return True
            for item1 in new_items:
                tag = 0
                for item2 in result_items:
                    if (item1.x(), item1.y()) == item2[0] and tuple(item1.size) == item2[1] and item1.text == item2[2]:
                        tag += 1
                if tag != 1:
                    return True
        return False

    def show_one_image(self, image_path):
        # 传入图片的路径，scene显示出来，图片路径必须是对的
        img_parent_dir = os_path_dirname(image_path)
        all_img = get_image_files(img_parent_dir, recurse=False)
        self.config.file_path = img_parent_dir
        self.config.all_file = all_img
        self.config.index = all_img.index(image_path)
        if self.config.index is not None:
            self.update_scene_image()
        pass

    def update_scene_image(self):
        # 根据当前的all_img和index更新scene显示的图片，同时也会重新尝试加载标注
        self.config.index = self.config.index
        if self.config.all_file == []:
            pass
        else:
            file_path = self.config.all_file[self.config.index]
            self.set_scene_image(file_path)
        pass

    def set_scene_image(self, file_path: str):
        # 设置当前scene的图片，mainWindow内改变scene的图片必须使用这个函数
        self.old_img_pass()  # 处理旧图片
        self.ui.scene.set_img_from_path(file_path)
        self.ui.image_path_label.setText("当前位置：" + get_short_path(file_path, self.config.file_tree_root))
        self.ui.image_path_label.setToolTip(file_path)
        # 加载新图片
        mod = 'new'
        self.new_img_load(mod)
        pass

    def old_img_pass(self):
        if not self.config.observe_check:
            if not self.ui.scene.if_have_img():
                logger.warning("当前图片为空")
                return False
            logger.info("处理当前图片")
            if not self.ui.scene.if_have_img():
                return
            scene = self.ui.scene
            items = scene.items()
            for item in items:
                # TODO 这里统一设置id
                item.categories_id = self.config.info_dict.clsName2id[item.text]
            img_path = scene.img_path
            if not "categories" in img_path:
                path = self.get_save_xml_path(img_path)
                save_flag = True
                if self.items_had_changed(items):
                    answer = pop_question(self, 'xml文件已存在,是否要覆盖')
                    save_flag = answer
                if save_flag:
                    MXml.get_xml(img_path, items, scene, path)
                    # if self.config.cut_img_flag:
                    #     imgAlgorithm.cut_picture(img_path, os_path_dirname(path), (scene.width(), scene.height()),
                    #                              scene.items())
        return True

    def image_callback(self, image, w, h):
        self.current_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.ui.scene.set_img(image, w, h)
        pass

    def set_camera_label(self, index, info):
        Info = ''.join(['当前摄像机索引：', str(index), '->', info])
        self.ui.camera_label.setText(Info)
        pass

    def check_path(self):
        mode = self.ui.comboBox.currentText()
        root_path = self.config.file_tree_root
        record_save_path = self.config.record_save_path
        if mode == '记录模式':
            if root_path is None or not os.path.exists(root_path):
                pop_warning_dialog(self, '根目录不存在')
                return False
            if record_save_path is None or not os.path.exists(record_save_path):
                pop_warning_dialog(self, '保存路径不存在')
                return False
            return True
        elif mode == '综合模式':
            if root_path is None or not os.path.exists(root_path):
                pop_warning_dialog(self, '根目录不存在')
                return True
                pass
        pass

    def recovery_statusbar(self):
        record_save_path = self.config.record_save_path
        if record_save_path is None:
            pass
        else:
            text = "".join(['当前保存路径：', record_save_path.split('/')[-2]])
            self.ui.label_current_save.setText(text)

    def recovery(self):
        # 每次初始化软件时调用的初始化函数
        self.config.load_setting()

        # 板块恢复函数
        self.recovery_list_widget()
        self.recovery_statusbar()

        # 恢复模式（包含了树文件更新）有坑
        if self.config.mode == '综合模式' or self.config.mode is None:
            self.ui.comboBox.currentTextChanged.emit(self.ui.comboBox.currentText())
        else:
            self.ui.comboBox.setCurrentText(self.config.mode)

        # 如果index有值就使scene显示图片
        if self.config.index is not None and self.config.all_file is not None:
            self.update_scene_image()
        pass

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.acceptProposedAction()
        pass

    def dropEvent(self, event: QDropEvent) -> None:
        if self.config.file_tree_root is None:
            pop_warning_dialog(self, "文件树根目录必须正确设置")
            return
        file_paths = event.mimeData().urls()
        file_path = file_paths[0].path()
        file_name = os.path.basename(file_path)
        if len(file_name.rsplit('_', 1)[0]) == 1:
            pop_warning_dialog(self, '打开失败，请拖入切割后的图片')
            return
        # TODO 暂时只能打开.jpg和.bmp的图片
        full_image_path_jpg = cut_img_path_to_img_path(file_name, self.config.file_tree_root, suffix='.jpg')
        full_image_path_bmp = cut_img_path_to_img_path(file_name, self.config.file_tree_root, suffix='.bmp')
        if os.path.exists(full_image_path_jpg):
            self.show_one_image(full_image_path_jpg)
        elif os.path.exists(full_image_path_bmp):
            self.show_one_image(full_image_path_bmp)
        else:
            pop_prompt(self, "拖入图片未能找到原图")
        pass

    def closeEvent(self, event) -> None:
        "退出事件"
        now_time = str(int(time.time()))
        if self.config.register_code is not None:
            try:
                inf = get_code.des_decrypt('scnuscnu', b''.join([bytes([int(i)]) for i in self.config.register_code]))
                inf = str(inf)[2:-1].split('_')
            except:
                pop_warning_dialog(self, '密匙被非法更改！请重置软件！')
                self.config.legal_flag = False
            else :
                if self.config.legal_flag:
                    [password, register_time, limit_time, last_time] = inf
                    new_inf = '_'.join([password, register_time, limit_time, now_time])
                    secret_bytes = get_code.des_encrypt('scnuscnu', new_inf)
                    secret_list = []
                    for each in secret_bytes:
                        secret_list.append(int(each))
                    self.config.register_code = secret_list

        if self.mode_changeable_flag:
            self.old_img_pass()
            # self.config.settings.setValue('window_state', self.saveState())
            pass
        else:
            if pop_question(self, '当前仍处于记录中，是否强制退出？'):
                pass
            else:
                event.ignore()
        pass
