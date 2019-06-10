from requests import Response

class vManageError(Exception):
    pass
class UnhandledResponseError(vManageError):
    def __init__(self,message:str,response:Response):
        super().__init__(message)
        self.response = response

class APIError:
    TYPE_FIELD = "type"
    MESSAGE_FIELD = "message"
    DETAILS_FIELD = "details"
    CODE_FIELD = "code"
    def __init__(self,err_type:str,message:str,details:str,code:str):
        self.type = err_type
        self.message = message
        self.details = details
        self.code = code
    @staticmethod
    def from_dict(document:dict):
        err_type = document.get(APIError.TYPE_FIELD)
        message = document.get(APIError.MESSAGE_FIELD)
        details = document.get(APIError.DETAILS_FIELD)
        code = document.get(APIError.CODE_FIELD)
        return APIError(err_type,message,details,code)

class CodedAPIError(vManageError):
    def __init__(self,message:str,response:Response,error:APIError):
        super().__init__(message)
        self.response = response
        self.error = error