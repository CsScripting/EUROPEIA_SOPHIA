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
    from src.core.event_processor_europeia import add_teacher_code_to_horarios_shopia
    import config
    from config import suffix
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de que o script está na raiz do projeto.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"extract_schedules_update_new_2_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# --- Variáveis de Controlo ---
SOURCE_DATA_DIR = os.path.join("DATA_PROCESS")
SOURCE_DATA_DIR_SCHEDULES_BEST = os.path.join(SOURCE_DATA_DIR, "SCHEDULES_BEST")
SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE = os.path.join(SOURCE_DATA_DIR, "DATA_UPDATE")
NAME_FILE_SCHEDULES_BEST = "Valid_data_EU_2025_PRIMER.xlsx"
NAME_FILE_SCHEDULES_SHOPIA = "Valid_data_NHORARIOS_EU_2025_PRIMER.xlsx"

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
    Carrega os ficheiros de dados necessários da pasta DATA_PROCESS.
    """
    df_events_BEST = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SCHEDULES_BEST, NAME_FILE_SCHEDULES_BEST), sheet_name="MergedData_Valid")
    logger.info(f"DataFrame de eventos BEST carregado com sucesso ({len(df_events_BEST)} linhas).")
    
    df_horarios_shopia = pd.read_excel(os.path.join(SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE, NAME_FILE_SCHEDULES_SHOPIA), sheet_name="NHORARIOS")
    logger.info(f"DataFrame de horários da SHOPIA carregado com sucesso ({len(df_horarios_shopia)} linhas).")
    
    return df_events_BEST, df_horarios_shopia

def main():
    """
    Função principal para orquestrar a verificação de horários.
    """
    logger.notice("--- INÍCIO DO PROCESSO DE VERIFICAÇÃO DE HORÁRIOS NA SHOPIA ---")

    # 1. Inicializar cliente SOAP
    client = initialize_soap_client()
    if not client:
        logger.error("A execução não pode continuar sem um cliente SOAP válido. A terminar.")
        return

    # 2. Carregar os dados
    df_events_BEST, df_horarios_shopia = load_dataframes()
    
    df_events_SHOPIA_FINAL = add_teacher_code_to_horarios_shopia(df_events_BEST, df_horarios_shopia)

    # Guardar o DataFrame final em um novo ficheiro Excel
    output_file_path = os.path.join(SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE, 'df_events_SHOPIA_FINAL.xlsx')
    df_events_SHOPIA_FINAL.to_excel(output_file_path, index=False, sheet_name="NHORARIOS")
    logger.info(f"O ficheiro final foi guardado em: {output_file_path}")


    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()
