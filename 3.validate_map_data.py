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
    from src.core.event_processor_europeia import filter_columns_best_events, split_data_st_groups, rename_columns, merge_data_entities, split_data_teachers, merge_nr_contab_n_horarios
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de que o script está na raiz do projeto.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"validate_map_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# --- Import config ---
import config

# Padrões para encontrar os ficheiros mais recentes

'''
IDENTIFICAR FICHEIRO SAIDA


'''

ano_semestre = "2025_PRIMER"

if config.INSTITUTION == "Europeia":
    INSTITUTION_NAME_FILE = 'EU' + "_" + ano_semestre
elif config.INSTITUTION == "UE_IADE":
    INSTITUTION_NAME_FILE = 'IADE' + "_" + ano_semestre
elif config.INSTITUTION == "IPAM_Porto":
    INSTITUTION_NAME_FILE = 'IPAM_POR' + "_" + ano_semestre
elif config.INSTITUTION == "IPAM_Lisboa":
    INSTITUTION_NAME_FILE = 'IPAM_LIS' + "_" + ano_semestre
elif config.INSTITUTION == "QA":
    INSTITUTION_NAME_FILE = 'QA' + "_" + ano_semestre
else:
    INSTITUTION_NAME_FILE = config.INSTITUTION

'''
### DADOS DE ENTRADA ####:

* EVENTOS DA RESPECTIVA INSTITUIÇÃO --> EXTRAIDOS DESDE BEST
* DADOS DA RESPECTIVA INSTITUIÇÃO PROVENINETES DE SHOPIA --> EXTRAIDOS DESDE SHOPIA

### OBJETIVO FINAL ###

* VERIFICAR SE DADOS DE EVENTOS (3 DIMENSÕES) EXISTEM NO SHOPIA 
    --> EM SCHEDULES_BEST GUARDA EVENTOS "VALIDOS" E "INVALIDOS"
* VERIFICAR SE DADOS DE NHORARIOS TEM PROFESSORES MAPEADOS EM BEST
    --> EM DATA_UPDATE GUARDA NHORARIOS "VALIDOS" E "INVALIDOS"

'''

# Setup das pastas base
DATA_PROCESS_DIR = "DATA_PROCESS"

# Mapeamento de instituição para prefixo do arquivo
INSTITUTION_TO_PREFIX = {
    'QA': 'QA',
    'Europeia': 'EU',
    'UE_IADE': 'IADE',
    'IPAM_Porto': 'IPAM_POR',
    'IPAM_Lisboa': 'IPAM_LIS'
}

# Obter o prefixo correto para o nome do arquivo
FILE_PREFIX = INSTITUTION_TO_PREFIX.get(config.INSTITUTION, config.INSTITUTION)

# Usar FILE_PREFIX para a estrutura de pastas
INSTITUTION_DIR = os.path.join(DATA_PROCESS_DIR, FILE_PREFIX)

## DADOS BEST - Nova estrutura
DATA_BEST_DIR = os.path.join(INSTITUTION_DIR, "DATA_BEST")
# Exceção: Ao ler de DATA_BEST quando é QA, usar EU
NAME_FILE_SCHEDULES_BEST = f"fetch_event_{'EU' if config.INSTITUTION == 'QA' else FILE_PREFIX}_{ano_semestre}.xlsx"

## DADOS SOPHIA - Nova estrutura
DATA_SOPHIA_DIR = os.path.join(INSTITUTION_DIR, "DATA_SOPHIA")
COURSES_FILE = f"Cursos_{FILE_PREFIX}.xlsx"
DISCIPLINAS_FILE = f"Disciplinas_{FILE_PREFIX}_Ano2025.xlsx"
TURMAS_FILE = f"Turmas_{FILE_PREFIX}_Ano2025.xlsx"
PROFESSORES_FILE = f"Docentes_{FILE_PREFIX}_E_A_NCont.xlsx"
NHORARIOS_FILE = f"Horarios_{FILE_PREFIX}_Ano2025.xlsx"

## PASTAS DE SAÍDA
VALIDATION_DATA_BEST_DIR = os.path.join(INSTITUTION_DIR, "VALIDATION_DATA_BEST")
VALIDATION_DATA_SOPHIA_DIR = os.path.join(INSTITUTION_DIR, "VALIDATION_DATA_SOPHIA")

# Criar estrutura de diretórios
os.makedirs(VALIDATION_DATA_BEST_DIR, exist_ok=True)
os.makedirs(VALIDATION_DATA_SOPHIA_DIR, exist_ok=True)


