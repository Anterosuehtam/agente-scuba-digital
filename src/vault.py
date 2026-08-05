import oci
from oci.secrets import SecretsClient
import base64
import os

def resgatar_segredo(secret_ocid):
    try:
        # Carrega a configuração padrão do arquivo ~/.oci/config
        config = oci.config.from_file()
        
        # Inicializa o cliente de segredos usando a classe correta do SDK
        secrets_client = SecretsClient(config)
        
        # Busca o conteúdo codificado do segredo
        secret_response = secrets_client.get_secret_bundle(secret_ocid)
        
        # Decodifica o segredo de Base64 para texto legível
        base64_secret_content = secret_response.data.secret_bundle_content.content
        secret_content = base64.b64decode(base64_secret_content).decode('utf-8')
        
        return secret_content
    except Exception as e:
        raise e