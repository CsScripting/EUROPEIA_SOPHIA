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
    from src.core.event_processor_europeia import iterate_relation_teachers_best_and_update_horarios_shopia
    import config
    from config import suffix
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
SOURCE_DATA_DIR = os.path.join("DATA_PROCESS")
SOURCE_DATA_DIR_SCHEDULES_BEST = os.path.join(SOURCE_DATA_DIR, "SCHEDULES_BEST")
NAME_FILE_SCHEDULES_BEST = "Valid_data_EU_2025_PRIMER.xlsx"
ANO_LECTIVO_A_CONSULTAR = 2025
SEMESTRE_A_CONSULTAR = "PRIMER" # Pode ser "PRIMER" ou "SEGUNDO"

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
    
    periodos_filepath = os.path.join(SOURCE_DATA_DIR, f"Periodos_{suffix}.xlsx")
    df_periodos = pd.read_excel(periodos_filepath)
    logger.info(f"DataFrame de períodos carregado com sucesso ({len(df_periodos)} linhas).")
    
    return df_events_BEST, df_periodos

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
    df_events_BEST, df_periodos = load_dataframes()
    
    # Mapear a string do semestre para a flag numérica
    semestre_flag = 1 if SEMESTRE_A_CONSULTAR == "PRIMER" else 2

    # 3. Iterar e verificar horários na SHOPIA
    logger.notice("--- A chamar a função para iterar sobre as relações e consultar a SHOPIA ---")
    df_best_updated, df_horarios_shopia = iterate_relation_teachers_best_and_update_horarios_shopia(
        df_best_teachers=df_events_BEST,
        client=client,
        logger=logger,
        df_periodos=df_periodos,
        ano_lectivo=ANO_LECTIVO_A_CONSULTAR,
        flag_semestre=semestre_flag
    )

    # 4. Salvar os resultados
    output_filename_best = os.path.join(SOURCE_DATA_DIR_SCHEDULES_BEST, f"Best_Relation_With_NHorario_{ANO_LECTIVO_A_CONSULTAR}_{SEMESTRE_A_CONSULTAR}.xlsx")
    df_best_updated.to_excel(output_filename_best, index=False, sheet_name="BestRelationUpdated")
    logger.info(f"Relação da BEST atualizada com a coluna 'NHorario' guardada em: {output_filename_best}")

    if not df_horarios_shopia.empty:
        output_filename_shopia = os.path.join(SOURCE_DATA_DIR, f"Horarios_Shopia_Encontrados_{ANO_LECTIVO_A_CONSULTAR}_{SEMESTRE_A_CONSULTAR}.xlsx")
        df_horarios_shopia.to_excel(output_filename_shopia, index=False, sheet_name="HorariosShopia")
        logger.info(f"Horários encontrados na SHOPIA guardados em: {output_filename_shopia}")
    else:
        logger.warning("Nenhum horário correspondente foi encontrado na SHOPIA, nenhum ficheiro de horários foi gerado.")


    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()
