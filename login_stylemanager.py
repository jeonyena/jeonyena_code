try:
    from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit, QDialog, QVBoxLayout, QHBoxLayout
    from PySide6.QtGui import QPixmap, QMovie
    from PySide6.QtCore import Qt, QSize
except:
    from PySide2.QtWidgets import QLabel, QPushButton, QLineEdit, QDialog, QVBoxLayout, QHBoxLayout
    from PySide2.QtGui import QPixmap, QMovie
    from PySide2.QtCore import Qt, QSize


class StyleManager:
    """
    UI 스타일을 관리하는 클래스.
    다른 UI에서도 동일한 스타일을 적용할 수 있도록 범용적으로 사용 가능.
    """
    
    @staticmethod
    def apply_styles(ui):
        """UI 요소에 스타일을 적용하는 함수"""
        
        # Label 정렬 설정
        for label in [ui.label_text_name, ui.label_text_mail, ui.label_text_main]:
            label.setAlignment(Qt.AlignCenter)
        
        # 공통 스타일 설정
        line_edit_style = """
            QLineEdit {
                border: 2px solid #fdcb01;
                border-radius: 10px;
                padding: 5px;
                font: bold 16px "Comic Sans MS";
                background-color: #FFF8DC;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #FFF8DC;
                background-color: #feeca4;
            }
        """
        
        label_style = """
            QLabel {
                font-family: "Comic Sans MS", cursive, sans-serif;
                font-size: 17px;
                font-weight: bold;
                color: #fdcb01;
            }
        """
        
        button_style = """
            QPushButton {
                border: 2px solid #fdcb01;
                border-radius: 10px;
                padding: 8px;
                font: bold 16px "Comic Sans MS";
                background-color: #FFF8DC;
                color: #333333;
            }
            QPushButton:hover {
                background-color: #feeca4;
                border: 2px solid #feeca4;
            }
            QPushButton:pressed {
                background-color: #fdd835;
                border: 2px solid #fbc02d;
            }
        """
        
        # 스타일 적용
        ui.lineEdit_name.setStyleSheet(line_edit_style)
        ui.lineEdit_mail.setStyleSheet(line_edit_style)
        
        ui.pushButton.setStyleSheet(button_style)
        
        ui.label_text_name.setStyleSheet(label_style)
        ui.label_text_mail.setStyleSheet(label_style)
        
        ui.label_text_main.setStyleSheet("""
            QLabel {
                font-family: "Comic Sans MS", cursive, sans-serif;
                font-size: 55px;
                font-weight: bold;
                color: #fdcb01;
            }
        """)
    
    @staticmethod
    def load_images(ui):
        """QLabel에 이미지 로드 및 크기 조절"""
        base_path = "/nas/Batz_Maru/pingu/imim/login"

        image_settings = {
            "label_image_1": (f"{base_path}/angel_right.png", 100),
            "label_image_2": (f"{base_path}/angel_left.png", 100),
            "label_image_3": (f"{base_path}/attendance.png", 70),
        }

        for label_name, (img_path, size) in image_settings.items():
            label = getattr(ui, label_name, None)
            if label:
                pixmap = QPixmap(img_path)
                pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 크기 조절
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)  # 중앙 정렬




class ErrorMessageManager:
    """오류 메시지 창을 스타일링하고 표시하는 클래스"""
    
    @staticmethod
    def show_error_message(parent):
        """스타일이 적용된 오류 메시지 창을 띄우는 함수"""
        
        dialog = QDialog(parent)
        dialog.setWindowTitle("입력 오류")
        dialog.setFixedSize(350, 160)  # 크기 조절
        
        dialog.setStyleSheet("background-color: #1c1c1c; border-radius: 10px;")  # 다이얼로그 배경색 적용
        
        img_path = "/nas/Batz_Maru/pingu/imim/gif/sorry.gif"
        movie = QMovie(img_path)
        movie.setScaledSize(QSize(100, 100))  # GIF 크기 조정
        
        gif_label = QLabel(dialog)
        gif_label.setMovie(movie)
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()  # GIF 애니메이션 시작
        
        movie.finished.connect(movie.start)
        
        text_label = QLabel("<p style='color: #FFF8DC; font-size: 14px; font-weight: bold;'>"
                            "Log-in Failed! <br> Please try again.</p>", dialog)
        text_label.setAlignment(Qt.AlignVCenter)
        
        ok_button = QPushButton("  확인  ", dialog)
        ok_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #fdcb01;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
                background-color: #feeca4;
                color: #333333;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fdd835;
                border: 2px solid #fbc02d;
            }
            QPushButton:pressed {
                background-color: #fdcb01;
                border: 2px solid #fbc02d;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        
        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        
        content_layout.addWidget(gif_label)
        content_layout.addWidget(text_label)
        content_layout.setAlignment(Qt.AlignCenter)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(content_layout)
        main_layout.addLayout(button_layout)
        
        dialog.setLayout(main_layout)
        dialog.exec_()
