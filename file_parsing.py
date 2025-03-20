try :
    from PySide6.QtWidgets import QMessageBox,QApplication
except :
    from PySide2.QtWidgets import QMessageBox,QApplication
from pathlib import Path
import re
import sys


class FileParser:
    """파일 경로를 파싱하는 클래스"""

    MAYA_SEQ_PATTERN = re.compile(
        r"^/nas/Batz_Maru/(?P<project>[^/]+)/(?P<work_dir>[^/]+)/(?P<seq_name>[^_]+)_(?P<shot_num>\d{4})_(?P<step>[^/]+)/(?P<work_space>[^_]+)/(?P=seq_name)_(?P=shot_num)_(?P<version>v\d+)\.(?P<ext>\w+)$"
    )

    MAYA_ASSET_PATTERN = re.compile(
        r"^/nas/Batz_Maru/(?P<project>[^/]+)/(?P<work_dir>[^/]+)/(?P<asset_name>.+?)_(?P<asset_type>[^_]+)_(?P<step>[^/]+)/(?P<work_space>[^_]+)/(?P=asset_name)_(?P<version>v\d+)\.(?P<ext>\w+)$"
    )

    SEQ_PATTERN = re.compile(
        r"^/nas/Batz_Maru/(?P<project>[^/]+)/(?P<work_dir>[^/]+)/(?P<seq_name>[^_]+)_(?P<shot_num>\d{4})_(?P<step>[^/]+)/(?P=seq_name)_(?P=shot_num)_(?P<version>v\d+)\.(?P<ext>\w+)$"
    )

    ASSET_PATTERN = re.compile(
        r"^/nas/Batz_Maru/(?P<project>[^/]+)/(?P<work_dir>[^/]+)/(?P<asset_name>.+?)_(?P<asset_type>[^_]+)_(?P<step>[^/]+)/(?P=asset_name)_(?P<version>v\d+)\.(?P<ext>\w+)$"
    )

    def info():
        """
        모듈처럼 사용되어 파일을 파싱하는 클래스입니다
        파일 파싱이 필요할 때 file_parsing을 임포트한 후 클래스를 인스턴스로 생성시켜 사용합니다

        사용예시 :  
                import file_parsing

                def file_parse():
                    parser = file_parsing.FileParser(path)      # path에는 파싱하고 싶은 파일의 경로에 대한 변수입니다

                    self.matching_key = parser.key              # key는 파일의 패턴을 찾아주는 변수값입니다
                    print(self.matching_key)                    # key는 (maya seq/aseet, seq, asset 총 네 가지의 패턴을 가집니다)

                    self.parsed = parser.data                   # data는 file_parsing에 종속되어 있는 변수값입니다
                    print(self.parsed['project'])               # data는 딕셔너리 형태로 파싱된 파일을 변환해줍니다

                    """

    def __init__(self, file_path: str):
        """파일 경로를 기반으로 정보 파싱"""

        self.str_path = file_path                           
        self.data = {}                         
        self.file_path = Path(file_path)                   
        self.file_name = self.file_path.stem              
        self.file_ext = self.file_path.suffix[1:] if self.file_path.suffix else "" 
        self.version = self.extract_version()             
        self.file_exists = self.file_path.exists()        
            
        self.project = None
        self.work_dir = None
        self.seq_name = None
        self.shot_num = None
        self.asset_type = None
        self.asset_name = None
        self.step = None
        self.work_space = None
        self.version = None

        self.parse_path() 


    def extract_version(self):
        """파일명에서 v001 버전 정보 추출"""
        match= re.search(r"v(\d+)", self.file_name)
        return int(match.group(1)) if match else None
    

    def parse_path(self):
        patterns = [
            ('maya_seq',self.MAYA_SEQ_PATTERN),
            ('maya_asset',self.MAYA_ASSET_PATTERN),
            ('seq',self.SEQ_PATTERN),
            ('asset',self.ASSET_PATTERN)
        ]

        matched = False
        self.matched_key = None

        for key, pattern in patterns:
            match = pattern.match(self.str_path)
            
            
            if not matched :
                print("No pattern matched for the given file path.")

            if match:
                self.data = match.groupdict()
                self.matched_key = key

                print(f"matched pattern : {key}")
                print(f"data : {self.data}")

                if key == 'maya_asset':
                    self.project = self.data.get('project')
                    self.work_dir = self.data.get('work_dir')
                    self.asset_type = self.data.get('asset_type')
                    self.asset_name = self.data.get('asset_name')
                    self.step = self.data.get('step')
                    self.work_space = self.data.get('work_space')
                    self.version = self.data.get('version')
                    self.ext = self.data.get('ext')

                elif key == 'maya_seq':
                    self.project = self.data.get('project')
                    self.work_dir = self.data.get('work_dir')
                    self.seq_name = self.data.get('seq_name')
                    self.shot_num = self.data.get('shot_num')
                    self.step = self.data.get('step')
                    self.work_space = self.data.get('work_space')
                    self.version = self.data.get('version')
                    self.ext = self.data.get('ext')

                elif key == 'asset': 
                    self.project = self.data.get('project')
                    self.work_dir = self.data.get('work_dir')
                    self.asset_type = self.data.get('asset_type')
                    self.asset_name = self.data.get('asset_name')
                    self.step = self.data.get('step')
                    self.version = self.data.get('version')
                    self.ext = self.data.get('ext')

                elif key == 'seq':
                    self.project = self.data.get('project')
                    self.work_dir = self.data.get('work_dir')
                    self.seq_name = self.data.get('seq_name')
                    self.shot_num = self.data.get('shot_num')
                    self.step = self.data.get('step')
                    self.version = self.data.get('version')
                    self.ext = self.data.get('ext')

                matched = True
                break


