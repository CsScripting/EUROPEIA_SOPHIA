import pandas as pd
import numpy as np
import logging
import os
import ast
import lxml.etree as etree
import xml.etree.ElementTree as ET
from src.core import constants
import config  # Adicionado para aceder ao ID_CERTIFICADO

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
    if 'CdDisc' in df_disciplinas_copy.columns:
        df_disciplinas_copy['CdDisc_SHOPIA'] = df_disciplinas_copy['CdDisc']
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
    df_professores_copy = df_professores[["NContabilistico", "NDocente"]].copy().drop_duplicates()
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

    # Filter DataFrame to Keep Relation Teacher Best

    df_merged_valid_events = extract_relation_teachers_best(df_merged_valid_events)
    df_merged_invalid_events = extract_relation_data_not_map(df_merged_invalid_events)

    logger.notice(f"Separação concluída: {len(df_merged_valid_events)} eventos válidos e {len(df_merged_invalid_events)} eventos inválidos.")
    
    return df_merged_valid_events, df_merged_invalid_events

def merge_nr_contab_n_horarios(df_n_horarios: pd.DataFrame, df_teachers: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:


    logger.info(f"NHORARIOS COM ({len(df_n_horarios)} linhas).")


    # merge PROFESSORES:
    df_teachers_copy = df_teachers[["NDocente","NContabilistico" ]].copy().drop_duplicates()
    df_teachers_copy['ValidTeacher'] = 1


    df_n_horarios = df_n_horarios.rename(columns={"CdDocente": "NDocente"})

    df_n_horarios= df_n_horarios.astype({"NDocente": "str"})
    df_teachers_copy = df_teachers_copy.astype({"NDocente": "str"})
    df_n_horarios = pd.merge(df_n_horarios, df_teachers_copy, on=["NDocente"], how="left", indicator=True)
    matches_professores = len(df_n_horarios[df_n_horarios['_merge'] == 'both'])
    logger.notice(f"Merge PROFESSORES | N_HORARIOS: {matches_professores} Linhas encontradas.")
    df_n_horarios['ValidTeacher'] = np.where(df_n_horarios['_merge'] == 'left_only', 0, 1)
    df_n_horarios = df_n_horarios.drop(columns=['_merge'])

    df_n_horarios_valid = df_n_horarios[df_n_horarios['ValidTeacher'] == 1].copy()
    df_n_horarios_invalid = df_n_horarios[df_n_horarios['ValidTeacher'] == 0].copy()

    logger.info(f"NHORARIOS VALIDOS COM ({len(df_n_horarios_valid)} linhas).")
    logger.info(f"NHORARIOS INVALIDOS COM ({len(df_n_horarios_invalid)} linhas).")

    return df_n_horarios_valid, df_n_horarios_invalid

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
    df_best_teachers = df[["CdDisc_SHOPIA","CdDisc", "DgTurma", "CdCurso", "NContabilistico", "teacher_names", "NDocente"]].copy()

    df_best_teachers["NDocente"] = df_best_teachers["NDocente"].astype(int).astype(str)


    # 3. Agrupar pela combinação única de disciplina, turma e curso
    # e agregar os dados dos professores em listas
    aggregation_rules = {
        'NContabilistico': lambda x: sorted(list(x.unique())),
        'teacher_names': lambda x: sorted(list(x.unique())),
        'NDocente': lambda x: sorted(list(x.unique()))
    }
    
    df_aggregated = df_best_teachers.groupby(['CdDisc',"CdDisc_SHOPIA", 'DgTurma', 'CdCurso']).agg(aggregation_rules).reset_index()

    logger.info(f"Agregação concluída. {len(df_aggregated)} relações únicas de aula-docente foram criadas.")

    return df_aggregated

def extract_relation_data_not_map(df: pd.DataFrame) -> pd.DataFrame:

    # 1. Selecionar apenas as colunas relevantes
    df_best_teachers = df[["CdDisc_SHOPIA","CdDisc", "DgTurma", "CdCurso", "NContabilistico", "teacher_names", "ValidCourse", "ValidDisc", "ValidTurma", "ValidProfessor"]].copy()
    df_best_teachers.drop_duplicates(inplace=True)


    return df_best_teachers


def add_teacher_code_to_horarios_shopia(df_best_teachers: pd.DataFrame, df_horarios_shopia: pd.DataFrame) -> pd.DataFrame:
    """
    Reconcilia os docentes da BEST com os horários da SHOPIA usando as chaves diretas
    e uma limpeza robusta das chaves para garantir a contagem correta.
    """
    logger.info("Iniciando reconciliação com limpeza de chaves robusta.")

    df_horarios_shopia = df_horarios_shopia.rename(columns={"CdDis": "CdDisc",
                                                            "NDocente": "CdDocente"})

    # --- 1. PREPARAÇÃO E LIMPEZA ROBUSTA DAS CHAVES ---

    # Preparar df_horarios_shopia (a nossa base)
    df_analysis = df_horarios_shopia.copy()
    key_cols = ['CdDisc', 'DgTurma']
    for col in key_cols:
        df_analysis[col] = df_analysis[col].fillna('').astype(str).str.strip()
    df_analysis['NHorarios'] = df_analysis.groupby(key_cols)['CdDisc'].transform('size')

    # Preparar df_best_teachers
    df_best_prepared = df_best_teachers.copy()
    
    # Manter o 'CdDisc' original da BEST se existir, renomeando-o
    if 'CdDisc' in df_best_prepared.columns and 'CdDisc_SHOPIA' in df_best_prepared.columns:
        df_best_prepared.rename(columns={'CdDisc': 'CdDisc_BEST'}, inplace=True)
    
    # Usar 'CdDisc_SHOPIA' como a chave de merge, renomeando para 'CdDisc'
    if 'CdDisc_SHOPIA' in df_best_prepared.columns:
        df_best_prepared.rename(columns={'CdDisc_SHOPIA': 'CdDisc'}, inplace=True)
    
    for col in key_cols:
        if col in df_best_prepared.columns:
            df_best_prepared[col] = df_best_prepared[col].fillna('').astype(str).str.strip()

    # Converter a coluna de professores para lista e contar DSD
    def safe_list_eval(val):
        try:
            return ast.literal_eval(val) if isinstance(val, str) else (val if isinstance(val, list) else [])
        except (ValueError, SyntaxError):
            return [val] if val else []
    
    df_best_prepared['NDocente_list'] = df_best_prepared['NDocente'].apply(safe_list_eval)
    df_best_prepared['DSD'] = df_best_prepared['NDocente_list'].apply(len)
    
    # Selecionar colunas da BEST para o merge
    df_best_to_merge = df_best_prepared[key_cols + ['DSD', 'NDocente_list']].drop_duplicates(subset=key_cols)

    # --- 2. MERGE E CÁLCULO DE STATUS ---
    df_merged = pd.merge(df_analysis, df_best_to_merge, on=key_cols, how='left')
    df_merged['DSD'] = df_merged['DSD'].fillna(0).astype(int)
    
    conditions = [
        (df_merged['DSD'] > df_merged['NHorarios']),
        (df_merged['DSD'] < df_merged['NHorarios']),
        (df_merged['DSD'] == df_merged['NHorarios']),
    ]
    choices = ['DSD>NHORARIO', 'DSD<NHORARIO', 'DSD=NHORARIO']
    df_merged['InfoDSD'] = np.select(conditions, choices, default='NO_BEST_DATA')

    # --- 3. RECONCILIAÇÃO DOS PROFESSORES ---
    df_merged['NovoProf'] = pd.NA
    
    for key, group in df_merged.groupby(key_cols):
        if group['InfoDSD'].iloc[0] == 'NO_BEST_DATA':
            continue
            
        professores_best = group['NDocente_list'].iloc[0] if isinstance(group['NDocente_list'].iloc[0], list) else []
        professores_best_set = set(map(str, professores_best))
        professores_shopia_atuais = set(group['CdDocente'].astype(str).dropna().unique())
        professores_a_adicionar = sorted(list(professores_best_set - professores_shopia_atuais))
        
        idx_prof_a_adicionar = 0
        for index, row in group.iterrows():
            docente_atual = str(row['CdDocente'])
            
            if docente_atual in professores_best_set:
                df_merged.loc[index, 'NovoProf'] = 'Keep'
            else:
                if idx_prof_a_adicionar < len(professores_a_adicionar):
                    df_merged.loc[index, 'NovoProf'] = professores_a_adicionar[idx_prof_a_adicionar]
                    idx_prof_a_adicionar += 1
                else:
                    df_merged.loc[index, 'NovoProf'] = ''

    # --- 4. LIMPEZA FINAL ---
    # df_final = df_merged.drop(columns=['NDocente_list'])
    df_final = df_merged
    df_final.rename(columns={"DSD": "DSD_NR_BEST", 
                             "NDocente_list": "DSD_BEST"}, inplace=True)
    logger.info("Processo de reconciliação (chaves diretas e limpas) concluído.")
    return df_final


def iterate_relation_teachers_best_and_update_horarios_shopia(
    df_best_teachers: pd.DataFrame, 
    client, 
    logger,
    df_periodos: pd.DataFrame,
    ano_lectivo: int, 
    flag_semestre: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Usa a relação da BEST para consultar os horários na SHOPIA, atualizando
    o DataFrame da BEST com o status e retornando os horários encontrados.
    """
    logger.info("Iniciando a consulta de horários na SHOPIA com base na relação da BEST.")

    # 1. Determinar os períodos a consultar com base na flag do semestre
    mapa_periodos = {
        1: ["Anual", "1º semestre", "1º trimestre", "2º trimestre"],
        2: ["Anual", "2º semestre", "3º trimestre", "4º trimestre"]
    }
    nomes_periodos_a_consultar = mapa_periodos.get(flag_semestre, [])
    if not nomes_periodos_a_consultar:
        logger.error(f"Flag de semestre inválida: {flag_semestre}. Use 1 ou 2.")
        return df_best_teachers, pd.DataFrame()

    periodos_a_consultar_df = df_periodos[df_periodos['DgPeriodo'].isin(nomes_periodos_a_consultar)]
    periodos_ids = periodos_a_consultar_df['CdPeriodo'].tolist()
    logger.info(f"Períodos a consultar para o semestre {flag_semestre}: {nomes_periodos_a_consultar} (IDs: {periodos_ids})")

    # 2. Inicializar resultados
    df_best_teachers_updated = df_best_teachers.copy()
    df_best_teachers_updated['NHorario'] = 0
    horarios_encontrados_lista = []

    # 3. Iterar sobre cada relação da BEST e consultar a SHOPIA
    for index, row in df_best_teachers_updated.iterrows():
        cd_curso = row['CdCurso']
        cd_disc_shopia = row['CdDisc_SHOPIA']
        horario_encontrado_para_esta_aula = False

        for periodo_id in periodos_ids:
            try:
                p_entrada = f"CdCurso={cd_curso};CdCadeira={cd_disc_shopia};CdAnoLect={ano_lectivo};CdPeriodo={periodo_id}"
                params = {
                    'Funcao': 'GetTurmas',
                    'NivelComp': 0,
                    'Certificado': '',
                    'FormatoOutput': 0,
                    'PEntrada': p_entrada,
                    'PSaida': 'CdTurma;DgTurma;NumVagas',
                    'Agrupar': '',
                    'UseParser': ''
                }
                
                response = client.service.Execute(**params)

                if response and "Não foi encontrado nenhum registo" not in response:
                    horario_encontrado_para_esta_aula = True
                    
                    root = ET.fromstring(response.encode('utf-8'))
                    for resultado in root.findall('.//resultado'):
                        horarios_encontrados_lista.append({
                            'CdTurma': resultado.find('c1').text if resultado.find('c1') is not None else '',
                            'DgTurma': resultado.find('c2').text if resultado.find('c2') is not None else '',
                            'NumVagas': resultado.find('c3').text if resultado.find('c3') is not None else '',
                            'CdCurso': cd_curso, # Adiciona o CdCurso para contexto
                            'CdDisc_SHOPIA': cd_disc_shopia # Adiciona a disciplina para contexto
                        })
            
            except Exception as e:
                logger.error(f"Erro ao consultar GetTurmas para a aula {cd_disc_shopia} no período {periodo_id}: {e}")
                continue
        
        # Atualizar a coluna NHorario se algum horário foi encontrado
        if horario_encontrado_para_esta_aula:
            df_best_teachers_updated.loc[index, 'NHorario'] = 1

    # 4. Criar o DataFrame final de horários
    df_horarios_final = pd.DataFrame(horarios_encontrados_lista)
    if not df_horarios_final.empty:
        df_horarios_final.drop_duplicates(inplace=True)
        logger.info(f"Consulta finalizada. {len(df_horarios_final)} horários únicos encontrados na SHOPIA.")
    else:
        logger.warning("Nenhum horário foi encontrado na SHOPIA para as relações da BEST fornecidas.")

    return df_best_teachers_updated, df_horarios_final


def edit_linha_horario(client, logger, df_horarios_shopia: pd.DataFrame, ano_lectivo: int) -> pd.DataFrame:
    """
    Atualiza os horários na SHOPIA utilizando o endpoint EditLinhaHorario.
    """
    logger.info(f"--- INÍCIO DA ATUALIZAÇÃO DE HORÁRIOS NA SHOPIA ---")
    total_rows = len(df_horarios_shopia)
    success_count = 0
    error_count = 0

    # Filtra as linhas que precisam de atualização
    df_to_update = df_horarios_shopia[df_horarios_shopia['NovoProf'] != 'Keep'].copy()
    logger.info(f"Encontradas {len(df_to_update)} linhas para atualizar (excluindo 'Keep').")


    for index, row in df_to_update.iterrows():
        # Ignorar linhas onde 'NovoProf' está vazio, pois não há docente para atribuir
        if pd.isna(row['NovoProf']) or row['NovoProf'] == '':
            logger.warning(f"Linha {index + 1}: 'NovoProf' está vazio. A saltar a atualização.")
            continue
        try:
            p_entrada = (
                f"TpUtil=0;CdUtil=2029;PwdUtil=S1st3m0nl1ne#;"
                f"CdCurso=0;"
                f"CdDisciplina={row['CdDisc']};"  # Usar CdDisc que é a chave
                f"NHorario={row['CdTurma']};"
                f"AnoLectivo={ano_lectivo};"
                f"CdPeriodo={row['CdPeriodo']};"
                f"AntigoDiaSemana={row['DiaSemana']};"
                f"AntigoHoraIni={row['HoraIni']};"
                f"AntigoMinuIni={row['MinutoIni']};"
                f"NovoDiaSemana={row['DiaSemana']};"
                f"NovoCdRegime={row['CdRegime']};"
                f"NovoHoraIni={row['HoraIni']};"
                f"NovoMinuIni={row['MinutoIni']};"
                f"NovoHoraFim={row['HoraFim']};"
                f"NovoMinuFim={row['MinutoFim']};"
                f"NovoCdDocente={row['NovoProf']}" # Usar o NovoProf que foi calculado
            )

            params = {
                'Funcao': 'EditLinhaHorario',
                'NivelComp': 0,
                'Certificado': config.ID_CERTIFICADO,
                'FormatoOutput': 0,
                'PEntrada': p_entrada,
                'PSaida': 'Retorno',
                'Agrupar': '',
                'UseParser': ''
            }
            
            logger.debug(f"A chamar 'Execute' para a linha {index + 1}/{total_rows} com PEntrada: {p_entrada}")
            response = client.service.Execute(**params)

            # Adicionar a resposta ao DataFrame para análise posterior
            df_horarios_shopia.loc[index, 'UpdateResponse'] = response

            if response and "sucesso" in str(response).lower():
                logger.info(f"Linha {index + 1}: Horário atualizado com sucesso. Resposta: {response}")
                success_count += 1
            else:
                logger.error(f"Linha {index + 1}: Erro ao atualizar horário. Resposta: {response}")
                error_count += 1

        except Exception as e:
            logger.error(f"Linha {index + 1}: Exceção ao chamar o serviço SOAP: {e}", exc_info=True)
            df_horarios_shopia.loc[index, 'UpdateResponse'] = f"EXCEPTION: {e}"
            error_count += 1

    logger.notice(f"--- FIM DA ATUALIZAÇÃO DE HORÁRIOS ---")
    logger.notice(f"Resultados: {success_count} sucessos, {error_count} erros de um total de {len(df_to_update)} linhas a atualizar.")

    return df_horarios_shopia
