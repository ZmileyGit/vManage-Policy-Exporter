from abc import ABC,abstractstaticmethod,abstractmethod

class Server:
    HOST_FIELD = "host"
    PORT_FIELD = "port"
    PROTOCOL_FIELD = "proto"
    SECURE_FIELD = "secure"
    DEFAULT_PORT = 443
    DEFAULT_PROTOCOL = "https"
    DEFAULT_SECURE = True
    def __init__(self,host:str,port:int=DEFAULT_PORT,protocol:str=DEFAULT_PROTOCOL,secure:bool=DEFAULT_SECURE):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.secure = secure
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
        secure = document.get(Server.SECURE_FIELD,Server.DEFAULT_SECURE)
        if host and port and protocol:
            return Server(host,port=port,protocol=protocol,secure=secure)
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
    def __hash__(self):
        return hash(self.id)
    def __eq__(self,other):
        return isinstance(other,Model) and self.id == other.id
    @abstractmethod
    def to_dict(self):
        pass

class ModelFactory(ABC):
    @abstractmethod
    def from_dict(self,document:dict):
        pass