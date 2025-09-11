import os
import pandas as pd
import logging
import datetime
import sys
from zeep import Client, Settings
from zeep.transports import Transport

# --- Adicionar o caminho da raiz do projeto ao sys.path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.utils.setup_logging import setup_colored_logging, redirect_stdout_stderr_to_log
    from src.core.event_processor_europeia import put_linha_horario_to_insert
    import config
    from config import suffix
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de que o script está na raiz do projeto.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"8.insert_new_n_linha_horario_{config.INSTITUTION}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# Mapeamento de instituição para prefixo do arquivo
INSTITUTION_TO_PREFIX = {
    'QA': 'QA',
    'Europeia': 'EU',
    'UE_IADE': 'IADE',
    'IPAM_Porto': 'IPAM_POR',
    'IPAM_Lisboa': 'IPAM_LIS'
}

# Variáveis de controle
ano_semestre = "2025_PRIMER"
ANO_LECTIVO = 2025  # Definir o ano letivo aqui para a FUNÇÃO DE INSERIR LINHA DE HORÁRIO

# Obter o prefixo correto para o nome do arquivo
FILE_PREFIX = INSTITUTION_TO_PREFIX.get(config.INSTITUTION, config.INSTITUTION)

# --- Setup Output Directories ---
DATA_PROCESS_DIR = "DATA_PROCESS"
INSTITUTION_DIR = os.path.join(DATA_PROCESS_DIR, FILE_PREFIX)

# Diretórios de entrada/saída
TO_INSERT_DIR = os.path.join(INSTITUTION_DIR, "TO_INSERT")  # Diretório onde estão os arquivos a serem inseridos

# Criar todas as pastas necessárias
os.makedirs(DATA_PROCESS_DIR, exist_ok=True)
os.makedirs(INSTITUTION_DIR, exist_ok=True)
os.makedirs(TO_INSERT_DIR, exist_ok=True)

# Nome do arquivo de entrada (deve corresponder ao arquivo gerado pelo script anterior)
NAME_FILE_TO_INSERT = f"TO_INSERT_NHORARIOS_{FILE_PREFIX}_{ano_semestre}.xlsx"

def initialize_soap_client():
    """Inicializa e retorna o cliente SOAP com as configurações necessárias."""
    try:
        settings = Settings(strict=False, xml_huge_tree=True)
        transport = Transport(timeout=300)
        client = Client(config.WSDL_URL, settings=settings, transport=transport)
        logger.info(f"Cliente SOAP inicializado para o WSDL: {config.WSDL_URL}")
        return client
    except Exception as e:
        logger.error(f"Falha ao inicializar o cliente SOAP: {e}", exc_info=True)
        return None

def load_dataframes():
    """
    Carrega os ficheiros de dados necessários da pasta TO_INSERT.
    """
    
    df_to_insert = pd.read_excel(os.path.join(TO_INSERT_DIR, NAME_FILE_TO_INSERT), sheet_name="HorariosToInsert")
    logger.info(f"DataFrame de horários a inserir carregado com sucesso ({len(df_to_insert)} linhas).")
    
    # Filtrar apenas as linhas que têm ToInsert = 1
    df_to_insert_filtered = df_to_insert[df_to_insert['ToInsert'] == 1].copy()
    logger.info(f"Após filtrar ToInsert = 1: {len(df_to_insert_filtered)} linhas para inserir.")
    
    return df_to_insert_filtered

def main():
    """
    Função principal para Inserir linha de Horario.
    """
    logger.notice("--- INÍCIO DO PROCESSO DE ATUALIZAÇÃO DE LINHAS DE HORÁRIO NA SHOPIA ---")

    # 1. Inicializar cliente SOAP
    client = initialize_soap_client()
    if not client:
        logger.error("A execução não pode continuar sem um cliente SOAP válido. A terminar.")
        return

    # 2. Carregar os dados
    df_horarios_shopia = load_dataframes()
    
    # 3. Chamar a função para inserir as linhas de horário
    df_horarios_atualizado = put_linha_horario_to_insert(client, logger, df_horarios_shopia, ano_lectivo=ANO_LECTIVO)
    df_horarios_atualizado.drop(columns=['ToInsert'], inplace=True)

    # 4. Guardar o DataFrame com as respostas da inserção
    output_filename = f"INSERTED_NHORARIOS_{FILE_PREFIX}_{ano_semestre}.xlsx"
    output_filepath = os.path.join(TO_INSERT_DIR, output_filename)
    df_horarios_atualizado.to_excel(output_filepath, index=False, sheet_name="InsertedHorarios", freeze_panes=(1,0))
    logger.info(f"Processo concluído. Ficheiro com resultados da inserção guardado em: {output_filepath}")

    logger.notice("--- FIM DO PROCESSO ---")


if __name__ == "__main__":
    main()