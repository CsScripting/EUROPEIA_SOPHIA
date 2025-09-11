import os
import pandas as pd
import numpy as np
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
log_file_name = f"4.extract_schedules_update_new_2_{config.INSTITUTION}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

'''
IDENTIFICAR FICHEIRO SAIDA
'''


'''
GUARDA:
 ** BEST_MAP_NHORARIOS --> GUARDA RELAÇÂO DE DADOS ENTRE BEST E NHORARIOS
    1- Existe Relação entre BEST e NHORARIOS
    0 - Não existe Relação entre BEST e NHORARIOS

** df_NHORARIOS_FINAL --> GUARDA DADOS DE NHORARIOS
   DADOS SUJEITOS A PROCESSO DE UPDATE

'''


'''
IDENTIFICAR FICHEIRO SAIDA
'''
# Mapeamento de instituição para prefixo do arquivo
INSTITUTION_TO_PREFIX = {
    'QA': 'QA',
    'Europeia': 'EU',
    'UE_IADE': 'IADE',
    'IPAM_Porto': 'IPAM_POR',
    'IPAM_Lisboa': 'IPAM_LIS'
}

ano_semestre = "2025_PRIMER"
# Obter o prefixo correto para o nome do arquivo
FILE_PREFIX = INSTITUTION_TO_PREFIX.get(config.INSTITUTION, config.INSTITUTION)




# --- Setup Output Directories ---
DATA_PROCESS_DIR = "DATA_PROCESS"
INSTITUTION_DIR = os.path.join(DATA_PROCESS_DIR, FILE_PREFIX)

# Diretórios de entrada
DATA_BEST_DIR = os.path.join(INSTITUTION_DIR, "DATA_BEST")
DATA_SOPHIA_DIR = os.path.join(INSTITUTION_DIR, "DATA_SOPHIA")

# Diretórios de saída
VALIDATION_DATA_BEST_DIR = os.path.join(INSTITUTION_DIR, "VALIDATION_DATA_BEST")
VALIDATION_DATA_SOPHIA_DIR = os.path.join(INSTITUTION_DIR, "VALIDATION_DATA_SOPHIA")

# Criar estrutura de diretórios
os.makedirs(VALIDATION_DATA_BEST_DIR, exist_ok=True)
os.makedirs(VALIDATION_DATA_SOPHIA_DIR, exist_ok=True)

# Nomes dos arquivos
NAME_FILE_SCHEDULES_BEST = f"Valid_data_BEST_{FILE_PREFIX}_{ano_semestre}.xlsx"
NAME_FILE_SCHEDULES_SHOPIA = f"Valid_data_NHORARIOS_{FILE_PREFIX}_{ano_semestre}.xlsx"

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
    Carrega os ficheiros de dados necessários das pastas VALIDATION_DATA_BEST e VALIDATION_DATA_SOPHIA.
    """
    df_events_BEST = pd.read_excel(os.path.join(VALIDATION_DATA_BEST_DIR, NAME_FILE_SCHEDULES_BEST), sheet_name="MergedData_Valid")
    logger.info(f"DataFrame de eventos BEST carregado com sucesso ({len(df_events_BEST)} linhas).")
    
    df_horarios_shopia = pd.read_excel(os.path.join(VALIDATION_DATA_SOPHIA_DIR, NAME_FILE_SCHEDULES_SHOPIA), sheet_name="NHORARIOS")
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

    def move_column_before_last_n(df, column_name, n):
        cols = df.columns.tolist()
        cols.remove(column_name)
        insert_pos = len(cols) - n
        cols.insert(insert_pos, column_name)
        return df[cols]

    df_events_SHOPIA_FINAL['DIMENSAO_SOPHIA'] = df_events_SHOPIA_FINAL['DgTurma'] + "_" + df_events_SHOPIA_FINAL['CdDisc']
    df_events_SHOPIA_FINAL = move_column_before_last_n(df_events_SHOPIA_FINAL, 'DIMENSAO_SOPHIA', 4)

    df_events_SHOPIA_FINAL = move_column_before_last_n(df_events_SHOPIA_FINAL, 'CdDocente', 6)

    df_events_SHOPIA_FINAL ['NovoProf']= np.where(df_events_SHOPIA_FINAL['DSD_NR_BEST'] == 0, 'Keep', df_events_SHOPIA_FINAL['NovoProf'])

    # Guardar o DataFrame final em um novo ficheiro Excel
    output_file_path = os.path.join(VALIDATION_DATA_SOPHIA_DIR, f'NHORARIOS_FINAL_MAPPING_{FILE_PREFIX}_{ano_semestre}.xlsx')
    df_events_SHOPIA_FINAL.to_excel(output_file_path, index=False, sheet_name="NHORARIOS", freeze_panes=(1,0))
    logger.info(f"O ficheiro final foi guardado em: {output_file_path}")

    df_events_BEST['DIMENSAO_SOPHIA'] = df_events_BEST['DgTurma'].astype(str) + "_" + df_events_BEST['CdDisc_SHOPIA'].astype(str)

    df_events_SHOPIA_FINAL = df_events_SHOPIA_FINAL[['DIMENSAO_SOPHIA']].drop_duplicates()
    df_events_SHOPIA_FINAL['NHorario'] = 1

    df_events_SHOPIA_FINAL= df_events_SHOPIA_FINAL.astype({"DIMENSAO_SOPHIA": "str"})
    df_events_BEST = df_events_BEST.astype({"DIMENSAO_SOPHIA": "str"})
    
    df_events_BEST = pd.merge(df_events_BEST, df_events_SHOPIA_FINAL, on=["DIMENSAO_SOPHIA"], how="left", indicator=True)
    matches_Nhorarios = len(df_events_BEST[df_events_BEST['_merge'] == 'both'])
    logger.notice(f"Merge N_HORARIOS | HORARIOS BEST: {matches_Nhorarios} Linhas encontradas.")
    df_events_BEST['NHorario'] = np.where(df_events_BEST['_merge'] == 'left_only', 0, 1)
    df_events_BEST = df_events_BEST.drop(columns=['_merge'])


    # Guardar o DataFrame final em um novo ficheiro Excel
    output_file_path = os.path.join(VALIDATION_DATA_BEST_DIR, f'BEST_MAP_NHORARIOS_{FILE_PREFIX}_{ano_semestre}.xlsx')
    df_events_BEST.to_excel(output_file_path, index=False, sheet_name="BEST_NHORARIOS", freeze_panes=(1,0))
    logger.info(f"O ficheiro final foi guardado em: {output_file_path}")



    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()
