try:
    from PySide6.QtWidgets import QMainWindow, QApplication, QMenu,QMessageBox
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QTreeWidget
    from PySide6.QtWidgets import QLabel, QLineEdit, QComboBox
    from PySide6.QtWidgets import QPushButton, QWidget, QTreeWidgetItem
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtGui import QPixmap, QCursor
    from PySide6.QtCore import Qt, QFile
    import shutil
except:
    from PySide2.QtWidgets import QMainWindow, QApplication, QMenu,QMessageBox
    from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QTreeWidget
    from PySide2.QtWidgets import QLabel, QLineEdit, QComboBox
    from PySide2.QtWidgets import QPushButton, QWidget, QTreeWidgetItem
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtGui import QPixmap, QCursor
    from PySide2.QtCore import Qt, QFile
    import shutil
import importlib
import os
import sys
import time
sys.path.append('/nas/Batz_Maru/pingu/nana/yenyaong/')
import sg_api
from singleton_sg import Singleton_SG
import json
from login_stylemanager import StyleManager,ErrorMessageManager

class Login_UI:

    def __init__(self):
        """로그인 후 로더 UI를 띄울 수 있게 하는 클래스"""
        print("연결이~~~ 됐습니다~~~!!!!~!~@@!~!@")
        init_sg = Singleton_SG()
        self.sg = init_sg.sg

        self.get_users()
        self.load_ui()
        self.center_window()

        self.name = self.ui.lineEdit_name
        self.mail = self.ui.lineEdit_mail

        # self.name.setText("전예나")
        # self.mail.setText("yenajun0319@gmail.com")

        self.ui.pushButton.clicked.connect(self.check_id)

        self.name.returnPressed.connect(self.check_id)
        self.mail.returnPressed.connect(self.check_id)

        StyleManager.apply_styles(self.ui)
        StyleManager.load_images(self.ui)


    def get_users(self):
        """샷그리드에서 사용자의 정보를 받는 함수"""

        self.users = list(self.sg.find(
            "HumanUser", 
            [["email","is_not",None]],
            ['login','firstname','lastname','id']
        ))
        return self.users

    def check_id(self):
        """샷그리드에서 받은 사용자들의 정보들과 사용자에게 받은 정보가 맞는 지 확인하는 함수"""
        input_name = self.name.text().strip()
        input_mail = self.mail.text().strip()

        matched_user = None
        # count = 0
        for user in self.users:
            last_name = user['lastname']
            first_name = user['firstname']
            name = f"{last_name}{first_name}"

            if name == input_name and input_mail == user['login']:
                matched_user = user
                break

        if matched_user:
            self.user_name = f"{matched_user['lastname']}{matched_user['firstname']}"
            self.user_id = matched_user['id']
            self.get_user_info()
            self.open_main_ui() 

            self.ui.close()

        else:
            self.show_error_message()

    def get_user_info(self):
        """사용자의 정보를 받아 한 파일에 저장시키는 함수
        만들어진 파일은 loader, publisher에 쓰일 예정"""
        
        user_dict = {}
        user_file = '/nas/Batz_Maru/pingu/nana/merge/user_info.json'
        current_time = time.strftime('%y/%m/%d  %X ')
        user_dict = {
            
            'name' : self.user_name , 'id' : self.user_id, 'connection_time' : current_time
        }

        with open(user_file,"w") as f:
                json.dump(user_dict, f, indent=4, ensure_ascii=False)
        if 'user_info':
            print('json 생성됨')
            print(user_dict)

        print('sg_api에 보냇서여')


    def show_error_message(self):
        """사용자의 정보가 맞지 않으면 에러창을 띄우는 함수"""

        ErrorMessageManager.show_error_message(self.ui)

    def open_main_ui(self):
        """로더 ui를 여는 함수"""
        print(" main ui 열어보겟서여")
        try:
            
            import loader
            self.w = loader.MainCtrl()

        except ImportError as e:
            print(f"Error importin load_ui : {e}")

    def load_ui(self):
        """로그인 UI 하는 함수 """
        ui_file_path = "/nas/Batz_Maru/pingu/nunu/login.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file)

        self.ui.show()
        print(" UI open")
        ui_file.close()


    def center_window(self):
        """UI를 화면 중앙에 배치하는 함수"""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        ui_geometry = self.ui.frameGeometry()
        center_point = screen_geometry.center()

        ui_geometry.moveCenter(center_point)
        self.ui.move(ui_geometry.topLeft())



if __name__=="__main__": 
    # app = QApplication().instance()
    # if not app:
    app = QApplication()
    window = Login_UI()
    app.exec()