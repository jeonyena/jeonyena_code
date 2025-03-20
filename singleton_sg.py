from shotgun_api3 import Shotgun

class Singleton_SG:

    _instance  = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):

        shotgun_url = "https://5thacademy.shotgrid.autodesk.com"
        api_key = "uojqn9zbben@cafyjbggjVssm"
        shotgun_script = "batzmaru_key"

        self.sg = Shotgun(shotgun_url, shotgun_script, api_key)
        

