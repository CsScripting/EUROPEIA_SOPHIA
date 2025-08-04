import pandas as pd
import numpy as np
import logging
import os
import ast
from src.core import constants

logger = logging.getLogger(__name__)

columns_to_keep = [
    "event_name",
    "day",
    "startTime",
    "endTime",
    "wlsSectionName",
    "eventType_name",
    "module_code",
    "CdDisc",
    "studentGroup_names",
    "course_names",
    "course_codes",
    "teacher_codes",
    "teacher_names",
    "Institution"
]

def filter_columns_best_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra o DataFrame de eventos para manter apenas as colunas essenciais
    e remove linhas onde dados críticos (studentGroup_names, CdDisc) estão em falta.
    """
    df_filtered = df[columns_to_keep].copy()
    logger.info(f"Colunas filtradas. DataFrame agora tem {len(df_filtered.columns)} colunas.")

    
    return df_filtered

columns_to_keep_shopia = [
    "CdTurma",
    "DgTurma",
    "CdDisc",
    "CdDocente"
]

def filter_columns_horarios_shopia(df: pd.DataFrame) -> pd.DataFrame:
    df_filtered = df[columns_to_keep_shopia].copy()
    logger.info(f"Colunas filtradas. DataFrame agora tem {len(df_filtered.columns)} colunas.")
    return df_filtered


def split_data_st_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande o DataFrame com base na coluna 'studentGroup_names'.
    Se uma célula em 'studentGroup_names' contém múltiplos grupos,
    a linha é duplicada para que cada grupo tenha a sua própria linha.
    """
    if 'studentGroup_names' not in df.columns:
        logger.error("A coluna 'studentGroup_names' não foi encontrada no DataFrame.")
        return df

    initial_rows = len(df)
    logger.info(f"A iniciar o split por grupos de estudantes. DataFrame tem {initial_rows} linhas.")
    
    # Colunas que se espera que sejam strings de listas
    list_str_columns = ['studentGroup_names', 'course_codes', 'course_names']

    # Função para converter string de lista para lista real
    def safe_literal_eval(val):
        if isinstance(val, str) and val.startswith('[') and val.endswith(']'):
            try:
                return ast.literal_eval(val)
            except (ValueError, SyntaxError):
                # Retorna o valor original ou uma lista com o valor se a conversão falhar
                return [val]
        # Se já for uma lista, retorna como está
        elif isinstance(val, list):
            return val
        # Para outros tipos (None, etc.), retorna como está para não quebrar o explode
        return val

    # Aplica a conversão a todas as colunas necessárias
    for col in list_str_columns:
        if col in df.columns:
            df[col] = df[col].apply(safe_literal_eval)
        else:
            logger.warning(f"A coluna '{col}' para o explode não foi encontrada.")
            # Garante que a coluna existe para o explode não falhar, preenchendo com None
            df[col] = None

    # Agora que as colunas são listas reais, podemos usar explode
    df_exploded = df.explode(list_str_columns)
    

    final_rows = len(df_exploded)
    logger.info(f"Divisão concluída. DataFrame agora tem {final_rows} linhas.")
    
    return df_exploded


