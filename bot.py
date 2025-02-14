import telebot
import requests
import os
import uuid
from pathlib import Path

Token = '7684550352:AAHcGOi4VM6kqqxfxpUpcYpLIxSkquuX1OY'
AdminID = '1425847313'
AdminID2 = '6379656679'
apiurl = 'https://meta-api-production-3abd.up.railway.app/api/Wallet/UpdateBalance'
ApiUrlToWithdraw = 'https://meta-api-production-3abd.up.railway.app/api/Wallet/WithdrawBalance'
ApiurlGetBalance = 'https://meta-api-production-3abd.up.railway.app/api/Wallet/GetBalance/'
ApiUrlGetVr ='https://meta-api-production-3abd.up.railway.app/api/UserPlans/GetVrsToUser/'
ApiUrlPostVr = 'https://meta-api-production-3abd.up.railway.app/api/UserPlans/AdminPlanToUser'   
ApiUrlDeleteVr = 'https://meta-api-production-3abd.up.railway.app/api/UserPlans/DeleteUserPlans'
bot = telebot.TeleBot(Token)
data_storage = {}
directory = os.path.abspath('./imagenes')
channel_id = -1002226124389

# Asegúrate de que el directorio de imágenes exista
if not os.path.exists(directory):
    os.makedirs(directory)

@bot.message_handler(commands=['actualizarsaldo'])
def iniciarActualizarSaldo(message):
    print(f"Comando recibido de: {message.from_user.id}") 
    if str(message.from_user.id) == AdminID or str(message.from_user.id) == AdminID2:
        bot.reply_to(message, "Por favor, envía el usuario que desea actualizar su saldo (# de teléfono o correo).")
        bot.register_next_step_handler(message, recibirusuario)
    else:
        bot.reply_to(message, "No tienes permisos para realizar esta acción.")

def recibirusuario(message):
    user_id = message.text
    data_storage['user_id'] = user_id
    bot.reply_to(message, "Ahora, envía el monto de la recarga.")
    bot.register_next_step_handler(message, recibirmonto)

def recibirmonto(message):
    try:
        monto = float(message.text)
        data_storage['monto'] = monto
        bot.reply_to(message, "Finalmente, envía la moneda (ej. Nequi, TRX, USDT_TRC20, PayPal).")
        bot.register_next_step_handler(message, recibirmoneda)
    except ValueError:
        bot.reply_to(message, "Por favor, ingrese un monto válido.")
        bot.register_next_step_handler(message, recibirmonto)

def recibirmoneda(message):
    moneda = message.text
    data_storage['moneda'] = moneda
    bot.reply_to(message, "Enviando datos a la API...")

    payload = {
        'Email': data_storage['user_id'],
        'Balance': data_storage['monto'],
        'Token': data_storage['moneda']
    }
    response = requests.post(apiurl, json=payload)

    if response.status_code == 200:
        bot.reply_to(message, "Saldo actualizado con éxito.")
    else:
        bot.reply_to(message, "Error al actualizar el saldo.".format(response.text))

    data_storage.clear()

@bot.message_handler(commands=['listarimagenes'])
def listar_imagenes(message):
    # Busca imágenes en formatos JPG, PNG y WEBP
    image_files = list(Path(directory).glob('*.jpg')) + list(Path(directory).glob('*.png')) + list(Path(directory).glob('*.webp'))

    print(f"Archivos encontrados: {image_files}")  # Mensaje de depuración
    if not image_files:
        bot.reply_to(message, "No hay imágenes guardadas.")
    else:
        for img in image_files:
            with open(img, 'rb') as image_file:
                bot.send_photo(message.chat.id, image_file, caption=f"Imagen ID: {img.stem}")

@bot.message_handler(commands=['eliminarimagenes'])
def iniciar_eliminar_imagen(message):
    bot.reply_to(message, "Por favor, envía el ID de la imagen que deseas eliminar.")
    bot.register_next_step_handler(message, eliminar_imagen)

def eliminar_imagen(message):
    image_id = message.text.strip()
    image_path = Path(directory) / f"{image_id}.jpg"

    if image_path.exists():
        os.remove(image_path)
        bot.reply_to(message, f"Imagen con ID {image_id} eliminada exitosamente.")
    else:
        bot.reply_to(message, "No se encontró ninguna imagen con ese ID.")

