import logging
import pandas as pd
import os
import dataclasses # Required for asdict
from typing import Optional, List, Any # Updated typing imports

try:
    import config
    from src.core import data_processor # To get academic_year_id
    from src.core.data_processor import _extract_and_concat, _extract_nested_and_concat # Import helpers
    from src.core import constants # For any event-related constants if needed in future
    
    from src.api.client import ApiClient
    from src.entities.event.dto import EventApiDTO, EventViewerDTO
    
except ModuleNotFoundError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) # Add project root to path
    import config
    from src.core import data_processor
    from src.core.data_processor import _extract_and_concat, _extract_nested_and_concat # Import helpers
    from src.core import constants 
    
    from src.api.client import ApiClient
    from src.entities.event.dto import EventApiDTO, EventViewerDTO
    
   

logger = logging.getLogger(__name__)

# Helper function to safely get an attribute from an object
def _safe_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    if obj is None:
        return default
    return getattr(obj, attr, default)

# Helper function to concatenate attributes from a list of DTOs
def _concat_attributes(dto_list: List[Any], attributes: List[str], separator: str = ',') -> dict[str, Optional[str]]:
    concatenated_values: dict[str, list[str]] = {attr: [] for attr in attributes}
    if not dto_list:
        return {attr: None for attr in attributes}

    for dto_item in dto_list:
        if dto_item:
            for attr in attributes:
                value = _safe_getattr(dto_item, attr)
                if value is not None:
                    concatenated_values[attr].append(str(value))
    
    return {
        attr: separator.join(values_list) if values_list else None 
        for attr, values_list in concatenated_values.items()
    }

# NEW HELPER FUNCTION: Collects attributes into a list of unique, sorted strings
def _collect_attributes_as_list(dto_list: List[Any], attributes: List[str]) -> dict[str, Optional[List[str]]]:
    """
    Extracts specified attributes from a list of DTOs, returning them as a dictionary
    where each key maps to a sorted list of unique string values.
    """
    collected_values: dict[str, set[str]] = {attr: set() for attr in attributes}
    if not dto_list:
        return {attr: None for attr in attributes}

    for dto_item in dto_list:
        if dto_item:
            for attr in attributes:
                value = _safe_getattr(dto_item, attr)
                if value is not None:
                    collected_values[attr].add(str(value))
    
    return {
        attr: sorted(list(value_set)) if value_set else None 
        for attr, value_set in collected_values.items()
    }


# NEW HELPER FUNCTION: Collects all attributes, preserving order and duplicates
def _collect_attributes_preserving_order(dto_list: List[Any], attributes: List[str]) -> dict[str, Optional[List[str]]]:
    """
    Extracts specified attributes from a list of DTOs, returning them as a dictionary
    where each key maps to a list of string values, preserving duplicates and order.
    """
    collected_values: dict[str, list[str]] = {attr: [] for attr in attributes}
    if not dto_list:
        return {attr: None for attr in attributes}

    for dto_item in dto_list:
        if dto_item:
            for attr in attributes:
                value = _safe_getattr(dto_item, attr)
                # Append value as string, or a placeholder if it's None
                collected_values[attr].append(str(value) if value is not None else '')
    
    return {
        attr: values_list if any(v is not None for v in values_list) else None 
        for attr, values_list in collected_values.items()
    }


def fetch_existing_events(api_client: ApiClient, academic_year_name: str) -> pd.DataFrame | None:
    """
    Fetches existing events from the API for a given academic year.
    MODIFIED: This function NO LONGER saves the raw data to Excel.
    It returns a raw DataFrame of events, or None/empty DataFrame on error/no data.
    """
    logger.info(f"--- Starting to fetch existing events for Academic Year: '{academic_year_name}' ---")

    logger.info(f"Fetching ID for Academic Year: '{academic_year_name}'")
    academic_year_id = data_processor.fetch_academic_year_id_by_name(api_client, academic_year_name)

    if not academic_year_id:
        logger.error(f"Could not find Academic Year ID for name '{academic_year_name}'. Cannot fetch events.")
        return None
    logger.info(f"Found Academic Year ID: {academic_year_id}")

    search_payload = {
        "filters": [
            {
                "type": 0, 
                "path": "AcademicYear.Id", 
                "Value": academic_year_id 
            },
            {   
                "and": "true",
                "type": 0, 
                "path": "EventType.Name", 
                "Value": "Aulas"
            },
            
            
        ],
        "paging": { "pageSize": 2000, "pageNumber": 1 } 
    }
    endpoint = config.EVENTS_SEARCH_ENDPOINT

    try:
        logger.info(f"Attempting to search for Events using POST to: {endpoint} with payload: {search_payload}")
        response = api_client.search_data(endpoint, json_payload=search_payload)

        if not response:
            logger.warning(f"No response received from Events search endpoint for Academic Year ID: {academic_year_id}")
            return pd.DataFrame() 

        if isinstance(response, dict) and 'data' in response and \
           isinstance(response['data'], dict) and 'data' in response['data'] and \
           isinstance(response['data']['data'], list):
            
            events_list = response['data']['data']
            if not events_list:
                logger.info(f"No events found for Academic Year ID: {academic_year_id}.")
                return pd.DataFrame() 

            logger.notice(f"Successfully fetched {len(events_list)} raw events for Academic Year ID: {academic_year_id}.")
            raw_events_df = pd.DataFrame(events_list)
            # Removed Excel export of raw_events_df from here
            return raw_events_df
        else:
            logger.warning(f"Received unexpected format from Events search endpoint for Academic Year ID: {academic_year_id}.")
            logger.debug(f"Received data: {response}")
            return pd.DataFrame() 

    except Exception as e:
        logger.error(f"Failed to fetch or process existing events for Academic Year '{academic_year_name}' (ID: {academic_year_id}): {e}")
        return None

