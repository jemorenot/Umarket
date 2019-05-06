from main import *
from . import modules
import re

@modules.route('/register', methods=['POST'])
def addUser():
    try:
        _json= request.get_json(force=True)
        _strcorreo = _json['stremail']
        #   _strusuario = _json['struser']
        _id_rol=_json['id_rol']
        _strcontrasena = _json['strpassword']
        _strnombres = _json['strname']
        _strapellidos = _json['strsurname']
        #Por defecto se registra con el id_estatus

        caracteres = string.ascii_uppercase + string.ascii_lowercase + string.digits
        longitud = 8  # La longitud que queremos
        _token = ''.join(random.choice(caracteres) for _ in range(longitud))

        # validate the received values
        if  request.method == 'POST':   
            if not _strcorreo: 
                resp = jsonify({"status":'error', "msj":"Debe ingresar un correo"})
                return  sendResponse(resp)  
            if not re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',_strcorreo.lower()):
                resp = jsonify({"status":'error', "msj":"Debe ingresar un correo válido"})
                return  sendResponse(resp)  
            if not _strcontrasena:
                resp = jsonify({"status":'error', "msj":"Debe ingresar una contraseña"})
                return sendResponse(resp)           
            if not _strnombres:        
                resp = jsonify({"status":'error', "msj":"Debe ingresar un apellido"})
                return sendResponse(resp)
            if not _strapellidos:        
                resp = jsonify({"status":'error', "msj":"Debe ingresar un nombre"})
                return sendResponse(resp)   
            if not _id_rol:
                resp = jsonify({"status":'error', "msj":"Debe ingresar un rol"})
                return sendResponse(resp)                            
            _hashed_password = hashlib.md5(_strcontrasena.encode())
            #existe_user=user_validate(_strusuario)
            #if not existe_user:                                
            existe_email=email_validate(_strcorreo)
            if not existe_email:
                # save edits
                sql = "INSERT INTO dt_usuarios(strcorreo, strcontrasena, id_rol, strnombres, strapellidos, token) VALUES(%s, %s, %s, %s, %s, %s)"
                data = (_strcorreo, _hashed_password.hexdigest(),_id_rol,_strnombres, _strapellidos, _token)
                nombapell= _strnombres + " " + _strapellidos
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                resp = jsonify({"status":'success', "msj":"El usuario fue registrado","token":_token})                                    
                resp.status_code = 200                                    
                send_mail(_token,_strcorreo,nombapell)
                return sendResponse(resp)
            else:
                resp = jsonify({"status":'error', "msj":"El usuario ya se encuentra registrado"})
                return  sendResponse(resp)                                                         
        else:
            resp = jsonify({"status":'error', "msj":"Debe ingresar un usuario"})
            return sendResponse(resp)
    except Exception as e:
        print(e)

@modules.route('/users') 
def users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM dt_usuarios ")
        rows = cursor.fetchall()
        if rows:
            resp = jsonify(rows)            
            resp.status_code = 200
            return sendResponse(resp)
        elif not rows:
            resp = jsonify({"status":'error', "msj":"No se encuentran usuarios registrados"})
            return sendResponse(resp)      
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
        

