import pandas as pd
import os
import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.api.client import ApiClient 
    

try:
    from src.entities.event_type.dto import ReadExcelDataEventType, EventTypeParcialDTO
    from src.api.client import ApiClient as _ApiClient_runtime # Para uso em runtime
    from src.utils.log_utils import ColoredFormatter # Adicionado
except ImportError as e:
    logging.basicConfig(level=logging.ERROR) # Apenas para este erro de importação inicial
    logging.error(f"Falha crítica ao importar DTOs ou ApiClient em event_type_processor: {e}. O módulo pode não funcionar.")
    _ApiClient_runtime = None 
    EventTypeParcialDTO = None # Garante que está definido mesmo em caso de falha de importação
    ReadExcelDataEventType = None # Adicionado para consistência

# Configurar um logger para este módulo
logger = logging.getLogger(__name__) # Usar __name__ é uma boa prática


# Constantes locais para o caminho do ficheiro e nome da folha
# Assumindo que 'DATA_PROCESS' é um subdiretório direto da raiz do projeto.
# Se for relativo a 'src' ou outro local, ajuste o base_path.
BASE_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # Vai para a raiz do projeto a partir de src/core/
DATA_PROCESS_SUBDIR = "DATA_PROCESS"
EXCEL_FILENAME = "TITULOS-FACULTADES.xlsx"
SHEET_NAME = "TIPOS_EVENTO"

API_EVENT_TYPES_ENDPOINT = "/EventTypes" # Constante para o endpoint

def load_event_types_data() -> Optional[pd.DataFrame]:
    """
    Carrega dados iniciais de tipos de evento da folha TIPOS_EVENTOS 
    do ficheiro TITULOS-FACULTADES.xlsx localizado no diretório DATA_PROCESS.
    Esta função é o primeiro passo para obter os dados de tipos de evento, 
    podendo ser seguida por chamadas a API para enriquecimento ou validação.

    Utiliza a DTO ReadExcelDataEventType para determinar quais colunas carregar do Excel.

    Returns:
        Optional[pd.DataFrame]: Um DataFrame com os dados carregados,
                                 ou None se ocorrer um erro.
    """
    excel_file_path = os.path.join(BASE_PROJECT_DIR, DATA_PROCESS_SUBDIR, EXCEL_FILENAME)
    logger.info(f"A iniciar o carregamento de tipos de evento do ficheiro Excel: {excel_file_path}, folha: '{SHEET_NAME}'")

    columns_to_load_excel = None
    try:
        columns_to_load_excel = ReadExcelDataEventType.get_field_names()
        if not columns_to_load_excel:
            logger.warning("O método get_field_names() de ReadExcelDataEventType retornou uma lista vazia ou None. Todas as colunas do Excel serão carregadas.")
            columns_to_load_excel = None
        else:
            logger.info(f"Colunas a serem carregadas do Excel (definidas por ReadExcelDataEventType): {columns_to_load_excel}")
    except AttributeError:
        logger.error("A classe 'ReadExcelDataEventType' não possui o método 'get_field_names()'. Todas as colunas do Excel serão carregadas.")
        columns_to_load_excel = None
    except Exception as e:
        logger.error(f"Erro ao obter nomes de colunas de ReadExcelDataEventType: {e}. Todas as colunas do Excel serão carregadas.")
        columns_to_load_excel = None

    if not os.path.exists(excel_file_path):
        logger.error(f"Ficheiro Excel não encontrado em: {excel_file_path}")
        return None

    try:
        df_event_types_excel = pd.read_excel(
            excel_file_path,
            sheet_name=SHEET_NAME,
            usecols=columns_to_load_excel
        )
        
        if columns_to_load_excel:
            loaded_cols = list(df_event_types_excel.columns)
            missing_cols = [col for col in columns_to_load_excel if col not in loaded_cols]
            if missing_cols:
                logger.warning(f"Nem todas as colunas solicitadas foram encontradas na folha Excel '{SHEET_NAME}'. Colunas em falta: {missing_cols}")
            logger.info(f"Carregados {len(df_event_types_excel)} registos e colunas {loaded_cols} da folha Excel '{SHEET_NAME}'.")
        else:
            logger.info(f"Carregados {len(df_event_types_excel)} registos e todas as colunas disponíveis ({list(df_event_types_excel.columns)}) da folha Excel '{SHEET_NAME}'.")

        if df_event_types_excel.empty:
            logger.warning(f"O DataFrame carregado da folha Excel '{SHEET_NAME}' está vazio.")
        
        return df_event_types_excel

    except FileNotFoundError:
        logger.error(f"Erro: Ficheiro Excel não encontrado em {excel_file_path} ao tentar ler com pandas.")
        return None
    except ValueError as ve:
        logger.error(f"Erro ao ler o Excel: Folha '{SHEET_NAME}' não encontrada em '{excel_file_path}'. Detalhes: {ve}")
        return None
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado ao carregar tipos de evento do Excel: {e}", exc_info=True)
        return None