def process_raw_events_df(raw_events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes the raw events DataFrame by converting each raw event dictionary 
    into an EventApiDTO, and then directly into an EventViewerDTO 
    for a flattened, view-oriented DataFrame.
    MODIFIED to store multi-value fields as lists instead of comma-separated strings.
    """
    if raw_events_df.empty:
        logger.info("Raw events DataFrame is empty. Returning empty DataFrame.")
        return pd.DataFrame()

    logger.info(f"Processing {len(raw_events_df)} raw events into EventViewerDTOs...")
    
    processed_event_view_dtos = []
    raw_event_dictionaries = raw_events_df.to_dict(orient='records')

    for i, event_dict in enumerate(raw_event_dictionaries):
        try:
            # Step 1: Convert raw dict to EventApiDTO
            event_api_dto = EventApiDTO.from_dict(event_dict)
            
            # Step 2: Populate EventViewerDTO directly from EventApiDTO
            viewer_dto = EventViewerDTO()

            # Direct fields from EventApiDTO
            
            viewer_dto.id = event_api_dto.id
            viewer_dto.name = event_api_dto.name
            viewer_dto.startTime = event_api_dto.startTime
            viewer_dto.endTime = event_api_dto.endTime
            viewer_dto.duration = event_api_dto.duration
            viewer_dto.day = event_api_dto.day 
            viewer_dto.wlsSectionName = event_api_dto.wlsSectionName
            viewer_dto.wlsSectionConnector = event_api_dto.wlsSectionConnector 
            viewer_dto.unit = event_api_dto.unit
            viewer_dto.annotations = event_api_dto.annotations
            viewer_dto.numStudents = event_api_dto.numStudents
            
            
            viewer_dto.createdBy = event_api_dto.createdBy
            viewer_dto.lastModifiedBy = event_api_dto.lastModifiedBy
            viewer_dto.lastModifiedAt = event_api_dto.lastModifiedAt
            viewer_dto.createdAt = event_api_dto.createdAt

            # EventType from event_api_dto.eventType (which is an EventTypeDTO)
            if event_api_dto.eventType:
                viewer_dto.eventType_id = _safe_getattr(event_api_dto.eventType, 'id')
                viewer_dto.eventType_name = _safe_getattr(event_api_dto.eventType, 'name')

            # Module from event_api_dto.module (which is a ModuleDTO)
            if event_api_dto.module:
                viewer_dto.module_id = _safe_getattr(event_api_dto.module, 'id') 
                viewer_dto.module_name = _safe_getattr(event_api_dto.module, 'name')
                viewer_dto.module_code = _safe_getattr(event_api_dto.module, 'code')
                viewer_dto.module_acronym = _safe_getattr(event_api_dto.module, 'acronym')

            # AcademicYear from event_api_dto.academicYear (which is an AcademicYearDTO)
            if event_api_dto.academicYear:
                viewer_dto.academicYear_id = _safe_getattr(event_api_dto.academicYear, 'id')
                viewer_dto.academicYear_name = _safe_getattr(event_api_dto.academicYear, 'name')
            
            # Weeks (List[WeekDTO]) from event_api_dto.weeks
            week_attrs = _collect_attributes_preserving_order(
                _safe_getattr(event_api_dto, 'weeks'), 
                attributes=['id', 'startDate']
            )
            viewer_dto.week_ids = week_attrs.get('id')
            
            # Process week_startDates to store only date part, now as a list
            raw_start_dates_list = week_attrs.get('startDate')
            if raw_start_dates_list:
                date_parts = {date_str[:10] for date_str in raw_start_dates_list if len(date_str) >= 10}
                viewer_dto.week_startDates = sorted(list(date_parts))
            else:
                viewer_dto.week_startDates = None

            # Classrooms (List[ClassroomDTO]) from event_api_dto.classrooms
            classroom_attrs = _collect_attributes_preserving_order(
                _safe_getattr(event_api_dto, 'classrooms'),
                attributes=['id', 'name', 'code']
            )
            viewer_dto.classroom_ids = classroom_attrs.get('id')
            viewer_dto.classroom_names = classroom_attrs.get('name')
            viewer_dto.classroom_codes = classroom_attrs.get('code')

            # StudentGroups (List[StudentGroupDTO]) from event_api_dto.studentGroups
            sg_attrs = _collect_attributes_preserving_order(
                _safe_getattr(event_api_dto, 'studentGroups'),
                attributes=['id', 'name', 'code']
            )
            viewer_dto.studentGroup_ids = sg_attrs.get('id')
            viewer_dto.studentGroup_names = sg_attrs.get('name')
            viewer_dto.studentGroup_codes = sg_attrs.get('code')

            # --- CORRECTED: Extract Curricular Plan and Course Information (1-to-1 mapping) ---
            plan_ids, plan_names, plan_codes = [], [], []
            course_ids, course_names, course_codes, course_acronyms = [], [], [], []

            if event_api_dto.studentGroups:
                for sg_dto in event_api_dto.studentGroups:
                    # Always append to plan lists for every student group
                    if sg_dto and sg_dto.curricularPlan:
                        plan = sg_dto.curricularPlan
                        plan_ids.append(str(_safe_getattr(plan, 'id', '')))
                        plan_names.append(str(_safe_getattr(plan, 'name', '')))
                        plan_codes.append(str(_safe_getattr(plan, 'code', '')))

                        # If plan exists, check for course and append, else append placeholder
                        if plan.course:
                            course = plan.course
                            course_ids.append(str(_safe_getattr(course, 'id', '')))
                            course_names.append(str(_safe_getattr(course, 'name', '')))
                            course_codes.append(str(_safe_getattr(course, 'code', '')))
                            course_acronyms.append(str(_safe_getattr(course, 'acronym', '')))
                        else:
                            # Append placeholders to maintain list alignment
                            course_ids.append(None)
                            course_names.append(None)
                            course_codes.append(None)
                            course_acronyms.append(None)
                    else:
                        # Append placeholders if a student group has no plan
                        plan_ids.append(None)
                        plan_names.append(None)
                        plan_codes.append(None)
                        course_ids.append(None)
                        course_names.append(None)
                        course_codes.append(None)
                        course_acronyms.append(None)
            
            # CORRECTED: Assign lists directly to preserve order and duplicates
            viewer_dto.plan_ids = plan_ids if plan_ids else None
            viewer_dto.plan_names = plan_names if plan_names else None
            viewer_dto.plan_codes = plan_codes if plan_codes else None

            viewer_dto.course_ids = course_ids if course_ids else None
            viewer_dto.course_names = course_names if course_names else None
            viewer_dto.course_codes = course_codes if course_codes else None
            viewer_dto.course_acronyms = course_acronyms if course_acronyms else None
            
            # Teachers (List[TeacherDTO]) from event_api_dto.teachers
            teacher_attrs = _collect_attributes_preserving_order(
                _safe_getattr(event_api_dto, 'teachers'),
                attributes=['id', 'name', 'code']
            )
            viewer_dto.teacher_ids = teacher_attrs.get('id')
            viewer_dto.teacher_names = teacher_attrs.get('name')
            viewer_dto.teacher_codes = teacher_attrs.get('code')

            # Typologies (List[TypologyDTO]) from event_api_dto.typologies
            typology_attrs = _collect_attributes_preserving_order(
                _safe_getattr(event_api_dto, 'typologies'),
                attributes=['id', 'name']
            )
            viewer_dto.typology_ids = typology_attrs.get('id') 
            viewer_dto.typology_names = typology_attrs.get('name')

            processed_event_view_dtos.append(dataclasses.asdict(viewer_dto))

        except ValueError as ve: 
            logger.error(f"ValueError processing event at index {i} (ID: {event_dict.get('id', 'N/A')}): {ve}. Skipping this event.")
        except Exception as e:
            logger.error(f"Unexpected error processing event at index {i} (ID: {event_dict.get('id', 'N/A')}): {e}. Skipping this event.", exc_info=True)
            
    if not processed_event_view_dtos:
        logger.warning("No events were successfully processed into EventViewerDTOs.")
        return pd.DataFrame()

    processed_df = pd.DataFrame(processed_event_view_dtos)
    logger.info(f"Finished processing events into EventViewerDTOs. Resulting DataFrame has {len(processed_df)} rows and {len(processed_df.columns)} columns.")
    
    rename_map = {
        "id": constants.EVENT_ID,
        "name": constants.EVENT_NAME,
    }
    
    existing_columns_to_rename = {k: v for k, v in rename_map.items() if k in processed_df.columns}
    if existing_columns_to_rename:
        processed_df.rename(columns=existing_columns_to_rename, inplace=True)
        logger.info(f"Renamed columns for compatibility with identify_event_operations: {existing_columns_to_rename}")
    else:
        logger.info("No columns needed renaming for identify_event_operations based on current map and DataFrame columns.")

    # --- Adicionar coluna CdDisc a partir de module_code ---
    if 'module_code' in processed_df.columns:
        logger.info("Creating 'CdDisc' column from 'module_code'.")
        # Garante que a coluna é do tipo string para usar o acessador .str
        processed_df['module_code'] = processed_df['module_code'].astype(str)
        
        # Faz o split no primeiro '-', e pega a última parte do resultado.
        # .str[-1] pega o último elemento, que será a parte direita ou a string inteira se não houver '-'.
        processed_df['CdDisc'] = processed_df['module_code'].str.split('-', n=1).str[-1].str.strip()
        logger.info("Successfully created 'CdDisc' column.")
    else:
        logger.warning("'module_code' column not found, cannot create 'CdDisc' column.")

    return processed_df

def identify_event_operations(final_wls_df: pd.DataFrame, existing_events_df: pd.DataFrame, semester: str,
                              output_event_operations_excel_filename: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compares WLSection data (final_wls_df) with existing Event data (existing_events_df)
    to identify matched events, events to insert, events to delete, WLSections with incomplete keys, and events with incomplete keys.

    Args:
        final_wls_df: DataFrame containing processed WLSection data.
                      Expected columns for matching: constants.MODULE_ID, constants.TYPOLOGY_IDS, constants.WLS_SECTION_CONECTOR.
                      It should also contain constants.TEACHER_IDS and constants.STUDENT_GROUP_IDS for comparison.
        existing_events_df: DataFrame containing processed existing Event data (now from EventViewerDTO).
                            Expected columns for matching: constants.MODULE_ID, constants.TYPOLOGY_IDS, constants.WLS_SECTION_CONECTOR.
                            It should also contain constants.TEACHER_IDS and constants.STUDENT_GROUP_IDS for comparison.

    Returns:
        A tuple containing five DataFrames:
        - df_matched_event: Events from existing_events_df that have a match in final_wls_df (using rows with complete keys from both).
                          This DataFrame will include the original columns from both sources (suffixed with '_event' and '_wls' for non-key columns)
                          and four additional columns:
                            - teacher_ids_to_remove: IDs in event's teacher_ids not in WLS's teacher_ids.
                            - teacher_ids_to_add: IDs in WLS's teacher_ids not in event's teacher_ids.
                            - studentGroup_ids_to_remove: IDs in event's studentGroup_ids not in WLS's studentGroup_ids.
                            - studentGroup_ids_to_add: IDs in WLS's studentGroup_ids not in event's studentGroup_ids.
        - df_insert_event: WLSections from final_wls_df (with complete keys) that do not have a match in existing_events_df (with complete keys).
        - df_delete_event: Events from existing_events_df (with complete keys) that do not have a match in final_wls_df (with complete keys).
        - df_wls_incomplete_keys: WLSections from final_wls_df with missing key values.
        - df_events_incomplete_keys: Events from existing_events_df with missing key values.
    """
    logger.info("Starting to identify event operations: matches, inserts, deletes, and incomplete keys for both WLS and Events.")

    def _calculate_id_differences(ids_event_str: Optional[str], ids_wls_str: Optional[str]) -> tuple[str, str]:
        """
        Compares two comma-separated ID strings.
        ids_event_str: IDs from the 'event' side.
        ids_wls_str: IDs from the 'wls' side.
        Returns: (ids_to_remove_from_event, ids_to_add_from_wls)
        """
        def to_set(s: Optional[str]) -> set[str]:
            if not pd.notna(s) or not s: # Handles None, NaN, empty string, 0, etc.
                return set()
            # Ensure s is treated as a string before splitting, and handle potential float representations
            s_str = str(s)
            if s_str.endswith('.0'): # Handle cases like '123.0'
                s_str = s_str[:-2]
            return set(item.strip() for item in s_str.split(',') if item.strip())

        set_event = to_set(ids_event_str)
        set_wls = to_set(ids_wls_str)

        ids_to_remove = sorted(list(set_event - set_wls)) # In event but not in wls
        ids_to_add = sorted(list(set_wls - set_event))    # In wls but not in event

        return ','.join(ids_to_remove), ','.join(ids_to_add)

    # Ensure WLS_SECTION_CONECTOR exists, derived from WLS_SECTION_NAME
    # TO WEEKLOADS
    if not final_wls_df.empty and constants.WLS_SECTION_NAME in final_wls_df.columns:
        final_wls_df[constants.WLS_SECTION_CONECTOR] = final_wls_df[constants.WLS_SECTION_NAME]
    elif not final_wls_df.empty:
        logger.warning(f"Column '{constants.WLS_SECTION_NAME}' not found in final_wls_df. Cannot create '{constants.WLS_SECTION_CONECTOR}'. This might lead to issues if it's a key.")
        # Initialize the column to avoid errors later if it's expected, but it will be all NaNs
        final_wls_df[constants.WLS_SECTION_CONECTOR] = pd.NA

    # Ensure WLS_SECTION_CONECTOR exists, derived from WLS_SECTION_NAME
    # TO EVENTS
    if not existing_events_df.empty and constants.WLS_SECTION_NAME in existing_events_df.columns: # Assuming existing events also use WLS_SECTION_NAME if available
        existing_events_df[constants.WLS_SECTION_CONECTOR] = existing_events_df[constants.WLS_SECTION_NAME]
    elif not existing_events_df.empty and constants.EVENT_WLS_SECTION_CONNECTOR in existing_events_df.columns: # If EVENT_WLS_SECTION_CONNECTOR already exists
         pass # Use the existing column
    elif not existing_events_df.empty :
        logger.warning(f"Column '{constants.WLS_SECTION_NAME}' (or '{constants.EVENT_WLS_SECTION_CONNECTOR}') not found in existing_events_df. Cannot ensure '{constants.WLS_SECTION_CONECTOR}'. This might lead to issues if it's a key.")
        existing_events_df[constants.WLS_SECTION_CONECTOR] = pd.NA


    keys = [constants.MODULE_ID, constants.TYPOLOGY_IDS, constants.WLS_SECTION_CONECTOR, constants.WLS_SECTION_NAME]


    if final_wls_df.empty or existing_events_df.empty:
        logger.info("Final_wls_df or existing_events_df are empty. STOP PROCESSING")
        return df_matched_event, df_insert_event, df_delete_event, df_wls_incomplete_keys, df_events_incomplete_keys


    # Initialize DataFrames to Store Results
    df_matched_event = pd.DataFrame()
    df_insert_event = pd.DataFrame()
    df_delete_event = pd.DataFrame()
    df_wls_incomplete_keys = pd.DataFrame(columns=final_wls_df.columns)
    df_events_incomplete_keys = pd.DataFrame(columns=existing_events_df.columns)

    

    # VERIFY INCOMPLETE KEYS to df_wls_incomplete_keys
    wls_df_copy = final_wls_df.copy()
    wls_with_complete_keys_df = pd.DataFrame(columns=wls_df_copy.columns)

    
    missing_wls_keys_in_df = [key for key in keys if key not in wls_df_copy.columns]
    if missing_wls_keys_in_df:
        logger.error(f"Key columns {missing_wls_keys_in_df} not found in final_wls_df. Cannot filter for incomplete keys. All WLS data considered incomplete.")
        df_wls_incomplete_keys = wls_df_copy.copy()
        # wls_with_complete_keys_df remains empty
    else:
        # Condition for incomplete WLS keys (NaN for ID, NaN or empty for others)
        condition_incomplete_wls = (
            pd.isna(wls_df_copy[keys[0]]) |
            pd.isna(wls_df_copy[keys[1]]) | (wls_df_copy[keys[1]] == '') |
            pd.isna(wls_df_copy[keys[2]]) | (wls_df_copy[keys[2]] == '')
        )
        df_wls_incomplete_keys = wls_df_copy[condition_incomplete_wls].copy()
        wls_with_complete_keys_df = wls_df_copy[~condition_incomplete_wls].copy()
        logger.info(f"Separated {len(df_wls_incomplete_keys)} WLSections with incomplete keys.")
        logger.info(f"{len(wls_with_complete_keys_df)} WLSections have complete keys for matching.")
    

    # NOS DATAFRAMES COM CHAVES COMPLETAS AJUSTAR TIPO DE DADOS PARA STRING
    if not wls_with_complete_keys_df.empty:
        for key_item in keys: # Iterate using key_item to avoid conflict with outer scope 'key' if any
            if key_item in wls_with_complete_keys_df.columns:
                original_dtype = wls_with_complete_keys_df[key_item].dtype
                try:
                    if key_item == constants.MODULE_ID:
                        logger.info(f"Attempting to normalize and convert key '{key_item}' (dtype: {original_dtype}) to string in wls_with_complete_keys_df.")
                        numeric_series = pd.to_numeric(wls_with_complete_keys_df[key_item], errors='coerce')
                        integer_series = numeric_series.astype(pd.Int64Dtype()) # Handles NaN, converts 2134.0 to 2134
                        wls_with_complete_keys_df[key_item] = integer_series.astype(str) # pd.NA becomes '<NA>'
                        logger.info(f"Successfully normalized and converted '{key_item}' to string in wls_with_complete_keys_df.")
                    elif original_dtype != 'object' and str(original_dtype) != 'string': # For other keys, simple string conversion if not already string
                        logger.info(f"Converting key '{key_item}' (dtype: {original_dtype}) to string in wls_with_complete_keys_df for consistent merge.")
                        wls_with_complete_keys_df[key_item] = wls_with_complete_keys_df[key_item].astype(str)
                    # else: Key is already object/string, no conversion needed or handled by specific logic above
                except Exception as e:
                    logger.warning(f"Could not convert key '{key_item}' (dtype: {original_dtype}) to string in wls_with_complete_keys_df using preferred method: {e}. Falling back to simple astype(str) if not already string/object.")
                    if wls_with_complete_keys_df[key_item].dtype != 'object' and str(wls_with_complete_keys_df[key_item].dtype) != 'string':
                        wls_with_complete_keys_df[key_item] = wls_with_complete_keys_df[key_item].astype(str) # Fallback
            else:
                logger.warning(f"Key '{key_item}' not found in wls_with_complete_keys_df. Skipping type conversion for this key.")

    # VERIFY INCOMPLETE KEYS to df_events_incomplete_keys
    events_df_copy = existing_events_df.copy()
    events_with_complete_keys_df = pd.DataFrame(columns=events_df_copy.columns)
    
    if not events_df_copy.empty:
        # Ensure event_keys are actually present in events_df_copy before using them for filtering
        # For safety, let's check if the intended keys exist.
        actual_event_keys_present = [key for key in keys if key in events_df_copy.columns]
        
        if len(actual_event_keys_present) != len(keys):
            missing_keys_from_event_keys_list = list(set(keys) - set(actual_event_keys_present))
            logger.error(f"Key columns {missing_keys_from_event_keys_list} (from defined keys) not found in existing_events_df. Cannot reliably filter for incomplete keys for events.")
            df_events_incomplete_keys = events_df_copy.copy() # Mark all as incomplete if keys are missing
            # events_with_complete_keys_df remains empty
        else:
            condition_incomplete_events = (
                pd.isna(events_df_copy[keys[0]]) |
                pd.isna(events_df_copy[keys[1]]) | (events_df_copy[keys[1]] == '') |
                pd.isna(events_df_copy[keys[2]]) | (events_df_copy[keys[2]] == '')
            )
            df_events_incomplete_keys = events_df_copy[condition_incomplete_events].copy()
            events_with_complete_keys_df = events_df_copy[~condition_incomplete_events].copy()
            logger.info(f"Separated {len(df_events_incomplete_keys)} events with incomplete keys.")
            logger.info(f"{len(events_with_complete_keys_df)} events have complete keys for matching.")

            if not events_with_complete_keys_df.empty:
                for key_item in keys: # Iterate using key_item
                    if key_item in events_with_complete_keys_df.columns:
                        original_dtype = events_with_complete_keys_df[key_item].dtype
                        try:
                            if key_item == constants.MODULE_ID:
                                logger.info(f"Attempting to normalize and convert key '{key_item}' (dtype: {original_dtype}) to string in events_with_complete_keys_df.")
                                numeric_series = pd.to_numeric(events_with_complete_keys_df[key_item], errors='coerce')
                                integer_series = numeric_series.astype(pd.Int64Dtype()) # Handles NaN, converts 2134.0 to 2134
                                events_with_complete_keys_df[key_item] = integer_series.astype(str) # pd.NA becomes '<NA>'
                                logger.info(f"Successfully normalized and converted '{key_item}' to string in events_with_complete_keys_df.")
                            elif original_dtype != 'object' and str(original_dtype) != 'string': # For other keys, simple string conversion if not already string
                                logger.info(f"Converting key '{key_item}' (dtype: {original_dtype}) to string in events_with_complete_keys_df for consistent merge.")
                                events_with_complete_keys_df[key_item] = events_with_complete_keys_df[key_item].astype(str)
                            # else: Key is already object/string, no conversion needed or handled by specific logic above
                        except Exception as e:
                            logger.warning(f"Could not convert key '{key_item}' (dtype: {original_dtype}) to string in events_with_complete_keys_df using preferred method: {e}. Falling back to simple astype(str) if not already string/object.")
                            if events_with_complete_keys_df[key_item].dtype != 'object' and str(events_with_complete_keys_df[key_item].dtype) != 'string':
                                events_with_complete_keys_df[key_item] = events_with_complete_keys_df[key_item].astype(str) # Fallback
                    else:
                        logger.warning(f"Key '{key_item}' not found in events_with_complete_keys_df. Skipping type conversion for this key.")
    else:
        logger.info("existing_events_df is empty. No events to filter for incomplete keys.")



    # Perform merge operations using dataframes with complete keys
    if not events_with_complete_keys_df.empty and not wls_with_complete_keys_df.empty:
        # Check if key columns actually exist in both dataframes before merge
        if not all(key in events_with_complete_keys_df.columns for key in keys):
            logger.error(f"One or more keys not found in events_with_complete_keys_df. Aborting merge for matched/delete.")
        elif not all(key in wls_with_complete_keys_df.columns for key in keys):
             logger.error(f"One or more keys not found in wls_with_complete_keys_df. Aborting merge for matched/delete.")
        else:
            merged_from_events = pd.merge(
                events_with_complete_keys_df,
                wls_with_complete_keys_df,
                left_on=keys,
                right_on=keys,
                how='left',
                suffixes=('_event', '_wls'),
                indicator='_merge_indicator'
            )

            df_matched_event = merged_from_events[merged_from_events['_merge_indicator'] == 'both'].copy()
            # Clean up columns in df_matched_event: keep original event columns, add WLS info if needed, drop indicator
            if '_merge_indicator' in df_matched_event.columns:
                df_matched_event.drop(columns=['_merge_indicator'], inplace=True)
            
            # Calculate differences for teacher_ids and studentGroup_ids
            if not df_matched_event.empty:
                logger.info("Calculating teacher and student group ID differences for matched events...")
                # Define expected column names after merge (suffixed)
                teacher_ids_event_col = constants.TEACHER_IDS + '_event'
                teacher_ids_wls_col = constants.TEACHER_IDS + '_wls'
                student_group_ids_event_col = constants.STUDENT_GROUP_IDS + '_event'
                student_group_ids_wls_col = constants.STUDENT_GROUP_IDS + '_wls'

                # --- Teachers ---
                # Check if source columns exist to avoid KeyErrors if they were not in original DFs
                if teacher_ids_event_col in df_matched_event.columns or teacher_ids_wls_col in df_matched_event.columns:
                    teacher_diffs = df_matched_event.apply(
                        lambda row: _calculate_id_differences(
                            row.get(teacher_ids_event_col),
                            row.get(teacher_ids_wls_col)
                        ), axis=1
                    )
                    df_matched_event[['teacher_ids_to_remove', 'teacher_ids_to_add']] = pd.DataFrame(teacher_diffs.tolist(), index=df_matched_event.index)
                else:
                    logger.warning(f"Source columns for teacher ID comparison ('{teacher_ids_event_col}', '{teacher_ids_wls_col}') not found in df_matched_event. Skipping teacher diff calculation.")
                    df_matched_event['teacher_ids_to_remove'] = ""
                    df_matched_event['teacher_ids_to_add'] = ""
                
                # --- Student Groups ---
                if student_group_ids_event_col in df_matched_event.columns or student_group_ids_wls_col in df_matched_event.columns:
                    sg_diffs = df_matched_event.apply(
                        lambda row: _calculate_id_differences(
                            row.get(student_group_ids_event_col),
                            row.get(student_group_ids_wls_col)
                        ), axis=1
                    )
                    df_matched_event[['studentGroup_ids_to_remove', 'studentGroup_ids_to_add']] = pd.DataFrame(sg_diffs.tolist(), index=df_matched_event.index)
                else:
                    logger.warning(f"Source columns for student group ID comparison ('{student_group_ids_event_col}', '{student_group_ids_wls_col}') not found in df_matched_event. Skipping student group diff calculation.")
                    df_matched_event['studentGroup_ids_to_remove'] = ""
                    df_matched_event['studentGroup_ids_to_add'] = ""
                logger.info("Finished calculating ID differences.")

            # Potentially drop redundant _wls columns if they are identical to _event columns due to merge keys
            # For now, keeping them for clarity or potential use in update logic
            logger.info(f"Identified {len(df_matched_event)} matched records between events and WLS (both with complete keys).")

            delete_mask = merged_from_events['_merge_indicator'] == 'left_only'
            # df_delete_event should contain original columns from events_with_complete_keys_df
            left_only_from_merged_events = merged_from_events[delete_mask]

            if not left_only_from_merged_events.empty:
                cols_to_select_for_delete = []
                rename_map_for_delete = {}
                for original_col_name in events_with_complete_keys_df.columns:
                    if original_col_name in keys: # Key columns are not suffixed by default in this type of merge
                        cols_to_select_for_delete.append(original_col_name)
                    else: # Non-key columns
                        suffixed_col_name = original_col_name + '_event'
                        if suffixed_col_name in left_only_from_merged_events.columns:
                            cols_to_select_for_delete.append(suffixed_col_name)
                            rename_map_for_delete[suffixed_col_name] = original_col_name
                        elif original_col_name in left_only_from_merged_events.columns: # Was not suffixed (unique to left or no collision)
                            cols_to_select_for_delete.append(original_col_name)
                        else:
                            logger.warning(f"Column '{original_col_name}' from events_with_complete_keys_df not found (nor as suffixed) in merged data for delete list. Will be missing in df_delete_event.")
                df_delete_event = left_only_from_merged_events[cols_to_select_for_delete].rename(columns=rename_map_for_delete).copy()
            else:
                # If no rows to delete, create an empty DataFrame with the correct columns
                df_delete_event = pd.DataFrame(columns=events_with_complete_keys_df.columns)

            logger.info(f"Identified {len(df_delete_event)} events (with complete keys) to potentially delete (not found in WLS with complete keys).")
        
    elif events_with_complete_keys_df.empty and not wls_with_complete_keys_df.empty:
        logger.info("No events with complete keys to perform matching. All WLS entries (with complete keys) could be inserts.")
        # df_delete_event remains empty
    elif not events_with_complete_keys_df.empty and wls_with_complete_keys_df.empty:
        logger.info("No WLS entries with complete keys. All existing events (with complete keys) are candidates for deletion.")
        df_delete_event = events_with_complete_keys_df.copy()
        # df_matched_event remains empty
    else: # Both are empty (or one became empty after key filtering)
        logger.info("Either events_with_complete_keys_df or wls_with_complete_keys_df (or both) are empty. No complex merge operations possible.")


    # Identify inserts from WLS data (with complete keys)
    if not wls_with_complete_keys_df.empty:
        if not events_with_complete_keys_df.empty:
            # Check if key columns actually exist in both dataframes before merge
            if not all(key in wls_with_complete_keys_df.columns for key in keys):
                logger.error(f"One or more keys not found in wls_with_complete_keys_df. Aborting merge for inserts.")
            elif not all(key in events_with_complete_keys_df.columns for key in keys):
                logger.error(f"One or more keys not found in events_with_complete_keys_df. Aborting merge for inserts.")
            else:
                merged_from_wls = pd.merge(
                    wls_with_complete_keys_df,
                    events_with_complete_keys_df, 
                    left_on=keys,
                    right_on=keys,
                    how='left',
                    suffixes=('_wls', '_event'), # Suffixes might be useful for inspection, but insert_df should come from wls
                    indicator='_merge_indicator'
                )
                insert_mask = merged_from_wls['_merge_indicator'] == 'left_only'
                
                left_only_from_merged_wls = merged_from_wls[insert_mask]

                if not left_only_from_merged_wls.empty:
                    cols_to_select_for_insert = []
                    rename_map_for_insert = {}
                    for original_col_name in wls_with_complete_keys_df.columns:
                        if original_col_name in keys: # Key columns
                            cols_to_select_for_insert.append(original_col_name)
                        else: # Non-key columns
                            suffixed_col_name = original_col_name + '_wls'
                            if suffixed_col_name in left_only_from_merged_wls.columns:
                                cols_to_select_for_insert.append(suffixed_col_name)
                                rename_map_for_insert[suffixed_col_name] = original_col_name
                            elif original_col_name in left_only_from_merged_wls.columns:
                                cols_to_select_for_insert.append(original_col_name)
                            else:
                                logger.warning(f"Column '{original_col_name}' from wls_with_complete_keys_df not found (nor as suffixed) in merged data for insert list. Will be missing in df_insert_event.")
                    df_insert_event = left_only_from_merged_wls[cols_to_select_for_insert].rename(columns=rename_map_for_insert).copy()
                else:
                    df_insert_event = pd.DataFrame(columns=wls_with_complete_keys_df.columns)

                logger.info(f"Identified {len(df_insert_event)} WLSections (with complete keys) to potentially insert as new events.")
        else: # No events with complete keys, so all WLS with complete keys are inserts
            logger.info("No events with complete keys found. All WLSections (with complete keys) are candidates for insertion.")
            df_insert_event = wls_with_complete_keys_df.copy()
        logger.info(f"Identified {len(df_insert_event)} WLSections (with complete keys) to potentially insert as new events.")
    else: # final_wls_df (or wls_with_complete_keys_df) is empty
        logger.info("final_wls_df (or wls_with_complete_keys_df) is empty. No insert operations from its perspective.")
        # df_insert_event remains empty as initialized
        
    logger.info(f"Event operations identification complete. "
                f"Matched: {len(df_matched_event)}, Insert: {len(df_insert_event)}, Delete: {len(df_delete_event)}, "
                f"WLS Incomplete Keys: {len(df_wls_incomplete_keys)}, Event Incomplete Keys: {len(df_events_incomplete_keys)}")
    
    #VALIDATION NUMBER EVENTS BY GROUP

    df_check_events_by_group = df_insert_event.copy()

    df_check_events_by_group = df_check_events_by_group[['studentGroup_names']].copy()
    df_count_events_by_group = count_events_by_group(df_check_events_by_group)

    try:
        output_dir = constants.OUTPUT_FILES_DIR 
        output_path = os.path.join(output_dir, output_event_operations_excel_filename)
        os.makedirs(output_dir, exist_ok=True) 
        logger.info(f"Exporting event operations analysis to Excel: {output_path}")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            if not df_matched_event.empty:
                df_matched_event.to_excel(writer, sheet_name='Matched_Events', index=False)
            logger.info(f"Written Matched_Events sheet with {len(df_matched_event)} rows." if not df_matched_event.empty else "Skipped empty Matched_Events sheet.")
            
            if not df_insert_event.empty:
                df_insert_event.to_excel(writer, sheet_name='Events_To_Insert', index=False)
            logger.info(f"Written Events_To_Insert sheet with {len(df_insert_event)} rows." if not df_insert_event.empty else "Skipped empty Events_To_Insert sheet.")

            if not df_delete_event.empty:
                df_delete_event.to_excel(writer, sheet_name='Events_To_Delete', index=False)
            logger.info(f"Written Events_To_Delete sheet with {len(df_delete_event)} rows." if not df_delete_event.empty else "Skipped empty Events_To_Delete sheet.")
            
            if not df_wls_incomplete_keys.empty:
                df_wls_incomplete_keys.to_excel(writer, sheet_name='WLS_Incomplete_Keys', index=False)
            logger.info(f"Written WLS_Incomplete_Keys sheet with {len(df_wls_incomplete_keys)} rows." if not df_wls_incomplete_keys.empty else "Skipped empty WLS_Incomplete_Keys sheet.")


            if not df_events_incomplete_keys.empty:
                df_events_incomplete_keys.to_excel(writer, sheet_name='Events_Incomplete_Keys', index=False)
            logger.info(f"Written Events_Incomplete_Keys sheet with {len(df_events_incomplete_keys)} rows." if not df_events_incomplete_keys.empty else "Skipped empty Events_Incomplete_Keys sheet.")

            if not df_count_events_by_group.empty:
                df_count_events_by_group.to_excel(writer, sheet_name='Event_by_Group', index=False)
            logger.info(f"Written Event_by_Group")
            
        logger.info(f"Successfully exported event operations analysis to {output_path}")
    except Exception as e:
        logger.error(f"Failed to export event operations to Excel: {e}", exc_info=True)

    return df_matched_event, df_insert_event, df_delete_event, df_wls_incomplete_keys, df_events_incomplete_keys 

def count_events_by_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Counts the number of events for each student group name.
    
    Args:
        df: DataFrame containing a 'studentGroup_names' column with comma-separated group names
        
    Returns:
        DataFrame with two columns:
        - Name_Group: The student group name
        - Number_Event: Count of events for that group
    """
    # Create a list to store all individual group names
    all_groups = []
    
    # Process each row's studentGroup_names
    for groups_str in df['studentGroup_names']:
        if pd.isna(groups_str):
            continue
        # Split by comma and strip whitespace
        groups = [g.strip() for g in str(groups_str).split(',')]
        all_groups.extend(groups)
    
    # Create a Series with the counts
    group_counts = pd.Series(all_groups).value_counts().reset_index()
    
    # Rename columns to match requested format
    group_counts.columns = ['Name_Group', 'Number_Event']
    
    return group_counts


def manage_missing_data(df : pd.DataFrame):

    series_dict_null = {'event_name' : '', 
                        'wlsSectionName' : '',
                        'wlsSectionConnector' : '',
                        'annotations' : '',
                        'unit' : '',
                        } 
    
    
    df = df.fillna(series_dict_null)
    
    return (df)

def insert_annotations_on_event(df: pd.DataFrame, annotation_info: str) -> pd.DataFrame:
    """
    Actualiza a coluna 'annotations' no DataFrame com base na annotation_info fornecida.
    
    A coluna annotations é actualizada concatenando a nova informação com a existente:
    - Nova informação: annotation_info + sufixo (baseado nas alterações)
    - Se há annotations existentes: "nova_info\n existing_annotations"
    - Se não há annotations existentes: apenas "nova_info"
    
    Os sufixos são determinados pela presença de valores nas seguintes colunas:
    - teacher_ids_to_remove
    - teacher_ids_to_add  
    - studentGroup_ids_to_remove
    - studentGroup_ids_to_add
    
    Casos de modificação da string:
    - CASO 1: Se há valores em teachers (remove OU add) E NÃO há valores em studentGroup: 
              adiciona " - PR" (Professor alterado)
    - CASO 2: Se há valores em studentGroup (remove OU add) E NÃO há valores em teachers:
              adiciona " - GR" (Grupo alterado) 
    - CASO 3: Se há valores em ambos teachers E studentGroup:
              adiciona " - GR;PR" (Grupo e Professor alterados)
    
    Args:
        df: DataFrame contendo as colunas necessárias para análise
        annotation_info: String base para a anotação (ex: 'UPD1_2526_0207_S1')
        
    Returns:
        DataFrame com coluna 'annotations' actualizada
    """
    # Cria uma cópia do DataFrame para não modificar o original
    df_copy = df.copy()
    
    
    # Verifica se as colunas existem no DataFrame
    required_cols = ['teacher_ids_to_remove', 'teacher_ids_to_add', 
                     'studentGroup_ids_to_remove', 'studentGroup_ids_to_add']
    
    for col in required_cols:
        if col not in df_copy.columns:
            logger.warning(f"Coluna '{col}' não encontrada no DataFrame. Criando coluna vazia.")
            df_copy[col] = ''
        
    
    # Verifica diretamente se há conteúdo string nas colunas
    def has_content(col_name):
        """Verifica se a coluna tem conteúdo string significativo"""
        series = df_copy[col_name].astype(str).str.strip()
        # True = tem conteúdo, False = vazio/nan
        empty_values = ['', 'nan', '<NA>', 'NaN', 'None', 'null']
        has_real_content = []
        
        for value in series:
            if value in empty_values:
                has_real_content.append(False)
            else:
                has_real_content.append(True)
        
        return pd.Series(has_real_content, index=df_copy.index)
    
    # Verifica cada coluna individualmente
    has_teacher_remove = has_content('teacher_ids_to_remove')
    has_teacher_add = has_content('teacher_ids_to_add')
    has_student_remove = has_content('studentGroup_ids_to_remove')
    has_student_add = has_content('studentGroup_ids_to_add')
    

    
    # Combina as verificações
    has_teacher_changes = has_teacher_remove | has_teacher_add
    has_student_changes = has_student_remove | has_student_add
    
    # Garante que a coluna annotations existe
    if 'annotations' not in df_copy.columns:
        df_copy['annotations'] = ''
    
    # Aplica os sufixos baseados nas condições e actualiza a coluna annotations
    for i in range(len(df_copy)):
        teacher_changed = has_teacher_changes.iloc[i]
        student_changed = has_student_changes.iloc[i]
        
        # Determina o novo annotation_info com sufixo
        if teacher_changed and student_changed:
            # CASO 3: Ambos alterados
            new_annotation_info = annotation_info + ' - GR;PR'
        elif teacher_changed and not student_changed:
            # CASO 1: Só professor alterado
            new_annotation_info = annotation_info + ' - PR'
        elif not teacher_changed and student_changed:
            # CASO 2: Só grupo alterado
            new_annotation_info = annotation_info + ' - GR'
        else:
            # Se nem teacher nem student changed, mantém o annotation_info original
            new_annotation_info = annotation_info
            
        # Obtém a annotation existente
        existing_annotation = df_copy.iloc[i]['annotations']
        existing_str = str(existing_annotation).strip() if pd.notna(existing_annotation) else ''
        
        # Concatena: nova info + '\n' + info existente (se houver)
        if existing_str and existing_str not in ['', 'nan', '<NA>', 'NaN', 'None', 'null']:
            final_annotation = new_annotation_info + '\n' + existing_str
        else:
            final_annotation = new_annotation_info
            
        # Actualiza a coluna annotations
        df_copy.iloc[i, df_copy.columns.get_loc('annotations')] = final_annotation
    
    # Log dos resultados
    case1_count = (has_teacher_changes & ~has_student_changes).sum()
    case2_count = (~has_teacher_changes & has_student_changes).sum()
    case3_count = (has_teacher_changes & has_student_changes).sum()
    no_changes_count = (~has_teacher_changes & ~has_student_changes).sum()
    
    logger.info(f"Coluna 'annotations' actualizada com base em '{annotation_info}':")
    logger.info(f"  Caso 1 (só PR): {case1_count} registros")
    logger.info(f"  Caso 2 (só GR): {case2_count} registros")
    logger.info(f"  Caso 3 (GR;PR): {case3_count} registros")
    logger.info(f"  Sem alterações: {no_changes_count} registros")
    
    if no_changes_count > 0:
        logger.warning(f"ATENÇÃO: {no_changes_count} registros sem alterações (não deveria acontecer)!")
    
    return df_copy


def create_column_institucion_info_and_id_mod(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new 'Institution' column by extracting unique institution names
    from the 'course_names' column, which is expected to contain lists of strings.
    It uses pandas.explode for robust processing.
    """
    if 'course_names' not in df.columns:
        logger.warning("DataFrame does not have 'course_names' column. Cannot create 'Institution' column.")
        df['Institution'] = None
        return df

    # Create a copy to avoid SettingWithCopyWarning
    df_copy = df.copy()

    # Explode the DataFrame on 'course_names'. Rows with None or empty lists will result in NaN
    exploded = df_copy.explode('course_names')

    # Extract the institution part (before the ':') from the exploded strings
    # .str accessor handles NaNs gracefully
    institutions = exploded['course_names'].str.split(':', n=1, expand=True)[0].str.strip()

    # Group by the original index, get unique non-null institutions, and convert to a list
    # The lambda function ensures we get a list of unique values for each original row
    agg_institutions = institutions.groupby(level=0).agg(lambda x: sorted(list(x.dropna().unique())) if x.dropna().any() else None)

    # Map the aggregated lists back to the original DataFrame's index
    df['Institution'] = df.index.map(agg_institutions)

    logger.info("Successfully created/updated 'Institution' column using explode.")
    
    return df

def create_column_institucion_info_and_id_mod_acronyms(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a new 'Institution_Acronyms' column by extracting unique institution acronyms
    from the 'course_acronyms' column, which is expected to contain lists of strings.
    It uses pandas.explode for robust processing.
    """
    if 'course_acronyms' not in df.columns:
        logger.warning("DataFrame does not have 'course_acronyms' column. Cannot create 'Institution_Acronyms' column.")
        df['Institution_Acronyms'] = None
        return df

    # Create a copy to avoid SettingWithCopyWarning
    df_copy = df.copy()

    # Explode the DataFrame on 'course_acronyms'.
    exploded = df_copy.explode('course_acronyms')

    # Extract the institution acronym part (before the '-') from the exploded strings
    institution_acronyms = exploded['course_acronyms'].str.split('-', n=1, expand=True)[0].str.strip()

    # Group by the original index, get unique non-null acronyms, and convert to a list
    agg_acronyms = institution_acronyms.groupby(level=0).agg(lambda x: sorted(list(x.dropna().unique())) if x.dropna().any() else None)

    # Map the aggregated lists back to the original DataFrame's index
    df['Institution_Acronyms'] = df.index.map(agg_acronyms)

    logger.info("Successfully created/updated 'Institution_Acronyms' column using explode.")
    
    return df