def split_data_teachers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande o DataFrame com base na coluna 'teacher_names' e teacher_codes.
    Se uma célula em 'teacher_names' contém múltiplos docentes,
    a linha é duplicada para que cada docente tenha a sua própria linha.
    """
    if 'teacher_names' not in df.columns:
        logger.error("A coluna 'teacher_names' não foi encontrada no DataFrame.")
        return df

    initial_rows = len(df)
    logger.info(f"A iniciar o split por docentes. DataFrame tem {initial_rows} linhas.")

    # Colunas que se espera que sejam strings de listas
    list_str_columns = ['teacher_names', 'teacher_codes']

    # Função para converter string de lista para lista real
    def safe_literal_eval(val):
        if isinstance(val, str) and val.startswith('[') and val.endswith(']'):
            try:
                return ast.literal_eval(val)
            except (ValueError, SyntaxError):
                # Retorna o valor original ou uma lista com o valor se a conversão falhar
                return [val]
        # Se já for uma lista, retorna como está
        elif isinstance(val, list):
            return val
        # Para outros tipos (None, etc.), retorna como está para não quebrar o explode
        return val

    # Aplica a conversão a todas as colunas necessárias
    for col in list_str_columns:
        if col in df.columns:
            df[col] = df[col].apply(safe_literal_eval)
        else:
            logger.warning(f"A coluna '{col}' para o explode não foi encontrada.")
            # Garante que a coluna existe para o explode não falhar, preenchendo com None
            df[col] = None

    # Agora que as colunas são listas reais, podemos usar explode
    df_exploded = df.explode(list_str_columns)
    

    final_rows = len(df_exploded)
    logger.info(f"Divisão concluída. DataFrame agora tem {final_rows} linhas.")
    
    return df_exploded


columns_to_rename = {
    "studentGroup_names" : "DgTurma",
    "course_codes" : "CdCurso",
    "teacher_codes" : "NContabilistico",
}

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_renamed = df.rename(columns=columns_to_rename)
    return df_renamed


def merge_data_entities(df_events: pd.DataFrame, df_st_groups: pd.DataFrame, df_disciplinas: pd.DataFrame,
                                 df_courses: pd.DataFrame, df_professores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Junta os dados de turmas, disciplinas e docentes ao DataFrame de eventos.
    """
    if df_events.empty:
        logger.warning("O DataFrame de eventos está vazio. A saltar o processo de merge.")
        return pd.DataFrame(), pd.DataFrame() # Retorna dois dataframes vazios

    initial_rows = len(df_events)
    logger.notice(f"A iniciar o processo de merge. DataFrame de eventos inicial tem {initial_rows} linhas.")


    df_merged = df_events.copy()

    # merge COURSES
    df_courses_copy = df_courses[["CdCurso", "NmCurso"]].copy().drop_duplicates()
    df_courses_copy['ValidCourse'] = 1
    
    df_merged = df_merged.astype({"CdCurso": "str"})
    df_courses_copy = df_courses_copy.astype({"CdCurso": "str"})

    df_merged = pd.merge(df_merged, df_courses_copy, on=["CdCurso"], how="left", indicator=True)
    matches_horarios = len(df_merged[df_merged['_merge'] == 'both'])
    logger.notice(f"Merge CURSOS: {matches_horarios} Linhas encontradas.")
    df_merged['ValidCourse'] = np.where(df_merged['_merge'] == 'left_only', 0, 1)
    df_merged = df_merged.drop(columns=['_merge'])

    # merge DISCIPLINAS:
    df_disciplinas_copy = df_disciplinas[["CdDisc", "DgCadeira"]].copy().drop_duplicates()
    df_disciplinas_copy['ValidDisc'] = 1

    # --- LÓGICA DE NORMALIZAÇÃO ---
    logger.info("A normalizar os códigos 'CdDisc' (removendo a letra 'C') antes do merge.")
    if 'CdDisc' in df_merged.columns:
        df_merged['CdDisc'] = df_merged['CdDisc'].astype(str).str.replace('C', '', regex=False)
    if 'CdDisc' in df_disciplinas_copy.columns:
        df_disciplinas_copy['CdDisc'] = df_disciplinas_copy['CdDisc'].astype(str).str.replace('C', '', regex=False)
    
    df_merged = df_merged.astype({"CdDisc": "str"})
    df_disciplinas_copy = df_disciplinas_copy.astype({"CdDisc": "str"})

    df_merged = pd.merge(df_merged, df_disciplinas_copy, on=["CdDisc"], how="left", indicator=True)
    matches_horarios = len(df_merged[df_merged['_merge'] == 'both'])
    logger.notice(f"Merge DISCIPLINAS: {matches_horarios} Linhas encontradas.")
    df_merged['ValidDisc'] = np.where(df_merged['_merge'] == 'left_only', 0, 1)
    df_merged = df_merged.drop(columns=['_merge'])

    # merge TURMAS
    df_st_groups_copy = df_st_groups[["DgTurma"]].copy().drop_duplicates()
    df_st_groups_copy['ValidTurma'] = 1

    df_merged = df_merged.astype({"DgTurma": "str"})
    df_st_groups_copy = df_st_groups_copy.astype({"DgTurma": "str"})

    df_merged = pd.merge(df_merged, df_st_groups_copy, on=["DgTurma"], how="left", indicator=True)
    matches_turmas = len(df_merged[df_merged['_merge'] == 'both'])
    logger.notice(f"Merge TURMAS: {matches_turmas} Linhas encontradas.")
    df_merged['ValidTurma'] = np.where(df_merged['_merge'] == 'left_only', 0, 1)
    df_merged = df_merged.drop(columns=['_merge'])
    
    # merge PROFESSORES:
    df_professores_copy = df_professores[["NContabilistico"]].copy().drop_duplicates()
    df_professores_copy['ValidProfessor'] = 1

    df_merged = df_merged.astype({"NContabilistico": "str"})
    df_professores_copy = df_professores_copy.astype({"NContabilistico": "str"})

    df_merged = pd.merge(df_merged, df_professores_copy, on=["NContabilistico"], how="left", indicator=True)
    matches_professores = len(df_merged[df_merged['_merge'] == 'both'])
    logger.notice(f"Merge PROFESSORES: {matches_professores} Linhas encontradas.")
    df_merged['ValidProfessor'] = np.where(df_merged['_merge'] == 'left_only', 0, 1)
    df_merged = df_merged.drop(columns=['_merge'])

    logger.info(f"Processo de merge concluído. DataFrame final tem {len(df_merged)} linhas.")
    
    # --- LÓGICA DE SEPARAÇÃO ---
    logger.info("A separar os eventos em válidos e inválidos...")
    
    # Condição para um evento ser válido: todas as colunas de validação têm de ser 1
    valid_condition = (
        (df_merged['ValidCourse'] == 1) &
        (df_merged['ValidDisc'] == 1) &
        (df_merged['ValidTurma'] == 1) &
        (df_merged['ValidProfessor'] == 1)
    )

    df_merged_valid_events = df_merged[valid_condition].copy()
    df_merged_invalid_events = df_merged[~valid_condition].copy()

    logger.notice(f"Separação concluída: {len(df_merged_valid_events)} eventos válidos e {len(df_merged_invalid_events)} eventos inválidos.")
    
    return df_merged_valid_events, df_merged_invalid_events


