import sys
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import *
from utils.popDialogUtils import *
from utils.utils import *


class ConfigPropertyException(BaseException):
    pass


class InfoDict(object):
    """包括class_name, id, color信息的数据结构，
    要求的是稳定性以及索引颜色的时候的速度"""

    def __init__(self):
        # 以下三个的信息要实时保持同步，其中一个正确那么其他两个一定正确
        self.all_info = []  # all_info的顺序应该等同于class.csv里面的顺序，所以插入的时候要注意
        self.clsName2color = {}
        self.clsName2id = {}
        pass

    def get_id2cls_name(self):
        return {k: v for v, k in self.clsName2id.items()}

    def insert(self, row, id, cls_name, color):
        """添加新的类别"""
        assert isinstance(id, int), '传入字典的id不是int'
        assert isinstance(cls_name, str), '传入字典的cls_name不是str'
        assert isinstance(color, tuple) or isinstance(color, list), '传入字典的color不是元组或列表类型'

        if id in list(self.clsName2id.values()):
            raise BaseException('该类别id已存在，出现问题')
        # 不检查是否出现相同cls_name
        self.all_info.insert(row, [id, cls_name, color])
        self.clsName2color[cls_name] = color
        self.clsName2id[cls_name] = id
        pass

    def get_cls_csv_rows(self):
        all_rows = [info[:2] for info in self.all_info]
        return all_rows

    def append(self, id, cls_name, color):
        """添加新的类别"""
        self.insert(len(self.all_info) + 1, id, cls_name, color)
        pass

    def delete_info_by_clsName(self, clsName):
        """用类别名字删除一个类别"""
        index = None
        for i, info in enumerate(self.all_info):
            if clsName in info:
                index = i
                break
        if index is None:
            raise BaseException('删除一个找不到的类别')
        info = self.all_info.pop(index)
        self.clsName2color.pop(info[1])
        self.clsName2id.pop(info[1])
        pass

    def rename_info_by_clsName(self, origin_name, new_name):
        """重命名一个类别"""
        index = None
        for i, info in enumerate(self.all_info):
            if origin_name in info:
                index = i
                break
        if index is None:
            raise BaseException('重命名一个找不到的类别')
        self.all_info[index][1] = new_name
        info = self.all_info[index]
        self.clsName2color[new_name] = self.clsName2color.pop(origin_name)
        self.clsName2id[new_name] = self.clsName2id.pop(origin_name)

    def get_color_by_clsName(self, clsName):
        """从clsName得到color"""
        if not clsName in self.clsName2color.keys():
            raise BaseException('要获取颜色的类别不存在')
        return self.clsName2color[clsName]

    def get_clsName_by_id(self, id):
        """从id得到clsName"""
        if not id in self.clsName2id.values():
            raise BaseException('要获取类别名字的id不存在')
        id2clsName = dict(zip(self.clsName2id.values(), self.clsName2id.keys()))
        return id2clsName[id]


