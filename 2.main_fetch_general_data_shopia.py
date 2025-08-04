# 2.main_fetch_module_group_shopia.py
import logging
import sys
import os
import datetime
from zeep import Client, Settings
from zeep.transports import Transport
import pandas as pd

# --- Adicionar o caminho da raiz do projeto ao sys.path ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.utils.setup_logging import setup_colored_logging, redirect_stdout_stderr_to_log
    import config
    from config import suffix # Importar o sufixo dinâmico
    # Importar as funções refatoradas
    from GET_DATA.get_periodos import get_periodos
    from GET_DATA.get_cursos import get_cursos
    from GET_DATA.get_disciplinas import get_disciplinas
    from GET_DATA.get_turmas import get_turmas
    from GET_DATA.get_docentes import get_docentes
    from GET_DATA.get_horarios import get_horarios
except ImportError as e:
    print(f"Erro de importação: {e}. Verifique se o PYTHONPATH está configurado ou se está a executar a partir da raiz.")
    sys.exit(1)

# --- Configuração do Logging ---
log_dir = "LOGS"
log_file_name = f"main_module_group_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)

setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# --- Variáveis de Controlo ---
ANO_LECTIVO_A_CONSULTAR = 2025
# Defina o semestre a consultar: 1 para o primeiro, 2 para o segundo
PERIODO_SEMESTRE = 1 


def initialize_soap_client():
    """Inicializa e retorna o cliente SOAP com as configurações necessárias."""
    try:
        settings = Settings(strict=False, xml_huge_tree=True)
        transport = Transport(timeout=300)
        client = Client(config.WSDL_URL, settings=settings, transport=transport)
        logger.info(f"Cliente SOAP inicializado para o WSDL: {config.WSDL_URL}")
        logger.info(f"Sufixo de ficheiro a ser usado: '{suffix}'")
        return client
    except Exception as e:
        logger.error(f"Falha ao inicializar o cliente SOAP: {e}", exc_info=True)
        return None

def get_periodos_para_consulta(periodos_df, semestre):
    """Filtra e retorna os IDs dos períodos com base no semestre desejado."""
    if periodos_df is None or periodos_df.empty:
        logger.warning("DataFrame de períodos está vazio. Não foi possível determinar os períodos a consultar.")
        return []

    # Mapeamento dos nomes dos períodos
    mapa_periodos = {
        1: ["Anual", "1º semestre", "1º trimestre", "2º trimestre"],
        2: ["Anual", "2º semestre", "3º trimestre", "4º trimestre"]
    }

    nomes_a_procurar = mapa_periodos.get(semestre)
    if not nomes_a_procurar:
        logger.error(f"Valor de PERIODO_SEMESTRE inválido: {semestre}. Use 1 ou 2.")
        return []

    # Filtrar o DataFrame
    periodos_filtrados_df = periodos_df[periodos_df['DgPeriodo'].isin(nomes_a_procurar)]
    
    # Extrair e retornar os IDs
    periodos_ids = periodos_filtrados_df['CdPeriodo'].astype(int).tolist()
    
    logger.info(f"Períodos selecionados para o semestre {semestre}: {periodos_filtrados_df['DgPeriodo'].tolist()}")
    logger.info(f"IDs correspondentes: {periodos_ids}")
    
    return periodos_ids

def main():
    """
    Função principal para orquestrar a extração de dados de várias entidades do Sophia.
    """
    logger.notice("--- INÍCIO DO PROCESSO DE EXTRAÇÃO DE DADOS DO SOPHIA ---")

    client = initialize_soap_client()
    if not client:
        logger.error("A extração não pode continuar sem um cliente SOAP válido. A terminar.")
        return

    # 1. Obter Períodos e determinar quais consultar
    logger.notice("--- Passo 1 de 6: A obter dados de Períodos ---")
    periodos_df = get_periodos(client=client, logger=logger, suffix=suffix)
    
    PERIODOS_A_CONSULTAR = get_periodos_para_consulta(periodos_df, PERIODO_SEMESTRE)
    if not PERIODOS_A_CONSULTAR:
        logger.error("Nenhum período válido para consulta foi determinado. A extração de dados dependentes será ignorada.")

    # 2. Obter Cursos
    logger.notice("--- Passo 2 de 6: A obter dados de Cursos ---")
    try:
        get_cursos(client=client, logger=logger, suffix=suffix)
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado ao chamar get_cursos: {e}", exc_info=True)

    # 3. Obter Disciplinas (Módulos)
    if PERIODOS_A_CONSULTAR:
        logger.notice("--- Passo 3 de 6: A obter dados de Disciplinas ---")
        try:
            get_disciplinas(
                client=client,
                logger=logger,
                ano_lectivo=ANO_LECTIVO_A_CONSULTAR,
                periodos=PERIODOS_A_CONSULTAR,
                suffix=suffix
            )
        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado ao chamar get_disciplinas: {e}", exc_info=True)

    # 4. Obter Turmas (Grupos)
    if PERIODOS_A_CONSULTAR:
        logger.notice("--- Passo 4 de 6: A obter dados de Turmas ---")
        try:
            get_turmas(
                client=client,
                logger=logger,
                ano_lectivo=ANO_LECTIVO_A_CONSULTAR,
                periodos=PERIODOS_A_CONSULTAR, # Usando a lista dinâmica
                suffix=suffix
            )
        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado ao chamar get_turmas: {e}", exc_info=True)

    # 5. Obter Docentes
    logger.notice("--- Passo 5 de 6: A obter dados de Docentes ---")
    try:
        get_docentes(client=client, logger=logger, suffix=suffix)
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado ao chamar get_docentes: {e}", exc_info=True)

    # 6. Obter Horários
    if PERIODOS_A_CONSULTAR:
        logger.notice("--- Passo 6 de 6: A obter dados de Horários ---")
        try:
            get_horarios(
                client=client,
                logger=logger,
                ano_lectivo=ANO_LECTIVO_A_CONSULTAR,
                periodos=PERIODOS_A_CONSULTAR,
                suffix=suffix
            )
        except Exception as e:
            logger.error(f"Ocorreu um erro inesperado ao chamar get_horarios: {e}", exc_info=True)

    logger.notice("--- FIM DO PROCESSO DE EXTRAÇÃO ---")

if __name__ == "__main__":
    main()
