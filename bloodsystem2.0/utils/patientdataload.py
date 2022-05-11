import os
import numpy as np
import csv

def os_path_join(*args, **kwargs):
    """
    替代os.path.join

    """
    result = os.path.join(*args, **kwargs)
    result = result.replace('\\', '/')
    return result


def load_name_set_from_csv(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        field_names = ['id', 'name']
        all_row = []
        csv_reader = csv.DictReader(f, field_names)
        for row in csv_reader:
            if row['name'] is None:
                continue
            all_row.append(row['name'])

        return all_row
    pass


def get_category_form_path(path):
    # 从类别目录读入数据
    count_dic = {}
    files = os.listdir(path)
    for cat in files:
        list = os.listdir(os_path_join(path, cat))
        num = len(list)
        count_dic[cat] = num

    return count_dic
    pass


# 将这一步跟最后一步分开，提高可读性
def make_final_list(path, x:bool):
    # 按照csv表排序，生成报告顺序的list
    flag = True
    final_list = []
    count_dic = get_category_form_path(path)
    all_row = load_name_set_from_csv(os_path_join(os.getcwd(), 'class_reporter.csv'))
    for i, name in enumerate(all_row):
        if name in count_dic.keys():
            final_list.append(count_dic[name])
            flag = False
            continue
        final_list.append(0)
    if flag and x:
        final_list = multiple_files_list(path)

    return final_list
    pass


def multiple_files_list(path):
    total_final_list = []
    files = os.listdir(path)
    for i,cat in enumerate(files):
        new_path = os.path.join(path, cat)
        final_list = make_final_list(new_path, False)
        for ii in range(len(final_list)):
            if i == 0:
                total_final_list.append(final_list[ii])
            else:
                total_final_list[ii] += final_list[ii]

    return total_final_list


def get_arr(path):
    # 返回类别个数和百分比两个二维数组
    final_list = make_final_list(path, True)
    percent_list = []
    arr_blood_num = np.array(final_list)
    sum = np.sum(arr_blood_num)
    for num in final_list:
        if num == 0:
            percent_list.append(0)
            continue
        percent_list.append(round(num / sum, 4) * 100)
    arr_blood_percent = np.array(percent_list)

    # TODO 髓片待做，这里是血片*2
    arr_num = np.stack((arr_blood_num, arr_blood_num), axis=1)
    # 虽然这个也是36*2，但是不影响，界面需要改
    arr_percent = np.stack((arr_blood_percent, arr_blood_percent), axis=1)

    return arr_num, arr_percent
    pass


if __name__ == '__main__':
    path = 'D:\Blood\SU\\thosix\\root\szh-man-20-17\categorys'
    print(get_arr(path))
