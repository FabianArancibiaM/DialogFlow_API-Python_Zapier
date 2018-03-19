import urllib
import json
import os
import requests
from flask import Flask
from flask import request
from flask import make_response



app2 = Flask(__name__)

#aqui se realiza la comunicacion utilisando JSON(El request y el Response)
@app2.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print()
    return r


# Aqui se toman los datos de JSON que seria la informacion solicitada al cliente
# se obtiene el numero(podria ser el telefono) el cual se usa para realizar las consultas a la base
# Al final se retorna el followupEvent para que el dialogFlow guarde los parametros buscados en la base de datos

def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    area = parameters.get("area")


    if area == 'FormEspecialista':
        var = agendarEspecialista(parameters,req)
        return var
    elif area == 'FormCuenta':
        var = estadoCuenta(parameters,req)
        return var

def agendarEspecialista(parameters,req):
    accion = req.get("result").get("action")

    nombre = parameters.get("nombre")
    apellido = parameters.get("apellido")
    telefono = parameters.get("telefono")
    correo = parameters.get("correo")
    area = parameters.get("area")
    nombreEvento = ""

    if accion == "ingresoCorreo":
        r = redirecMail(nombre, apellido, telefono, correo)
        return r
    elif accion == "ingresoDatos":
        nombreEvento = 'numeroCelular'
    elif accion == "ingresoCelular":
        if len(str(telefono)) == 9:
            nombreEvento = 'correo'
        else:
            nombreEvento = 'numeroCelular'

    print("Response:-> " + nombreEvento)
    return {
        "followupEvent": {
            "name": nombreEvento,
            "data": {
                'nombre': nombre,
                'apellido': apellido,
                'telefono': telefono,
                'correo': correo,
                'area': area
            }
        },
        # "speech": speech,
        # "displayText": speech,
        # "data": {},
        # "contextOut": [contexto],
        "source": "primerApp"
    }

def redirecMail(nombre,apellido,telefono,correo):
    url = 'https://hooks.zapier.com/xxxxx/xxxxx/xxxxxx/xxxxx/xxxxx/'
    data = {
        'nombre': nombre,
        'apellido': apellido,
        'telefono': telefono,
        'correo': correo
    }

    response = requests.post(
        url, data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    print(response.content)
    print(vars(response))
    return response.content

def estadoCuenta(parameters,req):
    accion = req.get("result").get("action")

    #loginCliente / cargandDatos /pagoCheque /pagoTarjetaCredito
    nombreEvento=""
    if accion == "datosCliente":
        var = infoCuentaCliente(parameters)
        return var
    elif accion == "pagoCheque":
        var = pagoChequeCuentaCliente(parameters)
        return var
    elif accion == "pagoTarjetaCredito":
        var = pagoTarjetaCreditoCuentaCliente(parameters)
        return var

def pagoTarjetaCreditoCuentaCliente(parameters):
    nombre = parameters.get("nombre")
    direccion = parameters.get("direccion")
    numTarjeta = parameters.get("numTarjeta")
    fechaExpiracion = parameters.get("fechaExpiracion")
    codigoSeguridad = parameters.get("codigoSeguridad")
    area = parameters.get("area")
    idCliente = parameters.get("idCliente")

    return {
        "followupEvent": {
            "name": 'pagoCorrecto'
        },
        "source": "primerApp"
    }

def pagoChequeCuentaCliente(parameters):
    area = parameters.get("area")
    nombre = parameters.get("nombre")
    direccion = parameters.get("direccion")
    numTarjeta = parameters.get("numTarjeta")
    rountNum = parameters.get("rountNum")
    idCliente = parameters.get("idCliente")

    return {
        "followupEvent": {
            "name": 'pagoCorrecto'
        },
        "source": "primerApp"
    }

def infoCuentaCliente(parameters):
    numCta = parameters.get("numCta")
    clave = parameters.get("pass")
    area = parameters.get("area")
    deuda = 0
    #idCliente = buscarIdCliente(numCta, clave)
    if clave == '123' and numCta == '123':
        idCliente = 1
    else:
        idCliente = None

    if idCliente == None:
        nombreEvento = 'errorLogin'
    else:
        #deuda = buscarDeuda(idCliente)
        deuda = 200000
        nombreEvento = 'cargandDatos'
    return {
        "followupEvent": {
            "name": nombreEvento,
            "data": {
                'area': area,
                'idCliente': idCliente,
                'deuda': deuda
            }
        },
        "source": "primerApp"
    }

# Iniciador del programa
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" %(port))

    app2.run(debug=True, port=port, host='0.0.0.0')
