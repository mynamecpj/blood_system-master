import os
import csv
import mimetypes
from pathlib import Path
import numpy as np
import yaml
import datetime


def path_preprocess(path):
    """
    对输入的path进行预处理，如将\\变成/
    Args:
        path (str):

    Returns:

    """
    return path.replace('\\', '/')


def cut_img_path_to_img_path(cut_img_path, file_tree_root, suffix='.bmp'):
    img_name_root = cut_img_path.rsplit('_', 2)[0]
    rel_path = '/'.join(img_name_root.split('+'))
    return os_path_join(file_tree_root, rel_path) + suffix


def img_path_to_cut_img_name_root(img_path, file_tree_root):
    """
    根据文件树根目录和图片路径得到切割图片保存路径的文件名根部分
    Args:
        img_path (str):
        file_tree_root (str):

    Returns:

    """
    rel_path = os_path_relpath(img_path, file_tree_root)
    return str(rel_path.rsplit('.', 1)[0]).replace('/', '+')


def ensure_dir_exist(dir):
    """保证路径存在，不存在则创建"""
    if not os.path.exists(dir):
        os.mkdir(dir)
        return False
    return True


def get_all_file_path(dir: str):
    """获得某个路径下所有文件的全名"""
    return [os_path_join(dir, os.listdir(dir)[i])
            for i in range(len(os.listdir(dir)))]


def get_dir_all_file(dir):
    """获得某个路径下所有子文件的完整路径名"""
    result = []
    for roots, dirs, files in os.walk(dir):
        for file in files:
            result.append(os_path_join(roots, file))
    return result


def get_index(path, fromImgName):
    """原来的getIndex"""
    if not os.path.isdir(path):
        os.mkdir(path)
    indexes = []
    for file in os.listdir(path):  # 得出某个文件夹里面来自fromImgName的切割图片
        file_name = file.rsplit('.', maxsplit=1)[0]
        ori_file_name = file_name.rsplit('_', maxsplit=2)[0]
        if ori_file_name == fromImgName:
            indexes.append(int(file_name.rsplit('_', maxsplit=1)[-1]))
    if len(indexes) > 0:
        index = max(indexes) + 1
    else:
        index = 0
    return index


def delete_name_image(allFile, name):
    """删除给的文件列表中文件格式为1-name中等于name的文件"""
    for file in allFile:
        print(os.path.basename(file).rsplit('.', maxsplit=1)[0].rsplit('_', maxsplit=1)[-2])
        if os.path.basename(file).rsplit('.', maxsplit=1)[0].rsplit('_', maxsplit=1)[-2] == name:
            os.remove(file)
    pass


def get_file_name(file):
    """获得文件名"""
    return os.path.basename(file).split('.')[-2]


# csv
def update_cls_csv(path, all_rows):
    """在增加删除类别的时候调用更新整个文件"""
    all_rows = [{'id': k, 'name': v} for k, v in all_rows]
    field_names = ['id', 'name']
    with open(path, 'r', encoding='utf-8') as f:
        # 先保证整个文件的数据还在，一旦写入出现问题，先把原来的数据写回去
        csv_reader = csv.DictReader(f, field_names)
        origin_rows = []
        for r in csv_reader:
            origin_rows.append(r)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            csv_writer = csv.DictWriter(f, field_names)
            csv_writer.writerows(all_rows)
    except:
        with open(path, 'w', encoding='utf-8') as f:
            csv_writer = csv.DictWriter(f, field_names)
            csv_writer.writerows(origin_rows)
        raise BaseException


def load_color_set_from_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        field_names = ['id', 'name']
        csv_reader = csv.DictReader(f, field_names)
        all_row = []
        for row in csv_reader:
            if row['name'] is None:
                continue
            row['id'] = int(row['id'])
            all_row.append(row)
        return all_row


def ifnone(a, b):
    "`a` if `a` is not None, otherwise `b`."
    return b if a is None else a


def poxis2str(l):
    return [str(i) for i in l]


def _path_to_same_str(p_fn):
    "path -> str, but same on nt+posix, for alpha-sort only"
    s_fn = str(p_fn)
    s_fn = s_fn.replace('\\', '.')
    s_fn = s_fn.replace('/', '.')
    return s_fn


def _get_files(parent, p, f, extensions):
    p = Path(p)  # .relative_to(parent)
    if isinstance(extensions, str): extensions = [extensions]
    low_extensions = [e.lower() for e in extensions] if extensions is not None else None
    res = [p / o for o in f if not o.startswith('.')
           and (extensions is None or f'.{o.split(".")[-1].lower()}' in low_extensions)]
    return res


