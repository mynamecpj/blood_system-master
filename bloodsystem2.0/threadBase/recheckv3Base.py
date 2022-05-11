# ! /usr/bin/env python3
# coding=utf-8
import glob
import time
import cv2
import numpy as np
import shelve
import torch
import matplotlib.pyplot as plt
from PIL import Image
from PyQt5.QtCore import pyqtSignal, QThread
from config import Config
from torch.nn import functional as F
from sklearn.decomposition import PCA
from utils.fileAlgorithm import *


def get_hist(img: np.ndarray) -> list:
    hist = lambda x: [cv2.calcHist([i], [0], None, [256], [0.0, 255.0]) for i in x]
    return hist(cv2.split(img))


def hist_score(tar_hist, pre_hist):
    # tar_img = cv2.imdecode(np.fromfile(tar_img, dtype=np.uint8), -1)
    # pre_img = cv2.imdecode(np.fromfile(pre_img, dtype=np.uint8), -1)
    decoder = lambda x: [i for i in x]
    print(tar_hist.shape)
    tar_b, tar_g, tar_r = decoder(tar_hist)

    pre_b, pre_g, pre_r = decoder(pre_hist)

    b_score = abs(sum(tar_b - pre_b))
    g_score = abs(sum(tar_g - pre_g))
    r_score = abs(sum(tar_r - pre_r))
    # print("id",self.img_path, "score:", b_score, g_score, r_score)
    if b_score < 1e-9 and g_score < 1e-9 and r_score < 0.03:
        return True
    else:
        return False


def cmpHash(hash1, hash2):
    # Hash值对比
    # 算法中1和0顺序组合起来的即是图片的指纹hash。顺序不固定，但是比较的时候必须是相同的顺序。
    # 对比两幅图的指纹，计算汉明距离，即两个64位的hash值有多少是不一样的，不同的位数越小，图片越相似
    # 汉明距离：一组二进制数据变成另一组数据所需要的步骤，可以衡量两图的差异，汉明距离越小，则相似度越高。汉明距离为0，即两张图片完全一样
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n


def dHash(img):
    # 差值哈希算法
    # 缩放8*8
    img = cv2.resize(img, (9, 8))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str


def pHash(img):
    # 感知哈希算法
    # 缩放32*32
    img = cv2.resize(img, (32, 32))  # , interpolation=cv2.INTER_CUBIC
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct = cv2.dct(np.float32(gray))
    # opencv实现的掩码操作
    dct_roi = dct[0:8, 0:8]
    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash


def calc_sift(img):
    # img = cv2.imdecode(np.fromfile(img, dtype=np.uint8), -1)
    # surf = cv2.xfeatures2d.SURF_create(150)
    # key, des = surf.detectAndCompute(img, None)
    # img = cv2.resize(img, (128, 128))
    sift = cv2.xfeatures2d.SIFT_create()
    kp1, des = sift.detectAndCompute(img, None)
    if isinstance(des, np.ndarray):
        return des
    else:
        return None


def match(des1, des2, rate, threshold):
    FLANN_INDEX_KDTREE = 0

    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
    search_params = dict(checks=10)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    if not isinstance(des1, np.ndarray) or not isinstance(des2, np.ndarray):
        return None
    if len(des1) < len(des2):
        matches = flann.knnMatch(des1, des2, k=1)
    elif len(des1) == len(des2):
        return ((des1[0] - des2[0]) ** 2).sum() < rate
    else:
        matches = flann.knnMatch(des2, des1, k=1)
    good = []
    for m in matches:
        if m[0].distance < rate:
            good.append(m)

    if len(good) / len(matches) > threshold:

        return True
    else:
        return False


