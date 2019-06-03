from abc import ABC,abstractstaticmethod,abstractmethod

class Server:
    HOST_FIELD = "host"
    PORT_FIELD = "port"
    PROTOCOL_FIELD = "proto"
    DEFAULT_PORT = 443
    DEFAULT_PROTOCOL = "https"
    def __init__(self,host:str,port:int=DEFAULT_PORT,protocol:str=DEFAULT_PROTOCOL):
        self.host = host
        self.port = port
        self.protocol = protocol
    @property
    def uri(self):
        return "{protocol}://{host}:{port}".format(protocol=self.protocol,host=self.host,port=self.port)
    def url(self,resource:str):
        return "{root}{url}".format(root=self.uri,url=resource)
    @staticmethod
    def from_dict(document:dict):
        host = document.get(Server.HOST_FIELD)
        port = int(document.get(Server.PORT_FIELD,Server.DEFAULT_PORT))
        protocol = document.get(Server.PROTOCOL_FIELD,Server.DEFAULT_PROTOCOL)
        if host and port and protocol:
            return Server(host,port=port,protocol=protocol)
        return None

class HelperModel:
    def __init__(self,definition:dict):
        self.definition = definition
    def __repr__(self):
        return "{klass}: {vars}".format(klass=type(self),vars=vars(self))

class Model(ABC):
    def __init__(self,mid:str):
        self.id = mid
    def __repr__(self):
        return "{0} : {1}".format(type(self),vars(self))
    @abstractmethod
    def to_dict(self):
        pass

class ModelFactory(ABC):
    @abstractmethod
    def from_dict(self,document:dict):
        pass