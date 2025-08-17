import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import config

def get_cursos(client, logger, suffix):
    """
    Chama o método GetCursos com todos os campos de saída, 
    salva o XML e converte para um arquivo Excel detalhado.
    Recebe o cliente SOAP já inicializado, um logger e um sufixo para o nome do arquivo.
    """
    try:
        # --- 1. Definição completa dos parâmetros de saída ---
        output_fields = [
            'CdCurso', 'NmCurso', 'AbrCurso', 'CdTpCurso', 'TpCurso',
            'NAnos', 'CdPlanoDef', 'Estado', 'SaidasProfiss', 'RequisitosAcesso',
            'CursoTpPosGrad', 'CdPolo', 'DgPolo', 'CdFaculd', 'DgFaculd',
            'NmCursoIng', 'CdTpCursoIntermedio', 'DgTpCursoIntermedio',
            'CdOferta', 'DgOferta', 'AudithCreated', 'AudithUpdated',
            'EctsDiploma', 'CodigoCRM', 'NmComercial', 'CdLinguaMinistrado'
        ]
        
        # --- 2. Chamada da Função GetCursos ---
        params = {
            'Funcao': 'GetCursos',
            'NivelComp': 0,
            'Certificado': '',
            'FormatoOutput': 0,
            'PEntrada': '',
            'PSaida': ';'.join(output_fields),
            'Agrupar': '',
            'UseParser': ''
        }
        logger.info("Chamando o método 'Execute' para GetCursos com todos os campos...")
        response = client.service.Execute(**params)

        # --- Verificação de resposta vazia ---
        if "Não foi encontrado nenhum registo" in response:
            logger.warning("A API retornou 'Não foi encontrado nenhum registo.' para GetCursos. Nenhum dado será salvo.")
            return False

        # --- 3. Salvar a Resposta XML ---
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        xml_filename = f"get_cursos_response_{timestamp}.xml"
        xml_filepath = os.path.join("XML_FILES", xml_filename)
        
        xml_formatted = etree.fromstring(response.encode('utf-8'))
        xml_pretty_str = etree.tostring(xml_formatted, pretty_print=True).decode('utf-8')

        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Resposta XML salva em: {xml_filepath}")

        # --- 4. Parse do XML e Conversão para DataFrame ---
        root = ET.fromstring(xml_pretty_str)
        cursos_data = []
        
        field_mapping = {f'c{i+1}': field_name for i, field_name in enumerate(output_fields)}

        for resultado in root.findall('.//resultado'):
            # Pular registos que são na verdade mensagens de erro
            if len(resultado) == 1 and resultado.find('c1') is not None and "Não foi encontrado nenhum registo" in resultado.find('c1').text:
                continue

            curso = {}
            for xml_field, df_field in field_mapping.items():
                element = resultado.find(xml_field)
                curso[df_field] = element.text.strip() if element is not None and element.text else ''
            
            curso['Estado_Descricao'] = 'Ativo' if curso.get('Estado') == 'A' else 'Inativo'
            try:
                curso['NAnos_Num'] = int(curso.get('NAnos')) if curso.get('NAnos') else 0
            except (ValueError, TypeError):
                curso['NAnos_Num'] = 0

            cursos_data.append(curso)

        if not cursos_data:
            logger.warning("Nenhum curso válido encontrado na resposta do serviço após a filtragem.")
            return False

        df = pd.DataFrame(cursos_data)
        logger.info(f"{len(df)} cursos processados.")

        # --- 5. Salvar DataFrame em Excel com Múltiplas Abas ---
        # Usar o caminho DATA_PROCESS/INSTITUTION/DATA_SOPHIA
        data_process_dir = "DATA_PROCESS"
        institution_dir = os.path.join(data_process_dir, suffix)  # Usa o sufixo da instituição (ex: EU para QA)
        data_sophia_dir = os.path.join(institution_dir, "DATA_SOPHIA")
        os.makedirs(data_sophia_dir, exist_ok=True)

        excel_filename = f"Cursos_{suffix}.xlsx"
        excel_filepath = os.path.join(data_sophia_dir, excel_filename)

        with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Todos_Cursos', index=False, freeze_panes=(1,0))
            df[df['Estado'] == 'A'].to_excel(writer, sheet_name='Cursos_Ativos', index=False, freeze_panes=(1,0))
            
            if 'TpCurso' in df.columns:
                stats_tipo = df.groupby('TpCurso').agg(
                    Total_Cursos=('CdCurso', 'count'),
                    Cursos_Ativos=('Estado', lambda x: (x == 'A').sum())
                ).reset_index()
                stats_tipo['Cursos_Inativos'] = stats_tipo['Total_Cursos'] - stats_tipo['Cursos_Ativos']
                stats_tipo.to_excel(writer, sheet_name='Estatisticas_Tipo_Curso', index=False, freeze_panes=(1,0))

            if 'NAnos_Num' in df.columns and df['NAnos_Num'].sum() > 0:
                stats_duracao = df[df['NAnos_Num'] > 0].groupby('NAnos_Num').agg(
                    Total_Cursos=('CdCurso', 'count'),
                    Cursos_Ativos=('Estado', lambda x: (x == 'A').sum())
                ).reset_index()
                stats_duracao.to_excel(writer, sheet_name='Estatisticas_Duracao', index=False, freeze_panes=(1,0))
        
        logger.info(f"Arquivo Excel detalhado gerado com sucesso em: {excel_filepath}")
        return True

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_cursos: {e}", exc_info=True)
        return False
