import os


def path_preprocess(path):
    """
    对输入的path进行预处理，如将\\变成/
    Args:
        path (str):

    Returns:

    """
    return path.replace('\\', '/')


def get_dir_all_file(dir):
    """获得某个路径下所有子文件的完整路径名"""
    result = []
    for roots, dirs, files in os.walk(dir):
        for file in files:
            result.append(os_path_join(roots, file))
    return result


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


def _path_to_same_str(p_fn):
    "path -> str, but same on nt+posix, for alpha-sort only"
    s_fn = str(p_fn)
    s_fn = s_fn.replace('\\', ' ')
    s_fn = s_fn.replace('/', ' ')
    return s_fn


def if_dic(l: str):
    l = list(l.split(" "))
    if '.' in l[-1]:
        return False
    else:
        return True


def get_all_file_path(dir: str):
    """获得某个路径下所有文件的全名"""
    return [os_path_join(dir, os.listdir(dir)[i])
            for i in range(len(os.listdir(dir)))]


if __name__ == '__main__':

    tmp = "D:/Blood/SU/thosix/root"
    base = get_all_file_path(tmp)
    for i in base:
        tmple = if_dic(_path_to_same_str(i))
        if tmple:
            print(i)
            case = get_all_file_path(i)
            for k in case:
                print(k)
                dase = get_all_file_path(k)
                for n in dase:
                    print(n)