@bot.message_handler(content_types=['photo'])
def guardar_imagen(message):
    print("Recibí una imagen.")
    try:
        # Aquí no hay filtro, por lo tanto, guarda todas las imágenes sin importar quién las envíe
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_id = str(uuid.uuid4())  # ID único para cada imagen
        image_extension = file_info.file_path.split('.')[-1]
        image_path = os.path.join(directory, f"{image_id}.{image_extension}")
        os.makedirs(directory, exist_ok=True)

        # Guardar la imagen en el directorio
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)

        bot.reply_to(message, f"Imagen guardada en {image_path}")
    except Exception as e:
        bot.reply_to(message, f"Error al guardar la imagen: {e}")

@bot.message_handler(commands=['enviarimagen'])
def enviar_imagen(message):
    # Esta es la imagen que el bot enviará
    image_url = "http://example.com/your_image.jpg"  # URL de la imagen que deseas enviar

    # Enviar la imagen al chat (o canal)
    sent_message = bot.send_photo(AdminID, image_url)

    # Ahora, para guardar esa imagen enviada
    try:
        # Obtener el ID de la imagen enviada
        file_info = bot.get_file(sent_message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Generar un ID único para la imagen
        image_id = str(uuid.uuid4())
        image_extension = file_info.file_path.split('.')[-1]
        image_path = os.path.join(directory, f"{image_id}.{image_extension}")
        os.makedirs(directory, exist_ok=True)

        # Guardar la imagen en el directorio
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)

        bot.reply_to(message, f"Imagen enviada y guardada en {image_path}")
    except Exception as e:
        bot.reply_to(message, f"Error al guardar la imagen: {e}")
@bot.message_handler(commands=['retirarsaldo'])
def IniciarRetiroSaldo(message):
    if str(message.from_user.id) == AdminID or str(message.from_user.id) == AdminID2:
        bot.reply_to(message, "Por favor, envía el usuario que desea actualizar su saldo (# de teléfono o correo).")
        bot.register_next_step_handler(message, RecibirUsuariodeRetiroSaldo)
    else:
        bot.reply_to(message, "Usted no es el administrador del bot, no puedes usar este comando.")
        
def RecibirUsuariodeRetiroSaldo(message):
    data_storage['user_identifier'] = message.text.strip()
    bot.reply_to(message, "Ahora por favor envie el monto a retirar")
    bot.register_next_step_handler(message, RecibirMontoARetirar)
    
def RecibirMontoARetirar(message):
    try:
        monto = float(message.text)
        if monto <= 0:
            raise ValueError("El monto a retirar debe ser mayor a cero")
        data_storage['monto_a_retirar'] = monto
        bot.reply_to(message, "Enviando datos a la API...")
        EnviarDatosARetirar(message)
    except ValueError:
        bot.reply_to(message, "Por favor entre un monto válido")     
        bot.register_next_step_handler(message, RecibirMontoARetirar)   
        
def EnviarDatosARetirar(message):
    payload = {
        'username': data_storage['user_identifier'],
        'withdraw': data_storage['monto_a_retirar']
    }
    try:
        response = requests.patch(ApiUrlToWithdraw , json=payload)
        response_data = response.json()
        if response.status_code == 200:
            bot.reply_to(message , response_data.get('message' , 'Saldo retirado con éxito'))
        else:
            bot.reply_to(message , response_data.get('message' , 'Error al retirar el saldo'))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message , "Error al retirar el saldo")
@bot.message_handler(commands=['obtenerbalance'])
def IniciarProcesoObtenerBalance(message):
    if str(message.from_user.id)== AdminID or str(message.from_user.id) == AdminID2:
        bot.reply_to(message, "Por favor, envía el usuario que desea obtener su balance (# de teléfono o correo).")
        bot.register_next_step_handler(message, RecibirUsuarioObtenerBalance)
    else:
        bot.reply_to(message, "Usted no es el administrador del bot, no puedes usar este comando.")
        
def RecibirUsuarioObtenerBalance(message):
    data_storage['user_identifier'] = message.text.strip()
    bot.reply_to(message, "Espere un momento...")
    RecibirBalance(message)
def RecibirBalance(message):
    try:
        response = requests.get(ApiurlGetBalance+data_storage['user_identifier'])
        if response.status_code == 200:
            balance = response.json();
            bot.reply_to(message , f"El saldo de ese usuario es {balance}")
        else:
            response_data = response.json()
            bot.reply_to(message , response_data.get('message' , 'Error al obtener el saldo'))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message , "Error al obtener el saldo")
@bot.message_handler(commands=['obtenergafasvr'])
def IniciarProcesoObtenerGafaVR(message):
    if str(message.from_user.id)== AdminID or str(message.from_user.id) == AdminID2:
        bot.reply_to(message, "Por favor, envía el usuario que desea obtener su balance (# de teléfono o correo).")
        bot.register_next_step_handler(message, RecibirUsuarioObtenerGafaVR)
    else:
        bot.reply_to(message, "Usted no es el administrador del bot, no puedes usar este comando.")
        
