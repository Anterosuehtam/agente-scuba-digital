import boto3
import os
from vault import resgatar_segredo

NAMESPACE = "grtjk2qyrhtu"
REGIAO = "sa-saopaulo-1"
BUCKET_NAME = "snorkel-documentos-scuba"

# OCIDs dos Segredos (Identificadores, não são senhas)
OCID_ACCESS_KEY = "ocid1.vaultsecret.oc1.sa-saopaulo-1.amaaaaaapd6tuwyaxvcnhujaarodszoylpqb2rofqzsrodzxapgmo5dz3g5q"
OCID_SECRET_KEY = "ocid1.vaultsecret.oc1.sa-saopaulo-1.amaaaaaapd6tuwyaqz2rhml645vvuyeftysrwbzcxl76rqurzfnkibpwkdbq"

def baixar_documentos_da_nuvem():
    print("🔐 Solicitando chaves de acesso ao OCI Vault...")
    access_key = resgatar_segredo(OCID_ACCESS_KEY)
    secret_key = resgatar_segredo(OCID_SECRET_KEY)

    if not access_key or not secret_key:
        print("❌ Falha ao resgatar chaves do cofre. Abortando sincronização.")
        return

    print("☁️ Conectando ao Object Storage da OCI...")
    
    # Inicializa o cliente S3 injetando as chaves que vieram do cofre
    s3 = boto3.client(
        's3',
        region_name=REGIAO,
        endpoint_url=f"https://{NAMESPACE}.compat.objectstorage.{REGIAO}.oraclecloud.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    # Garante que a pasta local data/ existe
    pasta_destino = "data"
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        
    try:
        # Lista todos os arquivos que estão no Bucket
        objetos = s3.list_objects(Bucket=BUCKET_NAME)
        
        if 'Contents' in objetos:
            for obj in objetos['Contents']:
                nome_arquivo = obj['Key']
                caminho_local = os.path.join(pasta_destino, nome_arquivo)
                
                print(f"Baixando: {nome_arquivo}...")
                s3.download_file(BUCKET_NAME, nome_arquivo, caminho_local)
                
            print("✅ Sincronização concluída com sucesso!")
        else:
            print("O bucket está vazio.")
            
    except Exception as e:
        print(f"❌ Erro ao conectar no Storage: {e}")

# Se rodar este arquivo direto, ele executa a função
if __name__ == "__main__":
    baixar_documentos_da_nuvem()