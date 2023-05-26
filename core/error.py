import pyrebase
import requests

class Error:

    def __init__(self, e: Exception):
        self.err = "Error"
        self.description = str(e)