class RecheckThread(QThread):
    finishSignal = pyqtSignal(list, str)

    def __init__(self,
                 db_name="base",
                 redb_name="repetition",
                 forward_search_num=200,
                 ths_hash=12,
                 ths_hist=0.96,
                 rate=200,
                 threshold=0.65,
                 ):

        """Image rechecking.
        Using a three-layer structure to determine whether the image is repeated.
        first layer:Hash fingerprint
        second layer:Color histogram
        third layer:SIFT
        Args:
            db_name: __database name.   会创建bak、dat、dir后缀的文件，如果保存了500张图片的建议更改其他名字保存下一批500张图片
                                        因为不会覆盖，所以查重的时候会把之前的500张也算进去
            redb_name: __database name for Duplicate picture. 同上
            forward_search_num: 向前查找的次数  default：全部
            ths_hash: hash指纹查找阈值
            ths_hist: 颜色直方图阈值
            rate: 特征距离的阈值
            threshold: 特征提取阶段输出阈值
        """
        super(RecheckThread, self).__init__()
        self.db_name = db_name
        self.redb_name = redb_name
        self.__fsn = forward_search_num
        self.__ths_hash = ths_hash
        self.__ths_hist = ths_hist
        # 特征提取的阈值设置
        self.__rate = rate
        self.__threshole = threshold
        # 重复数目
        self.sum = 0
        self.__re_dup = []

        # 记录重复图片数据库的大小
        self.__label_num = 0
        self.__dup_num = 0

        # 文件路径
        self.mode = None
        self.path = None

    def upload_img(self, img_path: str):
        self.img_path = img_path
        if cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1) is None:
            return
        else:
            self.img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)

    def first_layer(self, hash):
        review_hash = []
        if len(self.__database.items()) > self.__fsn:

            for pre_img, pre_value in list(self.__database.items())[0:]:
                review_hash += [pre_img] if cmpHash(hash, pre_value["hash"]) < self.__ths_hash else []
        else:

            for pre_img, pre_value in self.__database.items():
                review_hash += [pre_img] if cmpHash(hash, pre_value["hash"]) < self.__ths_hash else []
        return review_hash

    def second_layer(self, hist, review_hash):
        review_hist = []

        for path in review_hash:

            if abs(hist - self.__database[path]["hist"]) < 16:
                review_hist.append(path)
        return review_hist

    def third_layer(self, des, review_hist):
        review_sift = []

        for path in review_hist:

            if match(des, self.__database[path]["descriptor"], self.__rate, self.__threshole):
                review_sift.append(path)

        return review_sift, des

    def process(self):
        self.__database = shelve.open(self.db_name)
        self.redb = shelve.open(self.redb_name)
        k = np.ones((256, 1))
        k = np.cumsum(k, dtype=np.int).reshape((256, 1)) / 256

        hf = lambda h: np.where(np.logical_and(h > 0.25, h < 1), 8,
                                np.where(np.logical_and(h > 0.005, h <= 0.25), 6,
                                         np.where(np.logical_and(h > 0.001, h <= 0.005), 4,
                                                  np.where(
                                                      np.logical_and(h > 0.0, h <= 0.001),
                                                      2, np.where(h == 0, -2, h)))))
        if len(self.__database) == 0:
            size = self.img.shape[0] * self.img.shape[1]
            arr = np.array(get_hist(self.img))
            h1 = hf(arr[0] / size) * k
            h1_s = sum(h1)
            h2 = hf(arr[1] / size) * k
            h2_s = sum(h2)
            h3 = hf(arr[2] / size) * k
            h3_s = sum(h3)
            h_s = h1_s + h2_s + h3_s
            hist = sum(h1_s / h_s * h1 + h2_s / h_s * h2 + h3_s / h_s * h3)[0]
            hash = pHash(self.img)

            des = calc_sift(self.img)
            self.__database[self.img_path] = self.__database.get(self.img_path,
                                                                 {"hist": hist, "num": 1, "size": size, "hash": hash,
                                                                  "descriptor": des})
            return
        if self.img_path in self.__database.keys():
            return

        size = self.img.shape[0] * self.img.shape[1]

        arr = np.array(get_hist(self.img))

        h1 = hf(arr[0] / size) * k
        h1_s = sum(h1)
        h2 = hf(arr[1] / size) * k
        h2_s = sum(h2)
        h3 = hf(arr[2] / size) * k
        h3_s = sum(h3)
        h_s = h1_s + h2_s + h3_s
        hist = sum(h1_s / h_s * h1 + h2_s / h_s * h2 + h3_s / h_s * h3)[0]

        hash = pHash(self.img)
        des = calc_sift(self.img)
        review_hash = self.first_layer(hash)
        review_hist = self.second_layer(hist, review_hash)

        review_sift, des = self.third_layer(des, review_hist)
        if len(review_sift) == 0:
            self.__database[self.img_path] = self.__database.get(self.img_path,
                                                                 {"num": len(self.__database) + 1, "hist": hist,
                                                                  "size": size,
                                                                  "hash": hash, "descriptor": des})
        elif len(review_sift) > 0:
            a = []
            for i in review_sift:
                a.append(self.__database[i]["num"])
            n = sorted(a)[0]
            for j in review_sift:
                self.__database[j]["num"] = n
            self.__database[self.img_path] = self.__database.get(self.img_path,
                                                                 {"num": n, "hist": hist, "size": size,
                                                                  "hash": hash,
                                                                  "descriptor": des})
            self.redb["s{}".format(n)] = self.redb.get("s" + str(n), []) + review_sift + [self.img_path]
        self.close()

    def update(self):
        """
        更新重复的数目
        """
        self.__database = shelve.open(self.db_name)
        self.redb = shelve.open(self.redb_name)
        m = lambda x: sum([len(i) for i in x])
        if self.__label_num < len(self.redb) or self.__dup_num < m(list(self.redb.values())):
            s = 0
            for i, j in self.redb.items():
                self.redb[i] = list(set(j))
                s += len(list(set(j))) - 1
            self.__label_num = len(self.redb)
            self.__dup_num = m(list(self.redb.values()))
            self.sum = s
        self.close()

    def close(self):
        self.__database.close()
        self.redb.close()

    def get_rep_num(self):
        return self.sum

    def run(self):
        path = self.path
        files = get_dir_all_file(path)
        for i in files:
            self.upload_img(i)
            self.process()
        self.update()
        redb = shelve.open("repetition")
        repeat_images = []
        for i, j in redb.items():
            repeat_images.append(j)
        self.finishSignal.emit(repeat_images, self.mode)

        os.remove('repetition.bak')
        os.remove('repetition.dat')
        os.remove('repetition.dir')
        os.remove('base.bak')
        os.remove('base.dat')
        os.remove('base.dir')

        self.quit()

        pass
