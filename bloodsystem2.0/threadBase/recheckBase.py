# encoding: utf-8
"""
@author: Hehaisen, Soshio
@file: recheckBase.py
@time:  下午1:56
@desc:
"""
import math
import cv2
from PyQt5.QtCore import pyqtSignal, QThread
from utils.fileAlgorithm import *


def get_hist(img: np.ndarray) -> list:
    hist = lambda x: [cv2.calcHist([i], [0], None, [4], [0.0, 255.0]) for i in x]
    return hist(cv2.split(img))


def get_one_hist(img: np.ndarray) -> list:
    hist1 = cv2.calcHist([img], [0], None, [180], [0.0, 360.0])
    # hist2 = cv2.calcHist([img] , [1] , None , [3] , [0.0 , 360.0]).reshape(3,1).sum(1)/img.shape[0]/img.shape[1]
    # print("hist",hist1.reshape(3,60).sum(1)/img.shape[0]/img.shape[1])

    hist1 = hist1.reshape(3, 60).sum(1) / img.shape[0] / img.shape[1]
    out = np.exp(1 / (0.1 + abs(hist1[0] - hist1[1]) + abs(hist1[1] - hist1[2]) + abs(hist1[0] - hist1[2])))
    # print("out",out)
    return out


def img_code(img_hist):
    k1 = []
    k3 = []
    g1 = np.concatenate([img_hist[0], img_hist[1], img_hist[2]], 0).flatten()
    for i in range(11):
        if g1[i] > g1[i + 1]:
            k1.append(1)
        else:
            k1.append(0)

        if g1[i] == 0:
            k3.append(1)
        else:
            k3.append(0)
    return k1 + k3


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


q1 = [i for i in range(17 * 17)]
q2 = []
for j in [-72, -73, -74, -75, -76, -77, -78, -79, -80, -81, -82, -83, -84, -85, -86, -87]:
    for i in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]:
        q2.append(j + i)
# k1 = [i for i in range(-8,9,1)]
# for j in k1:
#     for i in k1:
#         q2.append((j,i))
# q2 = [-i*10-j for j in [8,7,6,5,4,3,2,1,-1,-2,-3,-4,-5,-6,-7,-8] for i in [8,7,6,5,4,3,2,1,-1,-2,-3,-4,-5,-6,-7,-8]  ]
q = dict(zip(q2, q1))
m = [1, 0, -1, 0, 1, 0, -1, 0]


def c(hash):
    hash = np.array(hash).reshape((8, 8))

    hash_h = hash
    hash_v = hash
    num_h = sum(hash_h.sum(axis=1) * m)
    num_v = sum(hash_v.sum(axis=1) * m)
    nh = math.ceil(num_h / 2)
    nv = math.ceil(num_v / 2)

    return q[nh * 10 + nv]


