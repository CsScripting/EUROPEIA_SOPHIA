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
    from src.core.event_processor_europeia import edit_linha_horario
    import config
    from config import suffix
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de que o script está na raiz do projeto.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"edit_linha_horario_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
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
ANO_LECTIVO = 2025  # Definir o ano letivo aqui para a FUNÇÂO DE EDITAR LINHA DE HORÁRIO

# Obter o prefixo correto para o nome do arquivo
FILE_PREFIX = INSTITUTION_TO_PREFIX.get(config.INSTITUTION, config.INSTITUTION)

# --- Setup Output Directories ---
DATA_PROCESS_DIR = "DATA_PROCESS"
INSTITUTION_DIR = os.path.join(DATA_PROCESS_DIR, FILE_PREFIX)

# Diretórios de entrada/saída
VALIDATION_DATA_SOPHIA_DIR = os.path.join(INSTITUTION_DIR, "VALIDATION_DATA_SOPHIA")
UPDATED_DIR = os.path.join(INSTITUTION_DIR, "UPDATED")  # Nova pasta para arquivos atualizados

# Criar todas as pastas necessárias
os.makedirs(DATA_PROCESS_DIR, exist_ok=True)
os.makedirs(INSTITUTION_DIR, exist_ok=True)
os.makedirs(VALIDATION_DATA_SOPHIA_DIR, exist_ok=True)
os.makedirs(UPDATED_DIR, exist_ok=True)  # Criar a pasta UPDATED se não existir

# Nome do arquivo de entrada
NAME_FILE_SCHEDULES_SHOPIA = f"NHORARIOS_FINAL_MAPPING_{FILE_PREFIX}_{ano_semestre}.xlsx"

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
    Carrega os ficheiros de dados necessários da pasta VALIDATION_DATA_SOPHIA.
    """
    
    df_horarios_shopia = pd.read_excel(os.path.join(VALIDATION_DATA_SOPHIA_DIR, NAME_FILE_SCHEDULES_SHOPIA), sheet_name="NHORARIOS")
    logger.info(f"DataFrame de horários da SHOPIA carregado com sucesso ({len(df_horarios_shopia)} linhas).")
    
    return df_horarios_shopia


def main():
    """
    Função principal para EDITAR linha de Horario.
    """
    logger.notice("--- INÍCIO DO PROCESSO DE ATUALIZAÇÃO DE LINHAS DE HORÁRIO NA SHOPIA ---")

    # 1. Inicializar cliente SOAP
    client = initialize_soap_client()
    if not client:
        logger.error("A execução não pode continuar sem um cliente SOAP válido. A terminar.")
        return

    # 2. Carregar os dados
    df_horarios_shopia = load_dataframes()
    
    # 3. Chamar a função para editar as linhas de horário
    df_horarios_atualizado = edit_linha_horario(client, logger, df_horarios_shopia, ano_lectivo=ANO_LECTIVO)

    # 4. Guardar o DataFrame com as respostas da atualização
    output_filename = f"UPDATED_NHORARIOS_FINAL_{FILE_PREFIX}_{ano_semestre}.xlsx"
    output_filepath = os.path.join(UPDATED_DIR, output_filename)  # Usar a pasta UPDATED
    df_horarios_atualizado.to_excel(output_filepath, index=False, sheet_name="UpdatedHorarios", freeze_panes=(1,0))
    logger.info(f"Processo concluído. Ficheiro com resultados da atualização guardado em: {output_filepath}")


    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()