def RecibirUsuarioObtenerGafaVR(message):
    data_storage['user_identifier'] = message.text.strip()
    bot.reply_to(message, "Espere un momento...")
    RecibirGafaVR(message)
def RecibirGafaVR(message):
    try:
        response = requests.get(ApiUrlGetVr+data_storage['user_identifier'])
        if response.status_code == 200:
            gafas = response.json()
            bot.reply_to(message , f"Los gafas de ese usuario son {gafas}")
        else:
            response_data = response.json()
            bot.reply_to(message , response_data.get('message' , 'Error al obtener los gafas'))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message , "Error al obtener los gafas")
@bot.message_handler(commands=['comprargafavr'])
def IniciarProcesoComprarGafaVR(message):
    if str(message.from_user.id)== AdminID or str(message.from_user.id) == AdminID2:
        bot.reply_to(message, "Por favor, envía el usuario que desea comprar gafas (# de teléfono o correo).")
        bot.register_next_step_handler(message, RecibirUsuarioComprarGafaVR)
    else:
        bot.reply_to(message, "Usted no es el administrador del bot, no puedes usar este comando.")
        
def RecibirUsuarioComprarGafaVR(message):
    data_storage['user_identifier'] = message.text.strip()
    bot.reply_to(message, "Ahora envie el id de la Vr ,por ejemplo 1 es Vr1 ,2 es vr2 etc")
    bot.register_next_step_handler(message, RecibirIdVrComprarGafaVR)
def RecibirIdVrComprarGafaVR(message):
    id = int(message.text)
    data_storage['id'] = id
    bot.reply_to(message, "Enviando datos a la API...")
    EnviarDatosAComprarGafaVR(message)
def EnviarDatosAComprarGafaVR(message):
    payload = {
        'username': data_storage['user_identifier'],
        'vr': data_storage['id']
    }
    try:
        response = requests.post(ApiUrlPostVr , json=payload)
        if response.status_code == 200:
            data = response.json()
            bot.reply_to(message , data.get('message' , 'Gafa comprada con éxito'))
        else:
            response_data = response.json()
            bot.reply_to(message , response_data.get('message' , 'Error al comprar la gafa'))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message , "Error al comprar la gafa")
@bot.message_handler(commands=['borrargafavr'])	
def IniciarProcesoBorrarGafaVR(message):
    if str(message.from_user.id)== AdminID or str(message.from_user.id) == AdminID2:
        bot.reply_to(message, "Por favor, envía el usuario que desea borrar su balance (# de teléfono o correo).")
        bot.register_next_step_handler(message, RecibirUsuarioBorrarGafaVR)
    else:
        bot.reply_to(message, "Usted no es el administrador del bot, no puedes usar este comando.")
        
def RecibirUsuarioBorrarGafaVR(message):
    data_storage['user_identifier'] = message.text.strip()
    bot.reply_to(message, "Ahora envie el id de la Vr ,por ejemplo 1 es Vr1 ,2 es vr2 etc")
    bot.register_next_step_handler(message, RecibirIdVrBorrarGafaVR)
def RecibirIdVrBorrarGafaVR(message):
    id = int(message.text)
    data_storage['id'] = id
    bot.reply_to(message, "Por favor ingrese la cantidad de gafas que desea borrar")
    bot.register_next_step_handler(message, RecibirCantidadBorrarGafaVR)
def RecibirCantidadBorrarGafaVR(message):
    cantidad = int(message.text)
    data_storage['cantidad'] = cantidad
    bot.reply_to(message, "Enviando datos a la API...")
    EnviarDatosABorrarGafaVR(message)
def EnviarDatosABorrarGafaVR(message):
    payload = {
        'username': data_storage['user_identifier'],
        'vr': data_storage['id'],
        'quantity': data_storage['cantidad']
    }
    try:
        response = requests.delete(ApiUrlDeleteVr , json=payload)
        if response.status_code == 200:
            data = response.json()
            bot.reply_to(message , data.get('message' , 'Gafa borrada con éxito'))
        else:
            response_data = response.json()
            bot.reply_to(message , response_data.get('message' , 'Error al borrar la gafa'))
    except requests.exceptions.RequestException as e:
        bot.reply_to(message , "Error al borrar la gafa")
try:
    print("Bot está escuchando...")  # Mensaje de depuración
    bot.polling(none_stop=True, interval=0)  # Usando long polling
except Exception as e:
    print(f"Error en el bot: {e}")