def load_dataframes():
    """
    Carrega os ficheiros de dados das pastas DATA_BEST e DATA_SOPHIA para DataFrames.
    """
    
    # Carregar os DataFrames
    df_events = pd.read_excel(os.path.join(DATA_BEST_DIR, NAME_FILE_SCHEDULES_BEST), sheet_name="Viewer_Events")
    df_courses = pd.read_excel(os.path.join(DATA_SOPHIA_DIR, COURSES_FILE), sheet_name="Cursos_Ativos")
    df_disciplinas = pd.read_excel(os.path.join(DATA_SOPHIA_DIR, DISCIPLINAS_FILE), sheet_name="Disciplinas")
    df_turmas = pd.read_excel(os.path.join(DATA_SOPHIA_DIR, TURMAS_FILE), sheet_name="Turmas")
    df_professores = pd.read_excel(os.path.join(DATA_SOPHIA_DIR, PROFESSORES_FILE), sheet_name="Docentes_Com_NContabilistico")
    df_nhorarios = pd.read_excel(os.path.join(DATA_SOPHIA_DIR, NHORARIOS_FILE), sheet_name="Horarios")


    # Logging dos resultados
    if df_events is not None:
        logger.info(f"DataFrame de eventos carregado com sucesso ({len(df_events)} linhas).")
    if df_disciplinas is not None:
        logger.info(f"DataFrame de disciplinas carregado com sucesso ({len(df_disciplinas)} linhas).")
    if df_turmas is not None:
        logger.info(f"DataFrame de turmas carregado com sucesso ({len(df_turmas)} linhas).")
    if df_courses is not None:
        logger.info(f"DataFrame de cursos carregado com sucesso ({len(df_courses)} linhas).")
    if df_professores is not None:
        logger.info(f"DataFrame de professores carregado com sucesso ({len(df_professores)} linhas).")
    return df_events, df_disciplinas, df_turmas, df_courses, df_professores, df_nhorarios

def main():
    """
    Função principal para filtrar e juntar os dados.
    """
    logger.notice("--- INÍCIO DO PROCESSO DE FILTRAGEM E MERGE DE DADOS ---")

    # 1. Carregar os dados
    df_events, df_disciplinas, df_turmas, df_courses, df_professores, df_nhorarios = load_dataframes()

    

    # 2. Filtrar colunas e linhas inválidas dos eventos
    logger.notice("--- Passo 1: A filtrar dados de eventos ---")
    df_events = filter_columns_best_events(df_events)
    
    
    # 3. Dividir os dados por studentGroup_names
    logger.info("--- Passo 2: A dividir dados por grupos de estudantes ---")
    df_events = split_data_st_groups(df_events)


    # 3.1 Dividir os dados por NContabilistico
    logger.info("--- Passo 2.1: A dividir dados por NContabilistico ---")
    df_events = split_data_teachers(df_events)
    
    # 4. Renomear colunas para o merge
    logger.info("--- Passo 3: A renomear colunas para compatibilidade ---")
    df_events = rename_columns(df_events)

    # 5. Fazer o merge dos dataframes
    logger.info("--- Passo 4: A juntar dados de turmas, disciplinas e docentes ---")
    df_merged_valid_events, df_merged_invalid_events = merge_data_entities(
        df_events=df_events, 
        df_st_groups=df_turmas, 
        df_disciplinas=df_disciplinas,
        df_courses=df_courses,
        df_professores=df_professores
    )

    

    # 6. Salvar o resultado final - VALIDATION_DATA_BEST
    output_filename = os.path.join(VALIDATION_DATA_BEST_DIR, f"Valid_data_BEST_{INSTITUTION_NAME_FILE}.xlsx")
    df_merged_valid_events.to_excel(output_filename, index=False, sheet_name="MergedData_Valid", freeze_panes=(1,0))
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")
    output_filename = os.path.join(VALIDATION_DATA_BEST_DIR, f"Invalid_data_BEST_{INSTITUTION_NAME_FILE}.xlsx")
    df_merged_invalid_events.to_excel(output_filename, index=False, sheet_name="MergedData_Invalid", freeze_panes=(1,0))
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")


    df_nhorarios_valid, df_nhorarios_invalid = merge_nr_contab_n_horarios(df_nhorarios, df_professores)

    # 7. Salvar o resultado final - VALIDATION_DATA_SOPHIA
    output_filename = os.path.join(VALIDATION_DATA_SOPHIA_DIR, f"Valid_data_NHORARIOS_{INSTITUTION_NAME_FILE}.xlsx")
    df_nhorarios_valid.to_excel(output_filename, index=False, sheet_name="NHORARIOS", freeze_panes=(1,0))
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")
    output_filename = os.path.join(VALIDATION_DATA_SOPHIA_DIR, f"Invalid_data_NHORARIOS_{INSTITUTION_NAME_FILE}.xlsx")
    df_nhorarios_invalid.to_excel(output_filename, index=False, sheet_name="NHORARIOS", freeze_panes=(1,0))
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")

    # logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()
