# encoding: utf-8
"""
@author: red0orange
@file: popDialogUtils.py
@time:  下午8:00
@desc:
"""
import random

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QDialog, QWidget, QMainWindow, QGraphicsScene, \
    QGraphicsPixmapItem, QApplication
from PyQt5.QtCore import Qt, QObject, QTimer
from ui.new_cls_dialog import Ui_NewClsDialog
from ui.rename_file_dialog import Ui_renamefileDialog
from ui.get_patient_inf_dialog import Ui_Get_Patient_Inf_Dialog
from ui.camera_setting_dialog import Ui_camera_setting_dialog
from ui.register import Ui_register_Dialog


def pop_prompt(parent, mstr: str):
    """
    弹出一个提示
    :param parent:
    :param mstr:显示的字符
    :return:
    """
    QMessageBox.information(parent, "提示", parent.tr(mstr))
    # QMessageBox.setTextInteractionFlags(Qt.TextSelectableByMouse)
    pass


def pop_file_dialog(parent, whichClass: str, tips, *args, **kwargs):
    """
    弹出文件选择
    :param parent:
    :param whichClass: 选择文件夹还是文件
    :param tips: 显示的提示
    :param args: 额外参数
    :param kwargs: 额外参数
    :return:
    """
    if whichClass == 'dir':
        result = QFileDialog.getExistingDirectory(
            parent=parent, caption=tips, directory=kwargs.get('directory'))
    elif whichClass == 'file':
        result, _ = QFileDialog.getOpenFileName(
            parent=parent, caption=tips, directory=kwargs.get('directory'), filter=kwargs.get('filter'))
    else:
        result = None
    if result == '':
        result = None
    return result


def pop_question(parent, tips, **kwargs):
    """
    弹出询问对错窗口
    :param parent:
    :param tips: 提示
    :param kwargs: 额外参数
    :return:
    """
    answer = QMessageBox.question(parent, "提示", parent.tr(tips),
                                  QMessageBox.Ok | QMessageBox.Cancel,
                                  QMessageBox.Cancel)
    if answer == QMessageBox.Ok:
        return 1
    else:
        return 0


def pop_timer_message_box(parent, text, time, **kwargs):
    """
    弹出一个定时关闭的提示窗口，之后可以改成进度条窗口
    :param parent:
    :param text: 显示的提示文字
    :param time: 多久关闭
    :param kwargs: 自定义QMessageBox的其他参数
    :return:
    """
    messageBox = QMessageBox(text=text, parent=parent)
    timer = QTimer()
    timer.setInterval(time)
    timer.timeout.connect(messageBox.close)
    timer.start()
    messageBox.exec()
    pass


def pop_confirm_dialog(parent, text):
    "弹出确认对话框，并显示传入的提示内容"
    answer = QMessageBox.question(parent, '确认操作', text)
    if answer == QMessageBox.Yes:
        return True
    return False


def pop_warning_dialog(parent, text):
    "弹出警告窗口"
    QMessageBox.warning(parent, '警告', text)
    pass


def pop_text_dialog(parent, default_text):
    t_dialog = QDialog(parent=parent)
    t_dialog.ui = Ui_renamefileDialog()
    t_dialog.ui.setupUi(t_dialog)
    t_dialog.ui.lineEdit.setPlaceholderText(default_text)
    if t_dialog.exec() == QDialog.Accepted:
        new_name = t_dialog.ui.lineEdit.text()
        return new_name
    pass


def pop_get_patient_inf_dialog(parent):
    p_dialog = QDialog(parent=parent)
    p_dialog.ui = Ui_Get_Patient_Inf_Dialog()
    p_dialog.ui.setupUi(p_dialog)
    if p_dialog.exec() == QDialog.Accepted:
        patient_name = p_dialog.ui.name_text.text()
        patient_gender = p_dialog.ui.gender_text.text()
        patient_age = p_dialog.ui.age_text.text()
        patient_bed = p_dialog.ui.bed_nub_text.text()
        patient_take_pack = p_dialog.ui.take_pack_text.text()
        patient_picture_number = p_dialog.ui.picture_number_text.text()

        information1 = "".join([patient_name, '-', patient_gender, '-', patient_age, '-', patient_bed, '-', patient_take_pack, '-',patient_picture_number])

        return information1
    pass

def pop_camera_setting_dialog(parent):
    c_dialog = QDialog(parent=parent)
    c_dialog.ui = Ui_camera_setting_dialog()
    c_dialog.ui.setupUi(c_dialog)
    if c_dialog.exec() == QDialog.Accepted:
        try:
            Hue = int(c_dialog.ui.hue.text())
            Contrast = int(c_dialog.ui.contrast.text())
            Saturation = int(c_dialog.ui.saturation.text())
            ExpoTime = int(c_dialog.ui.ExpoTime.text())
            ExpoAGain = int(c_dialog.ui.ExpoAGain.text())
            Gamma = int(c_dialog.ui.Gamma.text())
        except ValueError:
            return None
        return [Hue, Contrast, Saturation, ExpoTime, ExpoAGain, Gamma]
    else :
        pass
    pass

def pop_color_dialog(parent):
    m_dialog = QDialog(parent=parent)
    m_dialog.ui = Ui_NewClsDialog()
    m_dialog.ui.setupUi(m_dialog)
    m_dialog.ui.REdit.setText(str(random.randint(0, 255)))
    m_dialog.ui.GEdit.setText(str(random.randint(0, 255)))
    m_dialog.ui.BEdit.setText(str(random.randint(0, 255)))
    m_dialog.ui.okButton.pressed.connect(m_dialog.accept)
    m_dialog.ui.okButton.pressed.connect(m_dialog.close)
    m_dialog.ui.cancelButton.pressed.connect(m_dialog.close)
    if m_dialog.exec() == QDialog.Accepted:
        className = m_dialog.ui.lineEdit.text()
        try:
            R = int(m_dialog.ui.REdit.text())
            G = int(m_dialog.ui.GEdit.text())
            B = int(m_dialog.ui.BEdit.text())
        except BaseException:
            m_dialog.close()
            pop_prompt(parent, '颜色格式错误,请重新选择')
            return
        m_dialog.close()
        return className, (R, G, B)
    return None, None


def pop_save_file_dialog(parent, **kwargs):
    file_path, _ = QFileDialog.getSaveFileName(parent, "save file", "export.xml", **kwargs)
    if file_path == '':
        file_path = None
    return file_path

def pop_register_dialog(parent,base_code):
    r_dialog = QDialog(parent=parent)
    r_dialog.ui = Ui_register_Dialog()
    r_dialog.ui.setupUi(r_dialog)
    r_dialog.ui.label_3.setText(base_code)
    if r_dialog.exec() == QDialog.Accepted:
        password = r_dialog.ui.lineEdit.text()
        limit_time = r_dialog.ui.lineEdit_2.text()
        return [password,limit_time]
        pass