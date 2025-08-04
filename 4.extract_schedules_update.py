import os
import pandas as pd
import logging
import datetime
import sys
import glob

# --- Adicionar o caminho da raiz do projeto ao sys.path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.utils.setup_logging import setup_colored_logging, redirect_stdout_stderr_to_log
    from src.core.constants import OUTPUT_FILES_DIR
    from src.core.event_processor_europeia import extract_relation_teachers_best
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de que o script está na raiz do projeto.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"extract_schedules_update_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# --- Variáveis de Controlo ---
# Diretório onde os ficheiros de entrada estão localizados
SOURCE_DATA_DIR_SCHEDULES_BEST = os.path.join("DATA_PROCESS", "SCHEDULES_BEST")
NAME_FILE_SCHEDULES_BEST = "Valid_data_EU_2025_PRIMER.xlsx"


def load_dataframes():
    """
    Carrega os ficheiros de dados mais recentes da pasta DATA_PROCESS para DataFrames.
    """
    

    # Carregar os DataFrames
    df_events_BEST = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SCHEDULES_BEST, NAME_FILE_SCHEDULES_BEST), sheet_name="MergedData_Valid")
    
    


    # Logging dos resultados
    if df_events_BEST is not None:
        logger.info(f"DataFrame de eventos carregado com sucesso ({len(df_events_BEST)} linhas).")
    return df_events_BEST

def main():
    """
    Função principal para filtrar e juntar os dados.
    """
    logger.notice("--- INÍCIO DO PROCESSO DE FILTRAGEM E MERGE DE DADOS ---")

    # 1. Carregar os dados
    df_events = load_dataframes()

    
    # 2. Filtrar colunas e linhas inválidas dos eventos
    logger.notice("--- Passo 1: Extract Schedules SHOPIA ---")
    df_events = extract_relation_teachers_best(df_events)
    
    
    

    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()