@modules.route('/user', methods=['POST'])
def user():
    try:
        _json = request.json
        _id = _json['id']
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM dt_usuarios WHERE id_usuario=%s",_id)
        row = cursor.fetchone()
        resp = jsonify(row)        
        resp.status_code = 200
        return sendResponse(resp)

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@modules.route('/user_login', methods=['POST'])
def userLogin():
    try:             
        _json= request.get_json(force=True)
       # print(_json)
        _strusuario = _json['struser']
        _strcontrasena = _json['strpassword']
        if _strusuario and  request.method == 'POST':
            if _strcontrasena:
                existe_user=user_validate(_strusuario)  
                _hashed_password = hashlib.md5(_strcontrasena.encode())
                if existe_user:
                    if existe_user['tb_estatus_id']==2:
                        if (existe_user['strcontrasena']==_hashed_password.hexdigest()):
                            caracteres = string.ascii_uppercase + string.ascii_lowercase + string.digits
                            longitud = 32  # La longitud que queremos
                            _token = ''.join(random.choice(caracteres) for _ in range(longitud))
                            resp = jsonify({"status":"success", "msj":"El usuario logeado","strusuario":existe_user['strusuario'], "strnombres":existe_user['strnombres'], "strapellidos":existe_user['strapellidos'],"strcorreo":existe_user['strcorreo_electronico'],"token":_token})                                                      
                            resp.status_code = 200
                            return sendResponse(resp)
                        else:
                            resp = jsonify({"status":'warning', "msj":"La contraseña es inválida"})
                            return sendResponse(resp)                       
                    else:
                        resp = jsonify({"status": 'warning', "msj": "El usuario inactivo"})
                        return sendResponse(resp)
                else:
                    resp = jsonify({"status": 'error', "msj": "El usuario no existe"})
                    return sendResponse(resp)
            else:
                resp = jsonify({"status": 'error', "msj": "Debe ingresar una contraseña"})
                return sendResponse(resp)
        else:
            resp = jsonify({"status":"error", "msj": "Debe ingresar un usuario"})
            return sendResponse(resp)    
    except Exception as e:
        print(e)

@modules.route('/update', methods=['POST'])   
def updateUser():
    try:
        _json = request.json
        _id = _json['id_usuario']
        _strcorreo = _json['stremail']
        _strusuario = _json['struser']
        _strcontrasena = _json['strpassword']
        _strnombres = _json['strname']
        _strapellidos = _json['strsurname']
        _bt_estatus_id = _json['id_status']
        # validate the received values
        if _strcorreo and _strcontrasena and _id and request.method == 'POST':
            # do not save password as a plain text
            _hashed_password = generate_password_hash(_strcontrasena)
            # save edits
            sql = "UPDATE dt_usuarios SET strcorreo_electronico=%s,strcontrasena=%s WHERE id=%s"
            data = (_strcorreo, _hashed_password, _id)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            resp = jsonify({"status":"success","msj":"El usuario fue actualizado"})
            resp.status_code = 200
            return sendResponse(resp)
        else:
            return not_found()
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@modules.route('/delete/')
def deleteUser():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dt_usuarios WHERE id=%s", (id,))
        conn.commit()
        resp = jsonify({"status":"success","msj":"El usuario fue eliminado"})
        resp.status_code = 200
        return sendResponse(resp)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

#Funcion que valida si el usuario existe
def user_validate(strusuario):
    try:
        _strusuario=strusuario
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM dt_usuarios WHERE strusuario=%s",_strusuario)
        row = cursor.fetchone()
        return row
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
#Funcion que valida si el correo electronico existe
def email_validate(strcorreo):
    try:
        _strcorreo=strcorreo
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql="SELECT * FROM dt_usuarios WHERE strcorreo=%s"
        cursor.execute(sql,_strcorreo)
        row = cursor.fetchone()
        return row
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

@modules.route('/token',methods=['POST'])
def token():
    try:        
        _json= request.get_json(force=True)
        _token= _json['token']
        if _token and  request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sql="SELECT id,token,tb_estatus_id FROM dt_usuarios WHERE token=%s"
            cursor.execute(sql,_token)
            row = cursor.fetchone()
            if row:
                if row['tb_estatus_id']==1:
                    token=activate_user(_token)       
                    if token:
                        resp = jsonify({"status": 'success', "msj": "El token fue activado"})
                        return sendResponse(resp)
                    else:
                        resp = jsonify({"status": 'error', "msj": "El token no fue activado"})
                        return sendResponse(resp)
                else:
                    resp = jsonify({"status": 'error', "msj": "El token fue utilizado"})
                    return sendResponse(resp)
                                
            else:
                resp = jsonify({"status": 'error', "msj": "El token es inválido"})
                return sendResponse(resp)             
        else:
            resp = jsonify({"status": 'error', "msj": "Debe ingresar un token"})
            return sendResponse(resp)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

#Funcion que activa el usuario
def activate_user(token):
    try:
        _token=token
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        afectado=cursor.execute("UPDATE dt_usuarios SET tb_estatus_id=2 WHERE token=%s",_token)
        conn.commit()
        return afectado
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
