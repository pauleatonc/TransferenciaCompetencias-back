from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import requests
import jwt

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64decode
from applications.users.api.v1.serializers import CustomTokenObtainPairSerializer, UserSerializer

def get_keycloak_config():
    return settings.KEYCLOAK_CONFIG
    
def exchange_code_for_token(code, code_verifier):
    # Obtener las configuraciones de Keycloak según el entorno
    keycloak_config = get_keycloak_config()
    print("code en exchange_code_for_token", code)

    payload = {
        'grant_type': 'authorization_code',
        'client_id': keycloak_config['resource'],
        'redirect_uri': keycloak_config['redirect_uri'],
        'code': code,       
        'code_verifier': code_verifier,
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    keycloak_token_url = keycloak_config['keycloak_token_url']
    response = requests.post(keycloak_token_url, data=payload, headers=headers)

    if response.status_code == 200:
        token_info = response.json()
        print("token info =", response.json())
        return token_info  # Devuelve todo el objeto JSON, incluido el refresh_token
        
    else:
        # Log para depuración
        print(f'Error intercambiando el código por token: {response.status_code}, {response.text}')
        try:
            error_details = response.json()
            print(f'Detalles del error: {error_details}')
        except Exception as e:
            print(f'No se pudo parsear la respuesta de error: {e}')
        return None


def get_keycloak_public_key():
    keycloak_config = get_keycloak_config()
    certs_url = f"{keycloak_config['auth-server-url']}/realms/{keycloak_config['realm']}/protocol/openid-connect/certs"
    response = requests.get(certs_url)
    if response.status_code == 200:
        public_key_info = response.json()['keys'][0]
        public_cert_base64 = public_key_info['x5c'][0]
        public_key_pem = f"-----BEGIN CERTIFICATE-----\n{public_cert_base64}\n-----END CERTIFICATE-----"
        return public_key_pem
    else:
        raise Exception("No se pudo obtener la clave pública de Keycloak")

def verify_user(token):
    public_key_pem = get_keycloak_public_key()  # Asegura que esta función retorne la clave pública en el formato correcto.

    print("Public key pem: ", public_key_pem)
    print("Token: ", token)

    # Verificar el token con pyjwt
    try:
        token_info = jwt.decode(token, options={"verify_signature": False})
        print(token_info)

        rut_base = token_info['rut_numero']
        rut_dv = token_info['rut_dv']
        rut_formatted = f"{rut_base}-{rut_dv}"
        
        User = get_user_model()

        # Obtiene el usuario
        user = User.objects.get(
            rut=rut_formatted,
        )
        user_serializer = UserSerializer(user)
        print(f"Usuario encontrado: {user.rut}")

        return user_serializer.data

    except ObjectDoesNotExist:
        print(f"Usuario no encontrado con RUT: {rut_formatted}")
        return None
    except KeyError as e:
        print(f"Información clave faltante en el token: {e}")
        return None
    except Exception as e:
        print(f"Error al verificar el usuario: {e}")
        return None


def decrypt(encrypted_state, key):
    # Decode the base64 data
    encrypted = b64decode(encrypted_state)
    iv = encrypted[:12]  # Extract the first 12 bytes as the IV.
    encrypted_data = encrypted[12:]  # The rest is the encrypted data.

    # Convert key from Base64 to bytes, if it's in Base64 format
    key_bytes = b64decode(key)

    decryptor = Cipher(
        algorithms.AES(key_bytes),
        modes.GCM(iv),
        backend=default_backend()
    ).decryptor()

    return decryptor.update(encrypted_data) + decryptor.finalize()