def get_files(path, extensions=None, recurse: bool = False, exclude=None,
              include=None, presort: bool = False, followlinks: bool = False):
    "Return list of files in `path` that have a suffix in `extensions`; optionally `recurse`."
    if recurse:
        res = []
        for i, (p, d, f) in enumerate(os.walk(path, followlinks=followlinks)):
            # skip hidden dirs
            if include is not None and i == 0:
                d[:] = [o for o in d if o in include]
            elif exclude is not None and i == 0:
                d[:] = [o for o in d if o not in exclude]
            else:
                d[:] = [o for o in d if not o.startswith('.')]
            res += _get_files(path, p, f, extensions)
        if presort: res = sorted(res, key=lambda p: _path_to_same_str(p), reverse=False)
        return poxis2str(res)
    else:
        f = [o.name for o in os.scandir(path) if o.is_file()]
        res = _get_files(path, path, f, extensions)
        if presort: res = sorted(res, key=lambda p: _path_to_same_str(p), reverse=False)
        return [path_preprocess(i) for i in poxis2str(res)]


def get_image_files(path, extensions=None, recurse: bool = False, exclude=None, include=None, presort: bool = False,
                    followlinks: bool = False):
    image_extensions = set(k for k, v in mimetypes.types_map.items() if v.startswith('image/'))
    extensions = ifnone(extensions, image_extensions)
    return get_files(path, extensions, recurse, exclude, include, presort, followlinks)


def get_image_extensions():
    list_ = list(set(k for k, v in mimetypes.types_map.items() if v.startswith('image/')))
    list_.append('.JPEG')
    return list_


def find_same_name_file(all_file):
    "查找所有同名文件"
    path_result = {}
    for file in all_file:
        newPath = os.path.basename(file)
        if path_result.get(newPath) is not None:
            path_result[newPath] += [file]
        else:
            path_result[newPath] = [file]
    diff_path_result = {}
    for key, value in path_result.items():
        if len(value) > 1:
            diff_path_result[key] = value
    return path_result, diff_path_result


def find_intersection_mask(list_a, list_b):
    "传入两个列表，分别返回两个列表的交集mask，若为相交则为True，否则为False"
    intersection = list(set(list_a).intersection(set(list_b)))
    error_a = list(set(list_a).difference(set(intersection)))
    error_b = list(set(list_b).difference(set(intersection)))

    a_mask = np.ones(len(list_a), dtype=np.bool)
    b_mask = np.ones(len(list_b), dtype=np.bool)

    for i in range(len(list_a)):
        if list_a[i] in error_a:
            a_mask[i] = 0
    for i in range(len(list_b)):
        if list_b[i] in error_b:
            b_mask[i] = 0

    return a_mask, b_mask


def find_same_name_different_suffix_file(paths, find_root, suffix='.xml'):
    result = []
    all_files = get_files(find_root, recurse=True)
    all_names = [os.path.basename(path).split('.')[0] for path in all_files]
    for path in paths:
        all_names = np.array(all_names)
        name = os.path.basename(path).split('.')[0]
        same_index = (all_names == name)
        same_files = np.array(all_files)[same_index]
        suffixs_mask = (np.array([Path(path).suffix for path in same_files]) == suffix)
        same_files = list(same_files[suffixs_mask])
        result.append(same_files)
    return result


def compare_path_similarity(path_1, path_2):
    path_1_paths = []
    path_2_paths = []

    previous_path = None
    while True:
        path_1, tmp = os.path.split(path_1)
        path_1_paths.append(tmp)
        if previous_path == path_1:
            break
        previous_path = path_1
    while True:
        path_2, tmp = os.path.split(path_2)
        path_2_paths.append(tmp)
        if previous_path == path_2:
            break
        previous_path = path_2

    mask, mask = find_intersection_mask(path_1_paths, path_2_paths)
    similarity = sum(mask)
    return similarity


def read_color_yaml(file_path):
    with open(file_path, 'r') as yaml_file:
        yaml_obj = yaml.safe_load(yaml_file.read())
    return yaml_obj


def os_path_join(*args, **kwargs):
    """
    替代os.path.join
    Args:
        *args:
        **kwargs:

    Returns:

    """
    result = os.path.join(*args, **kwargs)
    result = path_preprocess(result)
    return result


def os_path_relpath(*args, **kwargs):
    result = os.path.relpath(*args, **kwargs)
    result = result.replace('\\', '/')
    return result


def os_path_dirname(*args, **kwargs):
    result = os.path.dirname(*args, **kwargs)
    result = result.replace('\\', '/')
    return result


def create_new_patient(root_path, inf):
    root_path_patient = os.path.join(root_path, inf)
    os.makedirs(root_path_patient, exist_ok=True)
    os.makedirs(os.path.join(root_path_patient, 'categories'), exist_ok=True)
    os.makedirs(os.path.join(root_path_patient, 'images'), exist_ok=True)
    os.makedirs(os.path.join(root_path_patient, 'xmls'), exist_ok=True)
    os.makedirs(os.path.join(root_path_patient, 'process'), exist_ok=True)


def CutHour(time=datetime.datetime.now()):
    """截取时分秒"""
    new_time = str(time)
    hour = new_time[11:19]
    return "".join(hour)


def get_time(time=datetime.datetime.now()):
    hour = CutHour(time)
    day2 = str(datetime.date.today())
    return "".join([day2, '  ', hour])