def fetch_event_types_from_api(api_client: 'ApiClient') -> Optional[pd.DataFrame]:
    """
    Busca todos os EventTypes da API a partir do endpoint /EventTypes e os processa num DataFrame.
    Utiliza EventTypeParcialDTO para definir as colunas de interesse.

    Args:
        api_client: Instância do ApiClient para fazer a chamada à API.

    Returns:
        pd.DataFrame: Um DataFrame contendo os EventTypes (id, name, active)
                      ou um DataFrame vazio se a busca falhar ou não houver dados.
    """
    logger.info(f"A iniciar busca de EventTypes da API a partir do endpoint: {API_EVENT_TYPES_ENDPOINT}")
    default_empty_df = pd.DataFrame() # DataFrame vazio por defeito a ser retornado

    if _ApiClient_runtime is None or EventTypeParcialDTO is None:
        logger.error("Dependências ApiClient ou EventTypeParcialDTO não estão disponíveis. Não é possível buscar EventTypes da API.")
        return default_empty_df

    if not api_client:
        logger.warning("ApiClient não fornecido para fetch_event_types_from_api. Não é possível buscar EventTypes.")
        return default_empty_df
    
    if not isinstance(api_client, _ApiClient_runtime):
        logger.error(f"api_client fornecido não é uma instância válida de ApiClient. Tipo: {type(api_client)}")
        return default_empty_df

    try:
        logger.info(f"Fazendo chamada GET para o endpoint {API_EVENT_TYPES_ENDPOINT}...")
        response_data = api_client.get_data(API_EVENT_TYPES_ENDPOINT) 
        
        event_types_list_from_api = None

        # A API pode retornar os dados diretamente numa lista ou dentro de um objeto com uma chave 'data'
        if response_data and isinstance(response_data, dict) and 'data' in response_data and isinstance(response_data['data'], list):
            event_types_list_from_api = response_data['data']
        elif response_data and isinstance(response_data, list):
            event_types_list_from_api = response_data
        else:
            logger.error(f"Resposta inesperada ou estrutura de dados inválida do endpoint {API_EVENT_TYPES_ENDPOINT}. Resposta: {response_data}")
            return default_empty_df

        if not event_types_list_from_api:
            logger.info(f"Nenhum EventType retornado pela API do endpoint {API_EVENT_TYPES_ENDPOINT}.")
            return default_empty_df # Retorna DataFrame vazio se a lista estiver vazia
        
        logger.info(f"Recebidos {len(event_types_list_from_api)} EventTypes da API.")

        # Usar EventTypeParcialDTO para obter os nomes das colunas desejadas
        api_columns = EventTypeParcialDTO.get_api_field_names()
        df_from_api = pd.DataFrame(event_types_list_from_api)

        missing_api_cols = [col for col in api_columns if col not in df_from_api.columns]
        if missing_api_cols:
            logger.error(
                f"As seguintes colunas esperadas (definidas em EventTypeParcialDTO: {api_columns}) não foram encontradas nos dados da API: {missing_api_cols}. "
                f"Colunas disponíveis na API: {df_from_api.columns.tolist()}. Verifique a DTO e a resposta da API."
            )
            return default_empty_df
        
        # Selecionar apenas as colunas desejadas e na ordem definida pela DTO
        df_api_processed = df_from_api[api_columns].copy()
        logger.info(f"DataFrame de EventTypes da API processado com {len(df_api_processed)} linhas e colunas: {df_api_processed.columns.tolist()}")
        
        return df_api_processed

    except Exception as e:
        logger.error(f"Erro ao buscar ou processar EventTypes da API ({API_EVENT_TYPES_ENDPOINT}): {e}", exc_info=True)
        return default_empty_df

