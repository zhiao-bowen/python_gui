import os
import sys

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPainter, QPixmap, QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit


class CustomWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(320, 450)
        self.setWindowIcon(QIcon(self.resource_path("app_icon.ico")))
        # 设置背景图片
        self.setStyleSheet("background: transparent;")
        self.QPixmap = QPixmap(self.resource_path('src/bg.png'))
        # 设置窗口设置按钮
        self.button_setting= QPushButton(self)
        self.button_setting.setGeometry(270, 8, 12, 14)
        self.button_setting.setIcon(QIcon(self.resource_path("src/setting.png")))
        self.button_setting.clicked.connect(lambda: print("setting button clicked!"))
        # 设置窗口关闭按钮
        self.button_close = QPushButton(self)
        self.button_close.setGeometry(290, 1, 32, 29)
        self.button_close.setIcon(QIcon(self.resource_path("src/close.png")))
        self.button_close.setIconSize(QSize(32,29))
        self.button_close.setStyleSheet("QPushButton:hover {background: red;}")
        self.button_close.clicked.connect(self.close)
        # 头像
        self.label_avatar = QLabel(self)
        self.label_avatar.setGeometry(120,64,80,80)
        self.label_avatar.setPixmap(QPixmap(self.resource_path("src/avatar.png")))
        # 输入QQ号
        self.label_edit_qq = QLabel(self)
        self.label_edit_qq.setGeometry(32, 169, 256, 40)
        self.label_edit_qq.setPixmap(QPixmap(self.resource_path("src/qq_edit.png")))
        self.edit_qq=QLineEdit(self)
        # 加载字体
        otf_path = self.resource_path("src/SourceHanSansSC-Regular-2.otf")
        font_id = QFontDatabase.addApplicationFont(otf_path)
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        font_name = font_families[0]
        # font_name = "黑体"
        font = QFont(font_name)
        font.setWeight(QFont.Bold)
        self.edit_qq.setFont(font)
        self.edit_qq.setGeometry(32, 169, 256, 40)
        self.edit_qq.setStyleSheet("""
                    QLineEdit {
                        background: transparent;
                        border: none;
                        color: white;
                        font-size: 16px;
                    }
                """)
        self.edit_qq.setAlignment(Qt.AlignCenter)
        self.edit_qq.setPlaceholderText("输入PP号")
        # 输入密码
        self.label_edit_pass = QLabel(self)
        self.label_edit_pass.setGeometry(32, 223, 256, 40)
        self.label_edit_pass.setPixmap(QPixmap(self.resource_path("src/qq_edit.png")))
        self.edit_pass = QLineEdit(self)
        font.setWeight(QFont.Black)
        self.edit_pass.setFont(font)
        self.edit_pass.setGeometry(32, 223, 256, 40)
        self.edit_pass.setAlignment(Qt.AlignCenter)
        self.edit_pass.setPlaceholderText("输入PP密码")
        self.edit_pass.setEchoMode(QLineEdit.Password)
        self.edit_pass.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
            }
            QLineEdit[echoMode="2"] {
                lineedit-password-character: 9679; 
            }
        """)
        # 协议勾选按钮
        self.radio_agree = QPushButton(self)
        self.radio_agree.setGeometry(32, 280, 17, 17)
        self.radio_agree.setIcon(QIcon(self.resource_path("src/radio.png")))
        self.radio_agree.setIconSize(QSize(17, 17))
        self.choice = False
        self.radio_agree.clicked.connect(self.radio_agree_clicked)
        # 协议勾选信息
        self.label_agree = QLabel(self)
        self.label_agree.setGeometry(52, 282, 222, 15)
        self.label_agree.setPixmap(QPixmap(self.resource_path("src/radio_info.png")))
        # 登录按钮
        self.button_login = QPushButton(self)
        self.button_login.setGeometry(32, 320, 256, 35)
        self.button_login.setIcon(QIcon(self.resource_path("src/button_login.png")))
        self.button_login.setIconSize(QSize(256, 35))
        self.button_login.clicked.connect(self.login)
        timer = QTimer(self)
        timer.timeout.connect(self.can_login)
        timer.start(10)
        # 注册账号按钮
        self.button_create = QPushButton(self)
        self.button_create.setGeometry(93, 399, 56, 21)
        self.button_create.setIcon(QIcon(self.resource_path("src/create_account.png")))
        self.button_create.setIconSize(QSize(56, 21))
        self.button_create.clicked.connect(self.create_account)
        # 分割线
        self.label_line = QLabel(self)
        self.label_line.setGeometry(160, 404, 2, 12)
        self.label_line.setPixmap(QPixmap(self.resource_path("src/line.png")))
        # 更多选项按钮
        self.button_more = QPushButton(self)
        self.button_more.setGeometry(170, 399, 56, 21)
        self.button_more.setIcon(QIcon(self.resource_path("src/more_options.png")))
        self.button_more.setIconSize(QSize(56, 21))

        # 拖动相关变量
        self._is_dragging = False
        self._drag_pos = None

    # 勾选同意
    def radio_agree_clicked(self):
        self.choice = not self.choice
        if self.choice:
            self.radio_agree.setIcon(QIcon(self.resource_path("src/radio_true.png")))
        else:
            self.radio_agree.setIcon(QIcon(self.resource_path("src/radio.png")))
    # 可登录检测
    def can_login(self):
        qq = self.edit_qq.text()
        password = self.edit_pass.text()
        if password and qq and self.choice:
            self.button_login.setIcon(QIcon(self.resource_path("src/button_login_true.png")))
        else:
            self.button_login.setIcon(QIcon(self.resource_path("src/button_login.png")))
    # 登录
    def login(self):
        qq = self.edit_qq.text()
        password = self.edit_pass.text()
        if qq and password and self.choice:
            # 连接服务器
            self.connect_server(qq, password)

    # 网络连接
    def connect_server(self, qq, password):
        # 这里可以添加连接服务器的代码
        pass

    # 注册账号
    def create_account(self):
        # 这里可以添加注册账号的代码
        pass

    # 资源路径拼接
    def resource_path(self,relative_path):
        if hasattr(sys, '_MEIPASS'):  # 打包后环境
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        self._drag_pos = None
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.QPixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CustomWindow()
    win.show()
    sys.exit(app.exec_())