# c(np.random.randint(0,2,(8,8)))
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
                 db_name="laji",
                 redb_name="repetition",
                 forward_search_num=200,
                 ths_hash=12, #这个可以调高点，但不要太高 12-18
                 ths_hist=0.96,# 可以把这个调低点 0.90-0.96
                 rate=200,
                 threshold=0.65,#这个也是0.45-0.65
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
        # self.redb_name = redb_name
        self.__fsn = forward_search_num
        self.__ths_hash = ths_hash
        self.__ths_hist = ths_hist
        # 特征提取的阈值设置
        self.__rate = rate
        self.__threshole = threshold
        # 重复数目
        self.sum = 0
        self.__re_dup = []
        self.sc = []
        self.n = []

        # self.redb.clear()
        # self.__database.clear()
        # 记录重复图片数据库的大小
        self.__label_num = 0
        self.__dup_num = 0
        self.redb = {}
        self.__database  = {}
        self.k = np.ones((8, 2))
        e = np.array([1, 1, 1, 1, 1, 1, 1, 1]).reshape(8, 1) / 8
        self.k = (self.k * e).reshape(16, 1)

        # 运行参数
        self.path = None
        self.mode = None

    def upload_img(self, img_path: str):
        self.img_path = img_path
        self.img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)


    def first_layer(self, hash, x):
        review_hash = []
        self.n.sort(key=lambda x: x[1])
        for i, j in self.n:


            if j == x - 15:
                review_hash += [(i, self.__database[i]["h"], self.__database[i]["hist"])] if cmpHash(hash,
                                                                                                     self.__database.get(
                                                                                                         i)[
                                                                                                         "hash"]) < self.__ths_hash else []
            elif j >= x - 2 and j <= x + 2:

                review_hash += [(i, self.__database[i]["h"], self.__database[i]["hist"])] if cmpHash(hash,
                                                                                                     self.__database.get(
                                                                                                         i)[
                                                                                                         "hash"]) < self.__ths_hash else []
            elif j == x + 15:

                review_hash += [(i, self.__database[i]["h"], self.__database[i]["hist"])] if cmpHash(hash,
                                                                                                     self.__database.get(
                                                                                                         i)[
                                                                                                         "hash"]) < self.__ths_hash else []
        return review_hash

    def second_layer(self, h, hist, review_hash):
        review_hist = []
        for path, sh, sco in review_hash:
            if sh < h - 1.5:
                continue
            elif sh > 1.5 + h:
                continue
            else:

                if cmpHash(hist, sco) < 4:
                    review_hist.append(path)
        return review_hist

    def third_layer(self, des, review_hist):
        review_sift = []

        for path in review_hist:
            if match(des, self.__database[path]["descriptor"], self.__rate, self.__threshole):
                review_sift.append(path)
        return review_sift, des

    def process(self):
        #self.__database = shelve.open(self.db_name)
        if len(self.__database) == 0:
            hist = np.array(get_hist(self.img))
            h1 = (hist[0] + hist[1] + hist[2]).reshape(2, 2).sum(1)
            hist = img_code(hist)
            h1 = np.log(1 / (0.1 + abs(h1[0] - h1[1])))
            self.sc.append((self.img_path, hist))
            hash = pHash(self.img)
            self.n.append((self.img_path, c(hash)))
            des = calc_sift(self.img)
            self.__database[self.img_path] = self.__database.get(self.img_path,
                                                                 {"num": len(self.__database) + 1, "hist": hist,
                                                                  "h": h1, "hash": hash,
                                                                  "descriptor": des})
            return
        if self.img_path in self.__database.keys():
            return
        hist = np.array(get_hist(self.img))
        h1 = (hist[0] + hist[1] + hist[2]).reshape(2, 2).sum(1)

        h1 = np.log(1 / (0.5 + abs(h1[0] - h1[1])))

        hist = img_code(hist)

        hash = pHash(self.img)

        x = c(hash)
        des = calc_sift(self.img)
        review_hash = self.first_layer(hash, x)

        self.n.append((self.img_path, x))

        review_hist = self.second_layer(h1, hist, review_hash)
        self.sc.append((self.img_path, hist))

        review_sift, des = self.third_layer(des, review_hist)
        if len(review_sift) == 0:
            self.__database[self.img_path] = self.__database.get(self.img_path,
                                                                 {"num": len(self.__database) + 1, "hist": hist,
                                                                  "h": h1,

                                                                  "hash": hash, "descriptor": des})
        elif len(review_sift) > 0:
            a = []
            for i in review_sift:
                a.append(self.__database[i]["num"])
            n = sorted(a)[0]
            for j in review_sift:
                self.__database[j]["num"] = n
            self.__database[self.img_path] = self.__database.get(self.img_path,
                                                                 {"num": n, "hist": hist, "h": h1,
                                                                  "hash": hash,
                                                                  "descriptor": des})
            self.redb["s{}".format(n)] = self.redb.get("s" + str(n), []) + review_sift + [self.img_path]

        #self.close()

    def update(self):
        """
        更新重复的数目
        """
        #self.__database = shelve.open(self.db_name)
        m = lambda x: sum([len(i) for i in x])
        if self.__label_num < len(self.redb) or self.__dup_num < m(list(self.redb.values())):
            s = 0
            for idx, (i, j) in enumerate(self.redb.items()):
                self.redb[i] = list(set(j))

                s += len(list(set(j))) - 1
            self.__label_num = len(self.redb)
            self.__dup_num = m(list(self.redb))
            self.sum = s
        #self.close()

    def close(self):
        self.__database.close()

    def get_rep_num(self):
        return self.sum

    def get_rep_pho(self):
        return list(self.redb.values())

    def run(self):
        path = self.path
        files = get_dir_all_file(path)
        for i in files:
            self.upload_img(i)
            self.process()
        self.update()
        repeat_images = self.get_rep_pho()
        self.finishSignal.emit(repeat_images, self.mode)
        # os.remove('laji.bak')
        # os.remove('laji.dat')
        # os.remove('laji.dir')
        self.__database={}
        self.n=[]
        self.quit()
        pass
