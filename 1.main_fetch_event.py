# main_event.py - Script for Fetching, Processing, and Saving BWP Event Data to Viewer Format
import logging
import sys
import os
import pandas as pd
import datetime
from src.utils.setup_logging import setup_colored_logging, redirect_stdout_stderr_to_log



try:
    from src.auth.identity_server import get_access_token
    from src.api.client import ApiClient
    from src.core.event_processor import fetch_existing_events, process_raw_events_df, create_column_institucion_info_and_id_mod, create_column_institucion_info_by_module_code
    from src.core.event_processor_europeia import filter_events_without_module_id_and_student_groups, save_data_institucion
    
    import config
except ImportError as e:
    logging.error(f"Failed to import necessary modules for main_fetchevent.py: {e}")
    sys.exit(1)

# --- Setup Application-Wide Logging ---
log_dir = "LOGS"
log_file_name = f"1.main_fetch_event_{config.INSTITUTION}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)

setup_colored_logging(log_file_path)
redirect_stdout_stderr_to_log()

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])

# --- Import config ---
import config

#VARIABLES SCRIPT
TARGET_ACADEMIC_YEAR_NAME = "2025/2026 - 1º Semestre"
SEMESTER = "PRIMER" ## ID 9
ANO_PREFIX = "2025"
OUTPUT_VIEWER_EVENTS_EXCEL_FILENAME = f'fetch_event_{ANO_PREFIX}_{SEMESTER}.xlsx'

# --- Setup Output Directories ---
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

INSTITUTION_DIR = os.path.join(DATA_PROCESS_DIR, FILE_PREFIX)  # Usa o sufixo da instituição (ex: EU para QA)
DATA_BEST_DIR = os.path.join(INSTITUTION_DIR, "DATA_BEST")
# Criar estrutura de diretórios
os.makedirs(DATA_BEST_DIR, exist_ok=True)

def run_event_fetching_and_processing():
    """Main function to orchestrate fetching, processing to viewer DTO, and saving event data."""
    logger.notice("Starting the BWP event data fetching and processing workflow...")

    # 1. Get Access Token
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to obtain access token. Halting BWP event processing.")
        return

    # 2. Initialize API Client
    try:
        api_client = ApiClient(access_token)
    except ValueError as e:
        logger.error(f"Failed to initialize API client: {e}")
        return

    # 3. Fetch Existing Raw Events (BWP)
    raw_events_df = fetch_existing_events(api_client, TARGET_ACADEMIC_YEAR_NAME)
    if raw_events_df is None or raw_events_df.empty:
        logger.error("Fetching raw events resulted in an empty or None DataFrame. Halting.")
        return
    logger.info(f"Successfully fetched {len(raw_events_df)} raw events from BWP.")

    # 4. Process Raw Events into ViewerDTO format
    # ADD CdDisc FROM Module_Code 
    viewer_events_df = process_raw_events_df(raw_events_df)
    if viewer_events_df is None or viewer_events_df.empty:
        logger.error("Processing raw events resulted in an empty or None DataFrame. Halting.")
        return
    logger.info(f"Successfully processed {len(viewer_events_df)} events into ViewerDTO format.")

    # 5. Create Institution Column (POR DESIGNAÇÂO CURSO)
    # viewer_events_df = create_column_institucion_info_and_id_mod(viewer_events_df)

    # 5.1 Create Institution Column Acronyms by module code (POR CODIGO DISCIPLINA)
    viewer_events_df = create_column_institucion_info_by_module_code(viewer_events_df)

    # 6. Filter Events
    viewer_events_df = filter_events_without_module_id_and_student_groups(viewer_events_df)

    # 7. Save the general, consolidated file first
    logger.info("=== BWP EVENT PROCESSING: Saving consolidated ViewerDTO events to Excel ===")
    try:
        # Criar diretório para a instituição dentro de DATA_BEST
        output_path = os.path.join(DATA_BEST_DIR, OUTPUT_VIEWER_EVENTS_EXCEL_FILENAME)
        
        viewer_events_df.to_excel(output_path, sheet_name='Viewer_Events', index=False, freeze_panes=(1,0))
        logger.info(f"Successfully exported consolidated ViewerDTO events data to {output_path}")

    except Exception as e:
        logger.error(f"Failed to export consolidated ViewerDTO events data to Excel: {e}", exc_info=True)

    # 8. Save Data Segmented by Institution
    logger.info("=== BWP EVENT PROCESSING: Saving segmented data by institution ===")
    try:
        save_data_institucion(viewer_events_df, SEMESTER, ANO_PREFIX,DATA_BEST_DIR)
    except Exception as e:
        logger.error(f"Failed to save segmented event data: {e}", exc_info=True)

    logger.notice("--- BWP event data fetching and processing workflow finished. ---")

if __name__ == "__main__":
    run_event_fetching_and_processing()
