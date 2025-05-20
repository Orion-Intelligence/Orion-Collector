import os

LANGUAGE_MODEL_PATH = "https://drive.usercontent.google.com/download?id=1S20Mr4S0uaIr-HAMtFpeZ_eaQEIOd8x2&export=download&authuser=0&confirm=t&uuid=f267de8b-6613-482b-b207-8e407b81ff3d&at=ALoNOgnOI36I_sU3TLvccOwQrYCC%3A1746775757150"

class RAW_PATH_CONSTANTS:
  MICROSERVER = "http://trusted-micros-api:8010"
  HREF_TIMEOUT = 345600
  LOG_DIRECTORY = os.path.join(os.getcwd(), 'logs')
  SESSION_PATH = "session_data"
