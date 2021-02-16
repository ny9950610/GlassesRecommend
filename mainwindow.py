import cv2
import os
import faceShapeRecognizer
import pictureCompound

from PySide2 import QtCore
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QTimer
from PySide2.QtWidgets import QPushButton, QLabel, QTextBrowser
from PySide2.QtWidgets import QScrollArea, QTabWidget, QWidget
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtGui import QImage, QPixmap, QIcon, QColor


class Mainwindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.setupCamera()
        self.window.show()

    def setupUI(self):
        # 載入ui檔"mainwindow.ui"
        path = os.path.join(os.path.dirname(__file__), "mainwindow.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(uiFile)
        uiFile.close()

        # 設定widget
        # 所有widget都要在前面加上self 否則其他function無法使用那個widget

        # 顯示攝影機畫面
        self.imageLabel = self.window.findChild(QLabel, 'imageLabel')

        # 按一下拍照 將畫面定格
        self.btn_takePict = self.window.findChild(QPushButton, 'btn_takePict')
        self.btn_takePict.clicked.connect(self.takePicture)

        # 按一下取消畫面定格
        self.btn_cancelTakePict = self.window.findChild(QPushButton, 'btn_cancelTakePict')
        self.btn_cancelTakePict.clicked.connect(self.cancelTakePicture)

        # 按一下把臉上的眼鏡清空
        self.btn_revert = self.window.findChild(QPushButton, 'btn_revert')
        self.btn_revert.clicked.connect(self.revert)

        # 提示user按下拍照件 並在拍照後顯示user臉型
        self.faceshapeOfUser = self.window.findChild(QTextBrowser, "faceshapeOfUser")
        self.faceshapeOfUser.setText("按下拍照來確認自己臉型")

        # 按下拍照後 會顯示適合的眼鏡 依照眼鏡類型分類
        self.tabWidget = self.window.findChild(QTabWidget, "tabWidget")
        self.numOfTab = 0

    def setupCamera(self):
        # 打開鏡頭
        self.capture = cv2.VideoCapture(0)
        # 設定大小
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)
        # 顯示畫面
        self.timer = QTimer()
        self.timer.timeout.connect(self.displayVideoStream)
        self.timer.start(30)

    def displayVideoStream(self):
        _, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.flip(frame, 1)
        self.image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))

    """ 下面是設定glassesButton的function """

    """
    在tabWidget中 放很多個tab 代表各種眼鏡種類
    每個tab會放一個scrollArea
    每個scrollArea中放一個QWidget(稱buttons)
    buttons中放許多pushButton
    每個pushButton都代表一個眼鏡 按下就讓畫面中的人戴上眼鏡
    """

    def setTabWidget(self, faceShape):
        # glassesShape[0]存絕配眼鏡 glassesShape[1]存可搭配的眼鏡
        path = os.path.join(os.path.dirname(__file__), "datas", "recommendType", faceShape + ".txt")
        fin = open(path, 'r')

        # 第一次讀絕配眼鏡 第二次讀可搭配的眼鏡
        for i in range(2):
            num = int(fin.readline())
            for j in range(num):
                glassesShape = fin.readline().strip("\n")
                # 建立一個tabWidget
                tab = self.createScrollArea(glassesShape)
                self.tabWidget.addTab(tab, glassesShape)

                # 將絕配眼鏡種類和可搭配眼鏡種類以字體顏色做出區別
                if i == 0:
                    # 絕配為綠色
                    self.tabWidget.tabBar().setTabTextColor(j, QColor(0, 100, 0))
                if i == 1:
                    # 可搭配為黃色
                    self.tabWidget.tabBar().setTabTextColor(self.numOfTab+j, QColor(255, 165, 0))

            self.numOfTab += num

    def createScrollArea(self, glassesType):
        scrollArea = QScrollArea()
        scrollArea.setWidget(self.setButtons(glassesType))
        return scrollArea

    def setButtons(self, glassesType):
        buttons = QWidget()
        layout = QVBoxLayout()
        glassesFileAddr = "images/glasses/" + str(glassesType)
        path = os.path.join(os.path.dirname(__file__), glassesFileAddr)

        # 根據資料夾中眼鏡照片的數量來依序建立按鈕
        for i in range(self.numOfGlasses(path)):
            glassesImgAddr = glassesFileAddr + "/" + str(i+1) + ".png"
            path = os.path.join(os.path.dirname(__file__), glassesImgAddr)

            btn = QPushButton()
            btn.setIcon(QIcon(path))
            btn.setIconSize(QtCore.QSize(128, 128))
            btn.pressed.connect(lambda val=glassesImgAddr: self.putOnGlasses(val))
            layout.addWidget(btn)

        buttons.setLayout(layout)
        return buttons

    def numOfGlasses(self, filePath):
        # fileInfo有三種資料
        # fileInfo[0]為檔案位址 fileInfo[1]為子資料夾名稱 fileInfo[2]為資料夾內檔案名稱
        fileInfo = next(os.walk(filePath))
        return len(fileInfo[2])

    """ 上面是設定glassesButton的function """

    @QtCore.Slot()
    def takePicture(self):
        if not self.timer.isActive(): return
        self.timer.stop()

        _, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.flip(frame, 1)
        self.image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        path = os.path.join(os.path.dirname(__file__), "images", "saved.jpg")
        self.image.save(path, "JPG")

        faceShape = faceShapeRecognizer.run()

        if(faceShape == "error1" or faceShape == "error2" or faceShape == "error3"):
            self.faceshapeOfUser.setText("請取消重拍 並再試一次")
        else:
            self.faceshapeOfUser.setText("你是"+faceShape+"臉")
            self.setTabWidget(faceShape)

    @QtCore.Slot()
    def cancelTakePicture(self):
        self.timer.start(30)

        # 刪除glassesButtons
        for i in range(self.numOfTab):
            self.tabWidget.removeTab(0)

        self.numOfTab = 0
        self.faceshapeOfUser.setText("按下拍照來確認自己臉型")

    @QtCore.Slot()
    def revert(self):
        if self.timer.isActive(): return
        path = os.path.join(os.path.dirname(__file__), "images", "saved.jpg")
        self.imageLabel.setPixmap(QPixmap.fromImage(path))

    @QtCore.Slot(str)
    def putOnGlasses(self, str):
        pictureCompound.run(str)
        path = os.path.join(os.path.dirname(__file__), "images", "result.jpg")
        self.image = QImage(path)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