def filter_events_without_module_id_and_student_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra o DataFrame de eventos para manter apenas as linhas onde 'module_id' e 'studentGroup_names' não são nulos.
    """
    # Verifica se a coluna é uma lista e se não está vazia
    df_filtered = df[df['studentGroup_names'].apply(lambda x: x is not None and len(x) > 0)]
    df_filtered = df_filtered.dropna(subset=['module_id'])
    return df_filtered


def save_data_institucion(df: pd.DataFrame, semester: str, ano_prefix: str):
    """
    Filtra, segmenta e guarda os dados dos eventos em ficheiros Excel por instituição
    dentro da subpasta DATA_PROCESS/SCHEDULES_BEST, incluindo o prefixo do ano.
    """
    logger.info("A iniciar a segmentação e gravação de dados por instituição.")
    
    institution_map = {
        'FCS': 'EU',
        'FCST': 'EU',
        'IPAM LISBOA': 'IPAM_LIS',
        'IPAM PORTO': 'IPAM_POR',
        'IADE': 'IADE'
    }
    valid_institutions = list(institution_map.keys())

    if 'Institution' not in df.columns:
        logger.error("A coluna 'Institution' não existe no DataFrame. Não é possível guardar por instituição.")
        return

    valid_mask = df['Institution'].apply(
        lambda x: isinstance(x, list) and len(x) == 1 and x[0] in valid_institutions
    )
    
    df_valid = df[valid_mask].copy()
    df_invalid = df[~valid_mask].copy()

    output_dir = os.path.join("DATA_PROCESS", "SCHEDULES_BEST")
    os.makedirs(output_dir, exist_ok=True)

    if not df_invalid.empty:
        invalid_filename = f"fetch_event_not_valid_{ano_prefix}_{semester}.xlsx"
        invalid_filepath = os.path.join(output_dir, invalid_filename)
        df_invalid.to_excel(invalid_filepath, index=False, sheet_name="Invalid_Events")
        logger.info(f"{len(df_invalid)} eventos inválidos guardados em: {invalid_filepath}")
    else:
        logger.info("Não foram encontrados eventos inválidos.")

    if not df_valid.empty:
        df_valid['Institution_Name'] = df_valid['Institution'].apply(lambda x: x[0])
        df_valid['File_Prefix'] = df_valid['Institution_Name'].map(institution_map)

        for prefix, group_df in df_valid.groupby('File_Prefix'):
            filename = f"fetch_event_{prefix}_{ano_prefix}_{semester}.xlsx"
            filepath = os.path.join(output_dir, filename)
            
            group_df_to_save = group_df.drop(columns=['Institution_Name', 'File_Prefix'])
            
            group_df_to_save.to_excel(filepath, index=False, sheet_name="Viewer_Events")
            logger.info(f"{len(group_df_to_save)} eventos para '{prefix}' guardados em: {filepath}")
    else:
        logger.info("Não foram encontrados eventos válidos para guardar.")

    logger.info("Gravação de dados por instituição concluída.")



def extract_relation_teachers_best(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai e agrega a relação de docentes da BEST para a SHOPIA.
    Para cada combinação única de Disciplina, Turma e Curso, esta função
    agrega os 'NContabilistico' e 'teacher_names' numa lista.
    """
    logger.info("A iniciar a extração e agregação da relação de docentes.")

    # 1. Selecionar apenas as colunas relevantes
    df_best_teachers = df[["CdDisc", "DgTurma", "CdCurso", "NContabilistico", "teacher_names"]].copy()

    # 2. Remover linhas onde as chaves principais ou os dados do professor são nulos
    df_best_teachers.dropna(subset=['CdDisc', 'DgTurma', 'CdCurso', 'NContabilistico', 'teacher_names'], inplace=True)

    # 3. Agrupar pela combinação única de disciplina, turma e curso
    # e agregar os dados dos professores em listas
    aggregation_rules = {
        'NContabilistico': lambda x: sorted(list(x.unique())),
        'teacher_names': lambda x: sorted(list(x.unique()))
    }
    
    df_aggregated = df_best_teachers.groupby(['CdDisc', 'DgTurma', 'CdCurso']).agg(aggregation_rules).reset_index()

    logger.info(f"Agregação concluída. {len(df_aggregated)} relações únicas de aula-docente foram criadas.")

    return df_aggregated
