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
    from src.core.event_processor_europeia import filter_columns_best_events, split_data_st_groups, rename_columns, merge_data_entities, split_data_teachers, merge_nr_contab_n_horarios
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de que o script está na raiz do projeto.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"filter_merge_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# --- Variáveis de Controlo ---
# Diretório onde os ficheiros de entrada estão localizados
SOURCE_DATA_DIR_SCHEDULES_BEST = os.path.join("DATA_PROCESS", "SCHEDULES_BEST")
NAME_FILE_SCHEDULES_BEST = "fetch_event_EU_2025_PRIMER.xlsx"

# Padrões para encontrar os ficheiros mais recentes

INSTITUTION = "EU_2025_PRIMER"

SOURCE_DATA_DIR_SHOPIA = os.path.join("DATA_PROCESS")

SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE = os.path.join(SOURCE_DATA_DIR_SHOPIA, "DATA_UPDATE")
COURSES_FILE = "Cursos_QA.xlsx"
DISCIPLINAS_FILE = "Disciplinas_QA_Ano2025.xlsx"
TURMAS_FILE = "Turmas_QA_Ano2025.xlsx"
PROFESSORES_FILE = "Docentes_QA_E_A_NCont_2025-08-05_12-53-05.xlsx"
NHORARIOS_FILE = "Horarios_QA_Ano2025.xlsx"


def load_dataframes():
    """
    Carrega os ficheiros de dados mais recentes da pasta DATA_PROCESS para DataFrames.
    """
    

    # Carregar os DataFrames
    df_events = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SCHEDULES_BEST, NAME_FILE_SCHEDULES_BEST), sheet_name="Viewer_Events")
    df_courses = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SHOPIA, COURSES_FILE), sheet_name="Cursos_Ativos")
    df_disciplinas = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SHOPIA, DISCIPLINAS_FILE), sheet_name="Disciplinas")
    df_turmas = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SHOPIA, TURMAS_FILE) , sheet_name="Turmas")
    df_professores = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SHOPIA, PROFESSORES_FILE) , sheet_name="Docentes_Com_NContabilistico")
    df_nhorarios = pd.read_excel(os.path.join(SOURCE_DATA_DIR_SHOPIA, NHORARIOS_FILE) , sheet_name="Horarios")


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

    

    # 6. Salvar o resultado final
    output_filename = os.path.join(SOURCE_DATA_DIR_SCHEDULES_BEST, f"Valid_data_{INSTITUTION}.xlsx")
    df_merged_valid_events.to_excel(output_filename, index=False, sheet_name="MergedData_Valid")
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")
    output_filename = os.path.join(SOURCE_DATA_DIR_SCHEDULES_BEST, f"Invalid_data_{INSTITUTION}.xlsx")
    df_merged_invalid_events.to_excel(output_filename, index=False, sheet_name="MergedData_Invalid")
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")


    df_nhorarios_valid, df_nhorarios_invalid = merge_nr_contab_n_horarios(df_nhorarios, df_professores)

    # 6. Salvar o resultado final
    output_filename = os.path.join(SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE, f"Valid_data_NHORARIOS_{INSTITUTION}.xlsx")
    df_nhorarios_valid.to_excel(output_filename, index=False, sheet_name="NHORARIOS")
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")
    output_filename = os.path.join(SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE, f"Invalid_data_NHORARIOS_{INSTITUTION}.xlsx")
    df_nhorarios_invalid.to_excel(output_filename, index=False, sheet_name="NHORARIOS")
    logger.info(f"Dados finais guardados com sucesso em: {output_filename}")

    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()
