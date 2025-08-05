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

# --- Variáveis de Controlo ---
SOURCE_DATA_DIR = os.path.join("DATA_PROCESS")
SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE = os.path.join(SOURCE_DATA_DIR, "DATA_UPDATE")
NAME_FILE_SCHEDULES_SHOPIA = "df_events_SHOPIA_FINAL.xlsx"
ANO_LECTIVO = 2025 # Definir o ano letivo aqui

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
    
    df_horarios_shopia = pd.read_excel(os.path.join(SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE, NAME_FILE_SCHEDULES_SHOPIA), sheet_name="NHORARIOS")
    logger.info(f"DataFrame de horários da SHOPIA carregado com sucesso ({len(df_horarios_shopia)} linhas).")
    
    return df_horarios_shopia


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
    
    # 3. Chamar a função para editar as linhas de horário
    df_horarios_atualizado = edit_linha_horario(client, logger, df_horarios_shopia, ano_lectivo=ANO_LECTIVO)

    # 4. Guardar o DataFrame com as respostas da atualização
    output_filename = f"updated_{NAME_FILE_SCHEDULES_SHOPIA}"
    output_filepath = os.path.join(SOURCE_DATA_DIR_NHORARIOS_TO_UPDATE, output_filename)
    df_horarios_atualizado.to_excel(output_filepath, index=False, sheet_name="UpdatedHorarios")
    logger.info(f"Processo concluído. Ficheiro com resultados da atualização guardado em: {output_filepath}")


    logger.notice("--- FIM DO PROCESSO ---")

if __name__ == "__main__":
    main()
