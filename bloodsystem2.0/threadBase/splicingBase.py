# encoding: utf-8
"""
@author: Lizilan, Soshio
@file: recheckBase.py
@time:  下午1:56
@desc:
"""
import cv2
import time
import os
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
from utils.utils import cv_imread
from utils.fileAlgorithm import *


def HLS(img, img_exm):
    HLS_img = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    (H, L, S) = cv2.split(HLS_img)
    Schange = cv2.mean(img_exm)[2] - cv2.mean(img)[2]
    Lchange = cv2.mean(img_exm)[1] - cv2.mean(img)[1]
    Hchange = cv2.mean(img_exm)[0] - cv2.mean(img)[0]
    Hresult = cv2.add(H, Hchange)
    Sresult = cv2.add(S, Schange)
    Lresult = cv2.add(L, Lchange)
    imgresult = cv2.merge((H, Lresult, Sresult))
    result = cv2.cvtColor(imgresult, cv2.COLOR_HLS2BGR)

    return result


def TemplateMatchingRight(sourceRaw, new_image, coordinate1, coordinate2):
    source = sourceRaw[coordinate1[1]:coordinate2[1], coordinate1[0]:coordinate2[0]]
    Hsource, Wsource = source.shape[:2]
    roi1 = new_image[int(new_image.shape[0] * 0.5):, :400, :]
    roi2 = new_image[:int(new_image.shape[0] * 0.5), :400, :]
    Hroi, Wroi = roi1.shape[:2]
    n = 1
    SetWsource = Wsource / n
    while SetWsource >= Wroi * 7:
        n = n + 1
        SetWsource = Wsource / n

    Setsource = source[:, Wsource - int(SetWsource):, :]
    result1 = cv2.matchTemplate(Setsource, roi1, cv2.TM_SQDIFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(result1)
    result2 = cv2.matchTemplate(Setsource, roi2, cv2.TM_SQDIFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result2)
    if min_val1 >= min_val2:
        min_val = min_val2
        # loc = [min_loc2[0]+int(SetWsource),min_loc2[1]]
        loc = [min_loc2[0] + Wsource - int(SetWsource) + coordinate1[0], min_loc2[1] + coordinate1[1]]
        roiLocation = "up"
    else:
        min_val = min_val1
        loc = [min_loc1[0] + Wsource - int(SetWsource) + coordinate1[0], min_loc1[1] + coordinate1[1]]
        roiLocation = "low"
    return loc, min_val, roiLocation


def TemplateMatchingLeft(sourceRAW, new_image, coordinate1, coordinate2):
    source = sourceRAW[coordinate1[1]:coordinate2[1], coordinate1[0]:coordinate2[0]]
    Hsource, Wsource = source.shape[:2]
    roi1 = new_image[int(new_image.shape[0] * 0.5):, new_image.shape[1] - 400:, :]
    roi2 = new_image[:int(new_image.shape[0] * 0.5), new_image.shape[1] - 400:, :]
    Hroi, Wroi = roi1.shape[:2]
    n = 1
    SetWsource = Wsource / n
    while SetWsource >= Wroi * 7:
        n = n + 1
        SetWsource = Wsource / n
    Setsource = source[:, :int(SetWsource), :]
    result1 = cv2.matchTemplate(Setsource, roi1, cv2.TM_SQDIFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(result1)
    result2 = cv2.matchTemplate(Setsource, roi2, cv2.TM_SQDIFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result2)
    if min_val1 >= min_val2:
        min_val = min_val2
        loc = [min_loc2[0] + coordinate1[0], min_loc2[1] + coordinate1[1]]
        roiLocation = "up"
    else:
        min_val = min_val1
        loc = [min_loc1[0] + coordinate1[0], min_loc1[1] + coordinate1[1]]
        roiLocation = "low"

    # cv2.namedWindow("loc",0)
    # cv2.imshow("loc",source[314:,286:])
    # cv2.waitKey(0)
    return loc, min_val, roiLocation


def TemplateMatchingDown(sourceRAW, new_image, coordinate1, coordinate2):
    source = sourceRAW[coordinate1[1]:coordinate2[1], coordinate1[0]:coordinate2[0]]
    Hsource, Wsource = source.shape[:2]
    roi1 = new_image[0:400, :int(new_image.shape[1] * 0.5), :]
    roi2 = new_image[0:400, int(new_image.shape[1] * 0.5):, :]
    Hroi, Wroi = roi1.shape[:2]
    n = 1
    SetHsource = Hsource / n
    while SetHsource >= Hroi * 7:
        n = n + 1
        SetHsource = Hsource / n
    Setsource = source[-int(SetHsource):, :, :]
    result1 = cv2.matchTemplate(Setsource, roi1, cv2.TM_SQDIFF_NORMED)
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(result1)
    result2 = cv2.matchTemplate(Setsource, roi2, cv2.TM_SQDIFF_NORMED)
    min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result2)
    if min_val1 >= min_val2:
        min_val = min_val2
        loc = [min_loc2[0] + coordinate1[0], min_loc2[1] + Hsource - int(SetHsource) + coordinate1[1]]
        roiLocation = "Right"
    else:
        min_val = min_val1
        loc = [min_loc1[0] + coordinate1[0], min_loc1[1] + Hsource - int(SetHsource) + coordinate1[1]]
        roiLocation = "Left"
        # cv2.rectangle(source, (loc[0],loc[1]), (loc[0] + Wroi, loc[1] + Hroi), (0, 0, 225),3)
        # cvshow(source, "source")

    return loc, min_val, roiLocation


def SplicingRight(source, new_image, loc, roiLocation):
    Xmat, Ymat = loc[:2]
    Hsource, Wsource = source.shape[:2]
    Hnew_image, Wnew_image = new_image.shape[:2]
    if roiLocation == "up":
        Xroi, Yroi = 0, 0
    else:
        Xroi, Yroi = 0, int(new_image.shape[0] * 0.5)
    if Yroi >= Ymat:
        expUp = Yroi - Ymat
        if expUp < 0:
            expUp = 0
        expBe = 0
    else:
        expUp = 0
        # expBe = Ymat - Yroi
        expBe = Ymat - Yroi + Hnew_image - Hsource
        if expBe < 0:
            expBe = 0
        # if Ymat -Yroi + Hnew_image + expBe < Hsource:
        #     expBe = 0
    expLe = 0
    expRi = Wnew_image - Xroi - Wsource + Xmat
    if expRi < 0:
        expRi = 0
    background = cv2.copyMakeBorder(source, expUp, expBe, expLe, expRi, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    result = background.copy()
    if Yroi >= Ymat:
        result[Ymat - Yroi + expUp:Ymat - Yroi + expUp + Hnew_image, Xmat - Xroi:Xmat - Xroi + Wnew_image] = new_image
        coordinate1 = (Xmat - Xroi, 0)
    else:
        # result[result.shape[0] - Hnew_image:, Xmat - Xroi:Xmat - Xroi + Wnew_image] = new_image
        result[Ymat - Yroi:Ymat - Yroi + Hnew_image, Xmat - Xroi:Xmat - Xroi + Wnew_image] = new_image
        coordinate1 = (Xmat - Xroi, result.shape[0] - Hnew_image)
    coordinate2 = (coordinate1[0] + Wnew_image, coordinate1[1] + Hnew_image)
    return result, coordinate1, coordinate2


def SplicingLeft(source, new_image, loc, roiLocation):
    Xmat, Ymat = loc[:2]
    Hsource, Wsource = source.shape[:2]
    Hnew_image, Wnew_image = new_image.shape[:2]
    if roiLocation == "up":
        Xroi, Yroi = Wnew_image - 400, 0
    else:
        Xroi, Yroi = Wnew_image - 400, int(Hnew_image * 0.5)

    if Yroi >= Ymat:
        expUp = Yroi - Ymat - (source.shape[0] - new_image.shape[0])

        if expUp < 0:
            expUp = 0

        expBe = 0
    else:
        expUp = 0
        expBe = Ymat - Yroi - (source.shape[0] - new_image.shape[0])

        if expBe < 0:
            expBe = 0

        # expBe = Ymat - Yroi
    expLe = Xroi - Xmat
    if expLe < 0:
        expLe = 0

    expRi = 0
    background = cv2.copyMakeBorder(source, expUp, expBe, expLe, expRi, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    result = background.copy()
    if Yroi >= Ymat:
        result[int(Ymat - Hnew_image * 0.5):int(Ymat + Hnew_image * 0.5),
        int(Xmat - Wnew_image + 400):int(Xmat + 400)] = new_image
        coordinate1 = (Xmat - Wnew_image + 400, Ymat - Hnew_image * 0.5)
    else:

        result[Ymat:Ymat + Hnew_image, Xmat + expLe - Wnew_image + 400:Xmat + expLe + 400] = new_image
        coordinate1 = (Xmat + expLe - Wnew_image + 400, Ymat)
    coordinate2 = (coordinate1[0] + Wnew_image, coordinate1[1] + Hnew_image)
    return result, coordinate1, coordinate2


def SplicingDown(source, new_image, loc, roiLocation):
    Xmat, Ymat = loc[:2]
    Hsource, Wsource = source.shape[:2]
    Hnew_image, Wnew_image = new_image.shape[:2]
    if roiLocation == "Left":
        Xroi, Yroi = 0, 0
    else:
        Xroi, Yroi = int(new_image.shape[1] * 0.5), 0
    if Xroi <= Xmat:
        expRi = Wnew_image - Wsource + Xmat + Xroi
        if expRi < 0:
            expRi = 0
        # expRi = Xmat - Xroi - 9843
        expLe = 0
    else:
        expRi = 0
        expLe = Xroi - Xmat
        if expLe < 0:
            expLe = 0
    expUp = 0
    expBe = Hnew_image - Yroi - Hsource + Ymat
    background = cv2.copyMakeBorder(source, expUp, expBe, expLe, expRi, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    result = background.copy()
    if Xroi <= Xmat:
        result[Ymat - Yroi:, Xmat - Xroi:Xmat - Xroi + Wnew_image] = new_image
        # coordinate1 = (result.shape[1] - Wnew_image, result.shape[0] - Hnew_image)    #有错！！！
        coordinate1 = (Xmat - Xroi, Ymat - Yroi)
    else:
        result[Ymat - Yroi:, :Wnew_image] = new_image
        # coordinate1 = (0, result.shape[0] - Hnew_image)
        coordinate1 = (Xmat - Xroi, Ymat - Yroi)
    coordinate2 = (coordinate1[0] + Wnew_image, coordinate1[1] + Hnew_image)
    return result, coordinate1, coordinate2


class SplicingThread(QThread):
    finishSignal = pyqtSignal(str)

    def __init__(self):
        super(SplicingThread, self).__init__()
        self.is_First = True
        self.first_image_path = None
        self.new_image_path = None
        self.whole_dir_path = None
        self.whole_image_save_path = None
        self.coordinate1 = None
        self.coordinate2 = None
        self.direction = 1

    def insert_image(self, image_path):
        if self.is_First:
            self.coordinate1 = (0, 0)
            self.first_image_path = image_path
        else:
            self.new_image_path = image_path

    def run(self):
        if self.is_First:
            image = cv_imread(self.first_image_path)
            self.whole_image_save_path = os_path_join(self.whole_dir_path, 'whole_image.jpg')
            # cv2.imwrite(self.whole_image_save_path, image)
            cv2.imencode('.jpg', image)[1].tofile(self.whole_image_save_path)

            self.coordinate2 = (image.shape[1], image.shape[0])
            self.finishSignal.emit(self.whole_image_save_path)
            self.quit()

        else:
            whole_image = cv_imread(self.whole_image_save_path)
            first_image = cv_imread(self.first_image_path)
            new_image = cv_imread(self.new_image_path)
            new_image = HLS(new_image, first_image)
            coordinate1 = self.coordinate1
            coordinate2 = self.coordinate2
            result = None

            if self.direction == 1:
                locRight, minvalRight, roiLocationRight = TemplateMatchingRight(whole_image, new_image, coordinate1,
                                                                                coordinate2)
                locDown, minvalDown, roiLocationDown = TemplateMatchingDown(whole_image, new_image, coordinate1,
                                                                            coordinate2)
                if minvalRight <= minvalDown:
                    result, coordinate1, coordinate2 = SplicingRight(whole_image, new_image, locRight, roiLocationRight)
                    self.direction = 1
                elif minvalRight > minvalDown:
                    result, coordinate1, coordinate2 = SplicingDown(whole_image, new_image, locDown, roiLocationDown)
                    self.direction = 3
                # else:
                #     judge = 0

            elif self.direction == 3:
                locLeft, minvalLeft, roiLocationLeft = TemplateMatchingLeft(whole_image, new_image, coordinate1,
                                                                            coordinate2)
                locRight, minvalRight, roiLocationRight = TemplateMatchingRight(whole_image, new_image, coordinate1,
                                                                                coordinate2)
                if minvalLeft <= minvalRight:
                    result, coordinate1, coordinate2 = SplicingLeft(whole_image, new_image, locLeft, roiLocationLeft)
                    self.direction = 2
                elif minvalLeft > minvalRight:
                    result, coordinate1, coordinate2 = SplicingRight(whole_image, new_image, locRight, roiLocationRight)
                    self.direction = 1
                # else:
                #     judge = 0

            elif self.direction == 2:
                locLeft, minvalLeft, roiLocationLeft = TemplateMatchingLeft(whole_image, new_image, coordinate1,
                                                                            coordinate2)
                locDown, minvalDown, roiLocationDown = TemplateMatchingDown(whole_image, new_image, coordinate1,
                                                                            coordinate2)
                if minvalLeft <= minvalDown:
                    result, coordinate1, coordinate2 = SplicingLeft(whole_image, new_image, locLeft, roiLocationLeft)
                    self.direction = 2
                elif minvalLeft > minvalDown:
                    result, coordinate1, coordinate2 = SplicingDown(whole_image, new_image, locDown, roiLocationDown)
                    self.direction = 3

            self.coordinate1 = coordinate1
            self.coordinate2 = coordinate2
            os.remove(self.whole_image_save_path)
            self.whole_image_save_path = os_path_join(self.whole_dir_path, 'whole_image.jpg')
            # cv2.imwrite(self.whole_image_save_path, result)
            cv2.imencode('.jpg', result)[1].tofile(self.whole_image_save_path)
            self.finishSignal.emit(self.whole_image_save_path)
            self.quit()

        if self.is_First:
            self.is_First = False

        pass
