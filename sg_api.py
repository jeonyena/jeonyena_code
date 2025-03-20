import os
from shotgun_api3 import Shotgun
import file_parsing
import json
from singleton_sg import Singleton_SG



class MyTask:
      def __init__(self, user_id, project):
            """ShotGrid 태스크 데이터를 로드하고 폴더 경로를 생성하는 클래스"""           

            init_sg = Singleton_SG()
            self.sg = init_sg.sg
            self.user_id = user_id

            self.project_id = self.get_project_id(project)
            self.tasks = self.get_tasks()
            self.entities = self.get_entities(self.tasks)
            self.folders = self.create_folders(self.tasks)
            self.path_list = self.create_paths(project)

            self.display_folders()

      def get_project_id(self, project):
        """ShotGrid에서 프로젝트 ID를 조회하는 함수"""

        filters = [
            ['users', 'is', {'type': "HumanUser", 'id': self.user_id}],
            ['name', 'is', project]
        ]
        project_data = self.sg.find_one("Project", filters, ['id', 'name'])

        if not project_data:
            raise ValueError(f" {project}  없어여")

        return project_data['id']

      def get_tasks(self):
        """유저의 태스크 조회하는 함수"""

        filters = [
            ['task_assignees', 'is', {'type': 'HumanUser', 'id': self.user_id}],
            ['project', 'is', {'type': 'Project', 'id': self.project_id}]
        ]
        fields = ['start_date', 'due_date', 'entity','status'
                   'content', 'step', 'sg_description', 'duration']

        tasks = self.sg.find("Task", filters, fields)
        print(f"tasks in get tasks : {tasks}")
        
        if not tasks:
            raise ValueError(" 태스크 없어여")
        
        return tasks

      def get_entity_fields(self):
        """엔티티 타입별 필드 매핑하는 함수"""
        
        return {
            'Asset': ['id', 'code', 'sg_asset_type'],
            'Shot': ['id', 'code']
        }

      def get_entities(self,tasks):
        """태스크에서 엔티티 정보 조회하는 함수"""

        entity_types = {task['entity']['type'] for task in tasks}
        entity_fields = self.get_entity_fields()

        entities = {}
        for entity_type in entity_types:
            entity_names = {
                task['entity']['name']
                for task in tasks if task['entity']['type'] == entity_type
            }
            if not entity_names:
                continue

            filters = [
                ['project', 'is', {'type': 'Project', 'id': self.project_id}],
                ['code', 'in', list(entity_names)]
            ]
            entity_list = self.sg.find(entity_type, filters, entity_fields[entity_type])

            for entity in entity_list:
                entities[entity['code']] = entity  

        return entities

      def create_folders(self,tasks):
        """태스크와 엔티티 정보를 조합해 폴더명 생성하는 함수"""

        folders = set()

        for task in tasks:
            entity_name = task['entity']['name']
            step_name = task['step']['name']
            entity_type = task['entity']['type']

            if entity_type == 'Shot':
                folders.add(f"{entity_name}_{step_name}")
            else:
                entity = self.entities.get(entity_name)
                if entity:
                    folders.add(f"{entity_name}_{entity['sg_asset_type']}_{step_name}")

        return list(folders)

      def create_paths(self, project):
        """폴더명들을 기반으로 경로 생성"""
            
        return [f"/nas/Batz_Maru/{project}/work/{folder}" for folder in self.folders]

      def display_folders(self):
            """폴더 리스트를 보내는 함수"""

            print(f"path list: {self.path_list}")
            return self.path_list