class Config(object):
    initFlag = 1

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self, file='setting.ini'):
        if Config.initFlag:
            self.settings = QSettings(file, QSettings.IniFormat)
            self.img_format = get_image_extensions()  # 所有图片格式，不知道需不需要独立出来
            self.info_dict = InfoDict()
            self.parent = None

            self._all_file = []
            self._file_path = None
            self._record_save_path = None
            self._last_img_save_path = None
            self._index = None
            self._observe_check = None
            self._whole_map_check = None
            self._real_time_recheck = None
            self._new_load_items = None
            self._file_tree_root = None
            self._file_tree_import_xml = None
            self._inf = None
            self._mode = None
            self.new_time = None
            self.real_time = None
            self.images_info = None
            self.real_time_image_path = None
            self._process_save_path = None
            self.cell_sum = 0
            self._camera_inf = None
            self._register_code = None
            self.now_time = None
            self.legal_flag = True

            Config.initFlag = 0
        pass


    def load_code(self):
        register_code = self.settings.value('register_code', defaultValue=None)
        try:
            self.register_code = register_code
        except ConfigPropertyException:
            self.register_code = None

    def load_setting(self):
        # TODO 将config类改成注册的形式，注册类别即可直接新增需要保存的配置
        # observe_check = self.settings.value('observe_check', defaultValue=0)
        # observe_check = protect_int(observe_check)
        # try:
        #     self.observe_check = observe_check  # 尝试设置成配置文件中的值
        # except ConfigPropertyException:
        #     self.observe_check = 0  # 若不成功就使用默认值
        #
        # whole_map_check = self.settings.value('whole_map_check', defaultValue=0)
        # whole_map_check = protect_int(whole_map_check)
        # try:
        #     self.whole_map_check = whole_map_check  # 尝试设置成配置文件中的值
        # except ConfigPropertyException:
        #     self.whole_map_check = 0  # 若不成功就使用默认值
        #
        #     #real_time_recheck
        # real_time_recheck = self.settings.value('real_time_recheck', defaultValue=0)
        # real_time_recheck = protect_int(real_time_recheck)
        # try:
        #     self.real_time_recheck = real_time_recheck  # 尝试设置成配置文件中的值
        # except ConfigPropertyException:
        #     self.real_time_recheck = 0  # 若不成功就使用默认值

        mode = self.settings.value('mode', defaultValue=None)
        try:
            self.mode = mode  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.mode = None  # 若不成功就使用默认值

        file_tree_root = self.settings.value('file_tree_root', defaultValue=None)
        try:
            self.file_tree_root = file_tree_root  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.file_tree_root = None  # 若不成功就使用默认值

        save_path = self.settings.value('save_path', defaultValue=None)
        try:
            self.save_path = save_path  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            pop_warning_dialog(self.parent, '原保存文件夹路径错误，请重新选择')
            self.save_path = None  # 若不成功就使用默认值

        file_tree_import_xml = self.settings.value('file_tree_import_xml', defaultValue=None)
        try:
            self.file_tree_import_xml = file_tree_import_xml  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.file_tree_import_xml = None  # 若不成功就使用默认值

        file_path = self.settings.value('file_path', defaultValue=None)
        try:
            self.file_path = file_path  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            pop_warning_dialog(self.parent, '原图片文件夹路径错误，请重新选择')
            self.file_path = None  # 若不成功就使用默认值

        video_path = self.settings.value('video_path', defaultValue=None)
        try:
            self.video_path = video_path  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.video_path = None  # 若不成功就使用默认值

        record_save_path = self.settings.value('record_save_path', defaultValue=None)
        try:
            self.record_save_path = record_save_path  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.record_save_path = None  # 若不成功就使用默认值

        process_save_path = self.settings.value('process_save_path', defaultValue=None)
        try:
            self.process_save_path = process_save_path  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.process_save_path = None  # 若不成功就使用默认值

        inf = self.settings.value('inf', defaultValue=None)
        try:
            self.inf = inf  # 尝试设置成配置文件中的值
        except ConfigPropertyException:
            self.inf = None  # 若不成功就使用默认值

        last_img = self.settings.value('last_img', defaultValue=None)
        try:
            self.last_img = last_img
        except ConfigPropertyException:
            self.last_img = None

        camera_inf = self.settings.value('camera_inf', defaultValue=None)
        try:
            self.camera_inf = camera_inf
        except ConfigPropertyException:
            self.camera_inf = [42,28,159,1000,100,100]
            # [Hue, Contrast, Saturation, ExpoTime, ExpoAGain, Gamma]

        # 加载原路径所有文件
        if self.file_path is not None:
            all_file = get_image_files(self.file_path, recurse=False)
            try:
                self.all_file = all_file
            except ConfigPropertyException:
                self.all_file = None
        else:
            self.all_file = None

        # 根据last_img重新得到index
        if self.all_file is not None and self.last_img is not None:
            if self.last_img in self.all_file:
                self.index = self.all_file.index(self.last_img)
            else:
                pop_warning_dialog(self.parent, '最后打开的图片找不到，自动打开文件夹的第一张图片')
                self.index = 0

        all_rows = load_color_set_from_csv(os_path_join(os.getcwd(), 'class.csv'))
        # TODO 这个文件在打包软件的时候要打包进去

        # dir_path = os.path.dirname(__file__)
        color_dict = read_color_yaml(os.path.join(os.getcwd(), "color.yaml"))
        for dict in all_rows:
            id = dict['id']
            cls_name = dict['name']
            color = tuple(color_dict[id])

            self.info_dict.append(id, cls_name, color)
        pass

    def add_cls(self, clsName, color: tuple, row):
        # 寻找一个不可能有的id保存下来
        current_all_id = list(self.info_dict.clsName2id.values())
        if len(current_all_id) == 0: current_all_id = [1]  # 应对一开始没有类别的情况
        id = max(current_all_id) + 1
        self.info_dict.insert(row, id, clsName, color)
        all_rows = self.info_dict.get_cls_csv_rows()
        update_cls_csv(os_path_join(os.getcwd(), 'class.csv'), all_rows)

    def delete_cls(self, cls_name):
        """config删除一个类别的外部方法"""
        self.info_dict.delete_info_by_clsName(cls_name)
        all_rows = self.info_dict.get_cls_csv_rows()
        update_cls_csv(os_path_join(os.getcwd(), 'class.csv'), all_rows)
        pass

    def rename_cls(self, origin_name, new_name):
        """config重命名一个类别的外部方法"""
        self.info_dict.rename_info_by_clsName(origin_name, new_name)
        all_rows = self.info_dict.get_cls_csv_rows()
        update_cls_csv(os_path_join(os.getcwd(), 'class.csv'), all_rows)
        pass

    @property
    def last_img_save_path(self):
        return self._last_img_save_path

    @last_img_save_path.setter
    def last_img_save_path(self, value):
        if value is None:
            self._last_img_save_path = value
            return
        if os.path.isdir(value):
            raise ConfigPropertyException(f'设置图像文件的时候出现错误，{value}\n不是一个图像')
        self.settings.setValue('last_img_save_path', value)
        self._last_img_save_path = value

        # observe_check

    @property
    def observe_check(self):
        return self._observe_check

    @observe_check.setter
    def observe_check(self, value):
        if value != 0 and value != 1:
            raise ConfigPropertyException(f'设置观察者模式时出现错误，出现{value}')
        self.settings.setValue('observe_check', int(value))
        self._observe_check = int(value)

        # whole_map_check

    @property
    def register_code(self):
        return self._register_code

    @register_code.setter
    def register_code(self, value):
        self.settings.setValue('register_code', value)
        self._register_code = value

    @property
    def whole_map_check(self):
        return self._whole_map_check

    @whole_map_check.setter
    def whole_map_check(self, value):
        if value != 0 and value != 1:
            raise ConfigPropertyException(f'设置观察者模式时出现错误，出现{value}')
        self.settings.setValue('whole_map_check', int(value))
        self._whole_map_check = int(value)

        #real_time_recheck

    @property
    def camera_inf(self):
        return self._camera_inf

    @camera_inf.setter
    def camera_inf(self, value:list):
        self._camera_inf = value
        self.settings.setValue('camera_inf', value)
        # self.camera_inf = [Hue, Contrast, Saturation, ExpoTime, ExpoAGain, Gamma]
        pass

    @property
    def real_time_recheck(self):
        return self._real_time_recheck

    @real_time_recheck.setter
    def real_time_recheck(self, value):
        if value != 0 and value != 1:
            raise ConfigPropertyException(f'设置观察者模式时出现错误，出现{value}')
        self.settings.setValue('real_time_recheck', int(value))
        self._real_time_recheck = int(value)

        # new_load_items

    @property
    def new_load_items(self):
        return self._new_load_items

    @new_load_items.setter
    def new_load_items(self, value: list):
        self._new_load_items = value
        pass

    @property
    def inf(self):
        return self._inf

    @inf.setter
    def inf(self, value):
        self._inf = value
        self.settings.setValue('inf', value)
        pass

    @property
    def record_save_path(self):
        return self._record_save_path

    @record_save_path.setter
    def record_save_path(self, value):
        if value is None:
            self._record_save_path = value
            return
        if not os.path.isdir(value):
            raise ConfigPropertyException(f'设置图像文件夹的时候出现错误，{value}\n不是一个文件夹')
        self.settings.setValue('record_save_path', value)
        self._record_save_path = value
        pass

    @property
    def process_save_path(self):
        return self._process_save_path

    @process_save_path.setter
    def process_save_path(self, value):
        # if value is None:
        #     self._process_save_path = value
        #     return
        # if not os.path.isdir(value):
        #     raise ConfigPropertyException(f'设置图像文件夹的时候出现错误，{value}\n不是一个文件夹')
        self.settings.setValue('process_save_path', value)
        self._process_save_path = value
        pass

    @property
    def file_tree_root(self):
        return self._file_tree_root

    @file_tree_root.setter
    def file_tree_root(self, value):
        if value is None:
            self._file_tree_root = value
            return
        if not os.path.isdir(value):
            raise ConfigPropertyException(f'设置文件树根目录的时候出现错误，{value}\n不是一个文件夹')
        self.settings.setValue('file_tree_root', value)
        self._file_tree_root = value

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.settings.setValue('mode', self.mode)

    @property
    def all_file(self):
        return self._all_file

    @all_file.setter
    def all_file(self, img_paths: list):
        if img_paths is None:
            self._all_file = img_paths
            return
        error_img_paths = []
        for img_path in img_paths:
            if not os.path.exists(img_path) or Path(img_path).suffix not in self.img_format:
                error_img_paths.append(img_path)
        if len(error_img_paths) != 0:
            paths_text = '\n'.join(error_img_paths)
            pop_warning_dialog(self.parent, f'设置图像文件列表时出现错误文件：\n{paths_text}\n已自动删除这些文件')
            for error_img_path in error_img_paths:
                img_paths.remove(error_img_path)
        self._all_file = img_paths

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        if value is None:
            self._file_path = value
            return
        if not os.path.isdir(value):
            raise ConfigPropertyException(f'设置图像文件夹的时候出现错误，{value}\n不是一个文件夹')
        self.settings.setValue('file_path', value)
        self._file_path = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if value is None:
            self._index = value
            return
        if not isinstance(value, int) and not (value >= 0 and (value < len(self.all_file))):
            raise ConfigPropertyException(f'设置的index错误')
        self._index = value
        # index 改变，记录当前图片路径保存
        if self.all_file == []:
            pass
        else:
            self.settings.setValue('last_img', self.all_file[self._index])

        # file_tree_import_xml

    @property
    def file_tree_import_xml(self):
        return self._file_tree_import_xml

    @file_tree_import_xml.setter
    def file_tree_import_xml(self, value):
        if value is None:
            self._file_tree_import_xml = value
            return
        if not os.path.isfile(value):
            raise ConfigPropertyException(f'设置文件树导入xml的目录的时候出现错误，{value}\n不是一个文件')
        self.settings.setValue('file_tree_import_xml', value)
        self._file_tree_import_xml = value
