from jwt import encode, decode

def create_token(data : dict):
    token: str = encode(payload = data, key= "mi_clave", algorithm="HS256")
        #"payLoad" es el contenido que se dara para convertirlo en el token
    return token

def validate_token(token : str):
    data : dict = decode(token, key="mi_clave" , algorithms=['HS256'])
    return data;