# Renomeada para indicar que é uma função auxiliar interna
def _fetch_event_types_from_api(api_client: 'ApiClient') -> Optional[pd.DataFrame]:
    """
    Busca todos os EventTypes da API a partir do endpoint /EventTypes e os processa num DataFrame.
    Utiliza EventTypeParcialDTO para definir as colunas de interesse.
    Esta é uma função auxiliar para load_processed_event_types.
    """
    logger.info(f"A iniciar busca de EventTypes da API (função auxiliar) a partir do endpoint: {API_EVENT_TYPES_ENDPOINT}")
    default_empty_df = pd.DataFrame()

    if _ApiClient_runtime is None or EventTypeParcialDTO is None:
        logger.error("Dependências ApiClient ou EventTypeParcialDTO não estão disponíveis. Não é possível buscar EventTypes da API.")
        return default_empty_df

    if not api_client:
        logger.warning("ApiClient não fornecido para _fetch_event_types_from_api. Não é possível buscar EventTypes.")
        return default_empty_df
    
    if not isinstance(api_client, _ApiClient_runtime):
        logger.error(f"api_client fornecido não é uma instância válida de ApiClient. Tipo: {type(api_client)}")
        return default_empty_df

    try:
        response_data = api_client.get_data(API_EVENT_TYPES_ENDPOINT) 
        event_types_list_from_api = None
        if response_data and isinstance(response_data, dict) and 'data' in response_data and isinstance(response_data['data'], list):
            event_types_list_from_api = response_data['data']
        elif response_data and isinstance(response_data, list):
            event_types_list_from_api = response_data
        else:
            logger.error(f"Resposta inesperada ou estrutura de dados inválida do endpoint {API_EVENT_TYPES_ENDPOINT}. Resposta: {response_data}")
            return default_empty_df

        if not event_types_list_from_api:
            logger.info(f"Nenhum EventType retornado pela API do endpoint {API_EVENT_TYPES_ENDPOINT}.")
            return default_empty_df
        
        logger.info(f"Recebidos {len(event_types_list_from_api)} EventTypes da API.")
        api_columns = EventTypeParcialDTO.get_api_field_names()
        df_from_api = pd.DataFrame(event_types_list_from_api)

        missing_api_cols = [col for col in api_columns if col not in df_from_api.columns]
        if missing_api_cols:
            logger.error(
                f"As seguintes colunas esperadas (definidas em EventTypeParcialDTO: {api_columns}) não foram encontradas nos dados da API: {missing_api_cols}. "
                f"Colunas disponíveis na API: {df_from_api.columns.tolist()}."
            )
            return default_empty_df
        
        df_api_processed = df_from_api[api_columns].copy()
        logger.info(f"DataFrame de EventTypes da API processado com {len(df_api_processed)} linhas e colunas: {df_api_processed.columns.tolist()}")
        return df_api_processed
    except Exception as e:
        logger.error(f"Erro ao buscar ou processar EventTypes da API ({API_EVENT_TYPES_ENDPOINT}): {e}", exc_info=True)
        return default_empty_df

