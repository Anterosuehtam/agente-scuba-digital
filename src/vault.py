import oci
import base64
import os

def resgatar_segredo(secret_ocid):
    """
    Conecta no OCI Vault e resgata o valor em texto plano do segredo.
    """
    try:
        # Carrega as credenciais locais da máquina para autenticar na Oracle
        config = oci.config.from_file()
        
        # Inicializa o cliente do cofre
        secret_client = oci.secrets.SecretsClient(config)
        
        # Solicita o pacote do segredo usando o OCID
        print("Buscando segredo no cofre...")
        response = secret_client.get_secret_bundle(secret_ocid)
        
        # O cofre devolve o dado criptografado em Base64, então decodificamos:
        conteudo_base64 = response.data.secret_bundle_content.content
        segredo_texto_plano = base64.b64decode(conteudo_base64).decode('utf-8')
        
        return segredo_texto_plano
        
    except Exception as e:
        print(f"❌ Erro ao acessar o cofre: {e}")
        return None