import os
import lxml.etree as etree
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

def get_docentes(client, logger, suffix: str, estado: str = 'A'):
    """
    Chama o método GetDocentes, filtrando por estado, salva o XML e converte para Excel.
    Recebe o cliente SOAP, um logger, o sufixo para o nome do ficheiro e o estado dos docentes.
    """
    logger.info(f"Iniciando a extração de docentes com estado: '{estado}'")

    try:
        # ATENÇÃO: Credenciais hardcoded. Mover para config.py no futuro.
        p_entrada = f"TpUtil=0;CdUtil=2029;PwdUtil=S1st3m0nl1ne#;Estado={estado}"
        psaida_fields = 'NDocente;Login;Email;NomeCompleto;Estado;CdFaculd;DgFaculd;CdPolo;DgPolo;NContabilistico'
        
        params = {
            'Funcao': 'GetDocentes',
            'NivelComp': 0,
            'Certificado': '',
            'FormatoOutput': 0,
            'PEntrada': p_entrada,
            'PSaida': psaida_fields,
            'Agrupar': '',
            'UseParser': ''
        }
        logger.info(f"Chamando o método 'Execute' para GetDocentes...")
        response = client.service.Execute(**params)

        # --- Verificação de resposta vazia ---
        if not response or "Não foi encontrado nenhum registo" in response:
            logger.warning(f"Nenhum docente encontrado ou a API retornou 'Não foi encontrado nenhum registo.' para o estado '{estado}'.")
            return None

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        xml_filename = f"get_docentes_response_{timestamp}.xml"
        
        xml_dir = "XML_FILES"
        os.makedirs(xml_dir, exist_ok=True)
        xml_filepath = os.path.join(xml_dir, xml_filename)
        
        xml_formatted = etree.fromstring(response.encode('utf-8'))
        xml_pretty_str = etree.tostring(xml_formatted, pretty_print=True).decode('utf-8')

        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_pretty_str)
        logger.info(f"Resposta XML salva em: {xml_filepath}")

        root = ET.fromstring(xml_pretty_str)
        docentes_data = []
        columns = psaida_fields.split(';')
        field_mapping = {f'c{i+1}': col for i, col in enumerate(columns)}

        for resultado in root.findall('.//resultado'):
            # Pular registos que são na verdade mensagens de erro
            if len(resultado) == 1 and resultado.find('c1') is not None and "Não foi encontrado nenhum registo" in resultado.find('c1').text:
                continue
            
            docente = {}
            for xml_field, df_field in field_mapping.items():
                element = resultado.find(xml_field)
                docente[df_field] = element.text.strip() if element is not None and element.text else ''
            docentes_data.append(docente)

        if not docentes_data:
            logger.warning(f"Nenhum docente válido encontrado para o estado '{estado}' após a filtragem.")
            return None

        df = pd.DataFrame(docentes_data)
        logger.info(f"{len(df)} docentes processados.")

        output_dir = "DATA_PROCESS"
        os.makedirs(output_dir, exist_ok=True)
        excel_filename = f"Docentes_{suffix}_Estado_{estado}.xlsx"
        excel_filepath = os.path.join(output_dir, excel_filename)

        df.to_excel(excel_filepath, index=False, sheet_name='Docentes')
        logger.info(f"Arquivo Excel com todos os docentes gerado com sucesso em: {excel_filepath}")

        df_com_ncont = df.dropna(subset=['NContabilistico'])
        df_com_ncont = df_com_ncont[df_com_ncont['NContabilistico'].str.strip() != '']

        if not df_com_ncont.empty:
            excel_filename_ncont = f"Docentes_{suffix}_E_{estado}_NCont_{timestamp}.xlsx"
            excel_filepath_ncont = os.path.join(output_dir, excel_filename_ncont)
            df_com_ncont.to_excel(excel_filepath_ncont, index=False, sheet_name='Docentes_Com_NContabilistico')
            logger.info(f"Arquivo Excel filtrado por NContabilistico gerado com sucesso em: {excel_filepath_ncont}")
        else:
            logger.warning("Nenhum docente com NContabilistico encontrado para guardar no ficheiro filtrado.")

        return df

    except Exception as e:
        logger.error(f"Ocorreu um erro em get_docentes: {e}", exc_info=True)
        return None