# Função principal a ser chamada por main_insert_event.py
def get_processed_event_types(api_client: 'ApiClient') -> pd.DataFrame: # Alterado para retornar sempre DataFrame (pode ser vazio)
    """
    Carrega dados de tipos de evento do Excel, busca dados da API,
    realiza um left merge (Excel como base, em 'name') e retorna um DataFrame
    contendo apenas as linhas que tiveram correspondência em ambos.
    Avisa sobre tipos de evento do Excel não encontrados na API.
    """
    logger.info("=== Iniciando processamento de Tipos de Evento (Excel + API) ===")
    empty_df_on_error = pd.DataFrame() # DataFrame a ser retornado em caso de erro ou sem correspondências 'both'

    # 1. Carregar e preparar dados do Excel
    if ReadExcelDataEventType is None:
        logger.error("DTO ReadExcelDataEventType não disponível. Abortando carregamento do Excel.")
        return empty_df_on_error
        
    # Definir excel_file_path aqui, antes de ser usado
    excel_file_path = os.path.join(BASE_PROJECT_DIR, DATA_PROCESS_SUBDIR, EXCEL_FILENAME)

    columns_to_load_excel = None
    try:
        columns_to_load_excel = ReadExcelDataEventType.get_field_names()
        if not columns_to_load_excel:
            logger.warning("ReadExcelDataEventType.get_field_names() retornou vazio. Todas as colunas do Excel serão carregadas.")
        else:
            logger.info(f"Colunas do Excel a carregar (DTO): {columns_to_load_excel}")
    except Exception as e:
        logger.error(f"Erro ao obter colunas de ReadExcelDataEventType: {e}. Carregando todas as colunas do Excel.")

    if not os.path.exists(excel_file_path):
        logger.error(f"Ficheiro Excel não encontrado: {excel_file_path}")
        return None

    try:
        df_excel_event_types = pd.read_excel(excel_file_path, sheet_name=SHEET_NAME, usecols=columns_to_load_excel)
        logger.info(f"Carregados {len(df_excel_event_types)} registos do Excel (folha '{SHEET_NAME}'). Colunas: {df_excel_event_types.columns.tolist()}")
        if df_excel_event_types.empty:
            logger.warning("DataFrame do Excel para tipos de evento está vazio.")
            # Pode-se decidir retornar aqui se o Excel for a base essencial e estiver vazio
            # return df_excel_event_types # ou None
    except Exception as e:
        logger.error(f"Erro ao carregar tipos de evento do Excel: {e}", exc_info=True)
        return None # Falha ao carregar Excel é crítica aqui

    # 2. Buscar dados da API
    # api_client é passado para esta função principal, então pode ser usado aqui
    df_api_event_types = _fetch_event_types_from_api(api_client)

    df_api_event_types.to_excel('./DATA_PROCESS/DATA_PROD_TEMP/EventTypes_UCJC.xlsx', sheet_name='EVENT_TYPES_API')
        
    if df_api_event_types is None or df_api_event_types.empty:
        logger.warning("DATA API TO EVENT TYPE NOT FOUND")
        return df_excel_event_types 

    
    try:
        merged_df = pd.merge(
            df_excel_event_types,
            df_api_event_types,
            how="left",
            on="name",
            indicator=True
        )

        merged_df_final = merged_df[merged_df['_merge'] == 'both'].copy()
        
        
        logger.info(f"Merge concluído. DataFrame final (apenas correspondências 'both') tem {len(merged_df_final)} linhas.")

        # Conversão para Int64Dtype para colunas que deveriam ser inteiros
        if not merged_df_final.empty:
            cols_to_convert_to_int = []
            
            # Coluna 'id' (da API, representa o ID do EventType no BWP)
            if 'id' in merged_df_final.columns:
                cols_to_convert_to_int.append('id')
            
            # Coluna 'faculty_id' (do Excel)
            if 'faculty_id' in merged_df_final.columns:
                cols_to_convert_to_int.append('faculty_id')

            for col in cols_to_convert_to_int:
                if col in merged_df_final.columns: 
                    try:
                        if merged_df_final[col].notna().any(): 
                            merged_df_final[col] = merged_df_final[col].astype(float).astype(pd.Int64Dtype())
                            logger.info(f"Coluna '{col}' convertida com sucesso para Int64Dtype.")
                        
                    except Exception as e:
                        logger.warning(f"Não foi possível converter a coluna '{col}' para Int64Dtype: {e}. Valores atuais: {merged_df_final[col].unique()[:5]}")
                


        merged_df_left_only = merged_df[merged_df['_merge'] == 'left_only']
        

        if '_merge' in merged_df_final.columns: # Assegurar que a coluna existe antes de drop
            merged_df_final.drop(columns=['_merge'], inplace=True)

        if not merged_df_left_only.empty:
            
            unmatched_names = merged_df_left_only['name'].unique().tolist()
            logger.warning(f"EVENT TYPE NOT FOUND IN API: {unmatched_names}")
        
        if merged_df_final.empty:
            logger.info("WITHOUT MATCHING EVENT TYPE")
            
        return merged_df_final # Retorna o DataFrame com as correspondências 'both'

    except KeyError as ke:
        logger.error(f"Erro de chave durante o merge: {ke}. Verifique se as colunas de merge ('event_type_name' no Excel, 'name' na API) existem.")
        logger.error(f"Colunas do DataFrame do Excel: {df_excel_event_types.columns.tolist()}")
        logger.error(f"Colunas do DataFrame da API: {df_api_event_types.columns.tolist()}")
        return df_excel_event_types # Retorna dados do Excel como fallback
    except Exception as e:
        logger.error(f"Erro durante o merge dos DataFrames de tipos de evento: {e}", exc_info=True)
        return df_excel_event_types # Retorna dados do Excel como fallback

if __name__ == '__main__':
    # Este bloco é para teste rápido do módulo isoladamente
    # Configurar logging básico para ver a saída se executar este ficheiro diretamente
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')
    
    logger.info("--- Testando get_processed_event_types (Excel + API + Merge) ---")
    
    logger.warning("Teste de get_processed_event_types requer um ApiClient configurado e ficheiro Excel. Secção de teste simplificada.")
    