class SGPublisher:
      def __init__(self,pub_dict):
            """ShotGrid 퍼블리시를 처리하는 클래스"""

            print("예나의 고생끝 sg publisher 시작하것습ㅈ니다. 끝내주는 코드 시작~~!!@")

            if pub_dict is None:
                  raise ValueError("Error: SGPublisher에 전달된 pub_dict가 None입니다.")
            if 'pub_files' not in pub_dict:
                  raise KeyError("Error: pub_dict에 'pub_files' 키가 없습니다.")

            print(f"받은 pub_dict: {pub_dict}") 

            self.sg = Singleton_SG().sg  
            self.published_files = []  
            self.version_id = None  
            
            self.pub_dict = self.get_dict(pub_dict)  
            
            self.user_id = self.get_user_id()

            self.parsed_data = self.parse_file_path(pub_dict['pub_files']['pub_maya'])
            self.project = self.get_project_id(self.parsed_data['project'])

            self.entity = self.get_entity_id(self.project, self.parsed_data['type_info'], self.parsed_data['entity_type'])
            self.task = self.get_task_id(self.project, self.entity, self.parsed_data['step'], self.parsed_data['entity_type'])

            self.publish_data = self.create_publish_files_data()
            self.create_and_publish_files()

            version_data = self.create_version_data()
            self.create_version(version_data)


      def get_dict(self,pub_dict):
            """딕셔너리를 받는 함수입니다"""

            self.pub_dict = pub_dict

            if pub_dict['pub_files']['pub_maya']:
                  print(f"got publish dictionary : {pub_dict}")
            else:
                  print("없더여")

            maya_file = self.parse_file_path(pub_dict['pub_files']['pub_maya'])
            

            self.pub_dict['parsed_data'] = maya_file  
            return self.pub_dict 


      def get_user_id(self):
            """json에서 사용자 아이디 가져오기"""

            json_file_path = '/nas/Batz_Maru/pingu/nana/user_info.json'
            with open(json_file_path, 'r', encoding='utf-8') as file:
                  user_info = json.load(file)
            return user_info.get('id')

      def parse_file_path(self, path):
            """파일 경로를 파싱하여 프로젝트, 엔티티, 태스크 정보 추출"""

            parser = file_parsing.FileParser(path)
            self.parsed = parser.data
            self.key = parser.matched_key

            f_project = self.parsed.get('project')
            f_work_dir = self.parsed.get('work_dir')
            f_step = self.parsed.get('step')

            if self.key in ['maya_seq', 'seq']: 
                  f_type_info = f"{self.parsed.get('seq_name')}_{self.parsed.get('shot_num')}"
                  f_entity_type = 'Shot'
            else:
                  f_type_info = self.parsed.get('asset_name')
                  f_entity_type = 'Asset'

            parsed_data = {
                  'project': f_project,
                  'work_dir': f_work_dir,
                  'entity_type' : f_entity_type,
                  'type_info': f_type_info,
                  'step': f_step,
            }
            
            print(f" parsed file data: {parsed_data}")
            return parsed_data


      def get_project_id(self, project_name):
            """프로젝트 ID 조회"""
            project = self.sg.find_one("Project", [['name', 'is', project_name]], ['id'])
            if not project:
                  raise ValueError(f"Error: Project '{project_name}' 없음")
            return project

      def get_entity_id(self, project, type_info, entity_type):
            """엔티티 ID 조회 (Shot 또는 Asset)"""
            entity = self.sg.find_one(entity_type, [
                  ['project', 'is', {'type': 'Project', 'id': project['id']}],
                  ['code', 'is', type_info]
            ], ['id'])
            if not entity:
                  raise ValueError(f"Error: {entity_type} '{type_info}' 없음")
            return entity

      def get_task_id(self, project, entity, step, entity_type):
            """태스크 ID 조회"""
            task = self.sg.find_one("Task", [
                  ['project', 'is', {'type': 'Project', 'id': project['id']}],
                  ['entity', 'is', {'type': entity_type, 'id': entity['id']}],
                  ['content', 'is', step]
            ], ['id'])
            if not task:
                  raise ValueError(f"Error: Task '{step}' 없음")
            return task

      def create_publish_files_data(self):
            """퍼블리시할 파일들의 데이터를 생성"""


            if not hasattr(self, 'pub_dict'):
                  raise AttributeError("Error: self.pub_dict가 존재하지 않습니다. __init__에서 초기화되었는지 확인하세요.")

            if 'pub_files' not in self.pub_dict:
                  print(f" Warning: self.pub_dict에 'pub_files' 키가 없습니다. 복구 시도 중...")
                  self.pub_dict = self.get_dict(self.pub_dict)  

            if 'pub_files' not in self.pub_dict:
                  raise KeyError("Error: self.pub_dict에 'pub_files' 키가 없습니다.")

            print(f"디버깅: create_publish_files_data에서 self.pub_dict = {self.pub_dict}")
 
            
            files = [self.pub_dict['pub_files']['pub_maya']] + self.pub_dict['pub_files']['Cache_abc_list']
            return [
                  {
                  'project': {'type': 'Project', 'id': self.project['id']},
                  'code': file_path,
                  'task': {'type': 'Task', 'id': self.task['id']},
                  'entity': {'type': self.parsed_data['entity_type'], 'id': self.entity['id']},
                  'path': {'local_path': file_path},
                  'description': self.pub_dict['pub_info']['description']
                  }
                  for file_path in files
            ]

      def create_and_publish_files(self):
            """ShotGrid에 퍼블리시 파일을 생성"""
            for publish_data in self.publish_data:
                  self.create_publish_file(publish_data)

      def create_publish_file(self, data):
            """퍼블리시 파일 생성"""
            result = self.sg.create("PublishedFile", data)
            self.published_files.append(result['id'])
            print(f"Created PublishedFile: {result}")

      def create_version_data(self):
                  """버전 데이터를 생성"""

                  version_data =  {
                        'project': {'type': 'Project', 'id': self.project['id']},
                        'code': self.pub_dict['pub_files']['pub_maya'],
                        'entity': {'type': self.parsed_data['entity_type'], 'id': self.entity['id']},
                        'published_files': [{'type': 'PublishedFile', 'id': pub_id} for pub_id in self.published_files],
                        'sg_task': {'type': 'Task', 'id': self.task['id']}
                  }
                  return version_data

      def create_version(self,version_data):
            """퍼블리시된 파일과 연결된 버전 생성"""
            version_result = self.sg.create("Version", version_data)
            self.version_id = version_result['id']
            print(f"Created Version: {version_result}")
            self.upload_version(self.pub_dict['pub_files']['Confirm_mov'], "sg_uploaded_movie")

      def upload_version(self, file_path, field_name):
            """ShotGrid에 파일을 업로드하고, 업로드된 파일의 ID를 반환"""
            if not os.path.exists(file_path):
                  print(f"Error: {file_path} 없음")
                  return None
            uploaded_file_id = self.sg.upload("Version", self.version_id, file_path, field_name)
            print(f"Uploading file to ShotGrid: {file_path}")
            if uploaded_file_id:
                  print(f"파일 업로드 완료: {uploaded_file_id}")
            return uploaded_file_id
