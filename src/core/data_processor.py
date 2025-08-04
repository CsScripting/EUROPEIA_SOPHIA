# Data processing logic using Pandas 
import logging
import pandas as pd # Import pandas early as we'll likely use it soon
from collections import defaultdict # Use defaultdict for easier mapping

# Assuming config.py and api client are accessible
try:
    import config
    from src.api.client import ApiClient # Import the client class
    from src.core import constants # Import constants
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) # Add project root to path
    import config
    from src.api.client import ApiClient
    from src.core import constants # Import constants

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper function to safely extract and concatenate list data ---
def _extract_and_concat(data_list: list | None, key: str, separator: str = ",") -> str | None:
    """Extracts a specific key from a list of dicts and concatenates into a string."""
    if not isinstance(data_list, list):
        return None
    values = [str(item.get(key)) for item in data_list if isinstance(item, dict) and item.get(key) is not None]
    return separator.join(values) if values else None

# --- Helper function to safely extract nested typology data and concatenate ---
def _extract_nested_and_concat(data_list: list | None, nested_key: str, item_key: str, separator: str = ",") -> str | None:
    """Extracts a key from a nested dict within a list of dicts and concatenates."""
    if not isinstance(data_list, list):
        return None
    values = []
    for item in data_list:
        if isinstance(item, dict):
            nested_obj = item.get(nested_key)
            if isinstance(nested_obj, dict):
                 value = nested_obj.get(item_key)
                 if value is not None:
                     values.append(str(value))
    return separator.join(values) if values else None

def _convert_slot_to_minutes(slot_str: str | None) -> int:
    """Converts an ISO 8601 slot string to minutes, returning 0 on error or None input."""
    if not slot_str:
        return 0
    try:
        # Use pandas to parse the datetime string
        dt_obj = pd.to_datetime(slot_str)
        # Extract minutes
        return dt_obj.minute
    except (ValueError, TypeError) as e:
        # Log the error for the specific string that failed
        logging.warning(f"Could not convert slot string '{slot_str}' to minutes: {e}. Returning 0.")
        return 0

def _extract_and_format_dates(data_list: list | None, key: str, date_format: str = "%Y-%m-%d", separator: str = ",") -> str | None:
    """Extracts datetime strings, formats them to date strings, and concatenates."""
    if not isinstance(data_list, list):
        return None
    formatted_dates = []
    for item in data_list:
        if isinstance(item, dict):
            date_str = item.get(key)
            if date_str:
                try:
                    dt_obj = pd.to_datetime(date_str) # errors='raise' is default
                    formatted_dates.append(dt_obj.strftime(date_format))
                except (ValueError, TypeError) as e:
                    logging.warning(f"Could not convert date string '{date_str}' using key '{key}': {e}. Skipping this date.")
    return separator.join(formatted_dates) if formatted_dates else None

def fetch_academic_term_id_by_name(api_client: ApiClient, term_name: str) -> str | None:
    """
    Fetches the ID of a specific AcademicTerm by its name using the POST search endpoint.

    Args:
        api_client: An initialized ApiClient instance.
        term_name: The exact name of the AcademicTerm to search for.

    Returns:
        The ID (string or int, depending on API) of the found AcademicTerm,
        or None if not found or an error occurs.
    """
    if not term_name:
        logging.error("Term name cannot be empty.")
        return None

    # Construct the JSON payload for the POST search request
    search_payload = {
        "filters": [
            {
                "type": 0,  # Assuming type 0 means equality or similar, adjust if needed
                "path": "Name", # Assuming the field name is 'Name', adjust if needed
                "Value": term_name
            }
        ]
        # Add other necessary parts to the payload if required by the API
        # "paging": { "pageSize": 10, "pageNumber": 1 },
        # "sorting": [ { "path": "Name", "direction": 0 } ]
    }
    endpoint = config.ACADEMIC_TERM_SEARCH_ENDPOINT

    try:
        logging.info(f"Attempting to search for AcademicTerm '{term_name}' using POST to: {endpoint} with payload: {search_payload}")
        # Use the new search_data method with the payload
        search_results = api_client.search_data(endpoint, json_payload=search_payload)

        if not search_results:
            logging.warning(f"No results received for AcademicTerm name: '{term_name}'")
            return None

        # --- Processing the specific response structure ---
        # Expected structure: { "data": { "data": [...] } }
        if isinstance(search_results, dict) and 'data' in search_results and \
           isinstance(search_results['data'], dict) and 'data' in search_results['data'] and \
           isinstance(search_results['data']['data'], list):

            terms_list = search_results['data']['data']
            logging.info(f"Processing {len(terms_list)} term(s) found in response structure for '{term_name}'.")

            found_term = None
            for term in terms_list:
                # Adjust key names ('id', 'name') if different in the actual object
                if isinstance(term, dict) and term.get('name') == term_name:
                    found_term = term
                    break # Found the first exact match

            if found_term:
                term_id = found_term.get('id')
                if term_id is not None: # Check for None explicitly as ID could be 0
                    logging.info(f"Found AcademicTerm '{term_name}' with ID: {term_id}")
                    return str(term_id) # Return ID as string
                else:
                    logging.error(f"Found term matching '{term_name}' but it has no 'id' key or the value is None.")
                    return None
            else:
                # This case might happen if the filter wasn't exact or API logic differs
                logging.warning(f"Response structure parsed, but no exact match found for name: '{term_name}' in the results list.")
                return None

        else:
            logging.warning(f"Received unexpected format from POST search endpoint for '{term_name}'. Expected structure like {{'data': {{'data': [...]}} }}.")
            logging.debug(f"Received data: {search_results}")
            return None

    except Exception as e:
        logging.error(f"Failed to fetch AcademicTerm ID for name '{term_name}' via POST: {e}")
        return None

def fetch_academic_year_id_by_name(api_client: ApiClient, year_name: str) -> str | None:
    """
    Fetches the ID of a specific AcademicYear by its name using the POST search endpoint.

    Args:
        api_client: An initialized ApiClient instance.
        year_name: The exact name of the AcademicYear to search for.

    Returns:
        The ID (string or int, depending on API) of the found AcademicYear,
        or None if not found or an error occurs.
    """
    if not year_name:
        logging.error("Academic Year name cannot be empty.")
        return None

    search_payload = {
        "filters": [
            {
                "type": 0, 
                "path": "Name", 
                "Value": year_name
            }
        ]
    }
    endpoint = config.ACADEMIC_YEAR_SEARCH_ENDPOINT

    try:
        logging.info(f"Attempting to search for AcademicYear '{year_name}' using POST to: {endpoint} with payload: {search_payload}")
        search_results = api_client.search_data(endpoint, json_payload=search_payload)

        if not search_results:
            logging.warning(f"No results received for AcademicYear name: '{year_name}'")
            return None

        if isinstance(search_results, dict) and 'data' in search_results and \
           isinstance(search_results['data'], dict) and 'data' in search_results['data'] and \
           isinstance(search_results['data']['data'], list):

            years_list = search_results['data']['data']
            logging.info(f"Processing {len(years_list)} year(s) found in response structure for '{year_name}'.")

            found_year = None
            for year_item in years_list:
                if isinstance(year_item, dict) and year_item.get('name') == year_name:
                    found_year = year_item
                    break 

            if found_year:
                year_id = found_year.get('id')
                if year_id is not None:
                    logging.info(f"Found AcademicYear '{year_name}' with ID: {year_id}")
                    return str(year_id)
                else:
                    logging.error(f"Found year matching '{year_name}' but it has no 'id' key or the value is None.")
                    return None
            else:
                logging.warning(f"Response structure parsed, but no exact match found for name: '{year_name}' in the results list.")
                return None
        else:
            logging.warning(f"Received unexpected format from POST search endpoint for '{year_name}'. Expected structure like {{'data': {{'data': [...]}} }}.")
            logging.debug(f"Received data: {search_results}")
            return None

    except Exception as e:
        logging.error(f"Failed to fetch AcademicYear ID for name '{year_name}' via POST: {e}")
        return None

def fetch_modules_for_term(api_client: ApiClient, academic_term_id: str) -> pd.DataFrame | None:
    """
    Fetches Curricular Plan Modules for a specific AcademicTerm ID using POST search,
    extracts module details (id, code, name), and returns them as a Pandas DataFrame.

    Args:
        api_client: An initialized ApiClient instance.
        academic_term_id: The ID of the AcademicTerm.

    Returns:
        A Pandas DataFrame with columns ['module_id', 'module_code', 'module_name'],
        containing data for all modules found. Returns None if an error occurs or no modules are found.
    """
    if not academic_term_id:
        logging.error("Academic Term ID cannot be empty.")
        return None

    # Construct the JSON payload for the POST search request
    search_payload = {
        "filters": [
            {
                "type": 0,
                "path": "Id",
                "Value": academic_term_id
            }
        ]
        # Add paging/sorting if needed, e.g., to get all modules:
        # "paging": { "pageSize": 1000, "pageNumber": 1 } # Adjust pageSize as needed
    }
    endpoint = config.MODULES_SEARCH_ENDPOINT # Endpoint for module search

    try:
        logging.info(f"Attempting to fetch modules for AcademicTerm ID '{academic_term_id}' using POST to: {endpoint}")
        search_results = api_client.search_data(endpoint, json_payload=search_payload)

        if not search_results:
            logging.warning(f"No results received for modules search (Term ID: {academic_term_id}).")
            return None

        # --- Processing the nested response structure ---
        modules_data_list = []
        if isinstance(search_results, dict) and 'data' in search_results and \
           isinstance(search_results['data'], dict) and 'data' in search_results['data'] and \
           isinstance(search_results['data']['data'], list) and \
           len(search_results['data']['data']) > 0: # Check if list is not empty
            term_data = search_results['data']['data'][0]
            if isinstance(term_data, dict) and 'curricularPlanModules' in term_data and \
               isinstance(term_data['curricularPlanModules'], list):
                for plan in term_data['curricularPlanModules']:
                    if isinstance(plan, dict) and 'modules' in plan and \
                       isinstance(plan['modules'], list):
                        for module in plan['modules']:
                            if isinstance(module, dict):
                                module_id = module.get('id')
                                module_code = module.get('code')
                                module_name = module.get('name')
                                if module_id is not None: # Require at least the ID
                                    modules_data_list.append({
                                        constants.MODULE_ID: module_id, # Use constant
                                        constants.MODULE_CODE: module_code, # Use constant
                                        constants.MODULE_NAME: module_name # Use constant
                                    })
                                else:
                                    logging.warning(f"Skipping module item without 'id': {module}")
                            else:
                                 logging.warning(f"Skipping non-dictionary item in inner modules list: {module}")
                    else:
                        logging.warning(f"Skipping plan item without 'modules' list: {plan}")
            else:
                logging.warning(f"AcademicTerm data for ID {academic_term_id} does not contain 'curricularPlanModules' list.")
        else:
            logging.warning(f"Received unexpected format or empty data from POST modules search for Term ID {academic_term_id}.")
            logging.debug(f"Received data: {search_results}")
            return None # Return None if structure is wrong or no data

        # --- Convert to DataFrame ---
        if not modules_data_list:
            logging.warning(f"No modules extracted for AcademicTerm ID {academic_term_id}.")
            # Use constants for empty DataFrame columns
            return pd.DataFrame(columns=[constants.MODULE_ID, constants.MODULE_CODE, constants.MODULE_NAME])

        # Create initial DataFrame (might contain duplicate modules)
        initial_modules_df = pd.DataFrame(modules_data_list)
        logging.info(f"Initially extracted {len(initial_modules_df)} module entries (may include duplicates across plans).")

        # --- Remove duplicates based on module_id, keeping the first occurrence ---
        modules_df = initial_modules_df.drop_duplicates(subset=[constants.MODULE_ID], keep='first').reset_index(drop=True)
        logging.info(f"Filtered down to {len(modules_df)} unique modules for Term ID {academic_term_id}.")

        return modules_df

    except Exception as e:
        logging.error(f"Failed to fetch and process modules for AcademicTerm ID '{academic_term_id}' via POST: {e}")
        return None

def fetch_wloads_for_module(api_client: ApiClient, module_identifier: str | int, academic_term_identifier: str | int) -> list | None:
    """
    Fetches WLoads data, extracts detailed fields from WLoad, Module, Term, Session,
    Section, Groups, Typologies, Weeks for each WLSection, returning a list of enriched dictionaries.
    """
    if not module_identifier or not academic_term_identifier:
        logging.error("Module Identifier and Academic Term Identifier cannot be empty.")
        return None

    try:
        endpoint_path = config.WLOADS_ENDPOINT_TEMPLATE.format(
            moduleIdentifier=module_identifier,
            academicTermIdentifier=academic_term_identifier
        )
        # logging.info(f"Attempting to fetch WLoads data using GET from: {endpoint_path}")
        wload_response = api_client.get_data(endpoint_path)

        if not wload_response:
            logging.warning(f"No WLoad data received for module {module_identifier}, term {academic_term_identifier} from {endpoint_path}")
            return None

        all_enriched_wls_sections = []
        if isinstance(wload_response, dict) and 'data' in wload_response and \
           isinstance(wload_response['data'], list) and len(wload_response['data']) > 0:

            # --- Loop through each WLoad returned in the data list ---
            for wload_data in wload_response['data']:
                if not isinstance(wload_data, dict):
                    logging.warning(f"Skipping non-dictionary item in WLoad data list for module {module_identifier}: {wload_data}")
                    continue # Skip to the next item in the wload_response['data'] list

                # --- Extract data from WLoad Level (Level 0) ---
                wload_id = wload_data.get('id')
                wload_name = wload_data.get('name')

                # Nested Module data
                module_obj = wload_data.get('module', {}) if isinstance(wload_data.get('module'), dict) else {}
                module_id = module_obj.get('id')
                module_Name = module_obj.get('name')
                module_Code = module_obj.get('code')

                # Nested Academic Term data
                academic_term_obj = wload_data.get('academicTerm', {}) if isinstance(wload_data.get('academicTerm'), dict) else {}
                academicTerm_slot_str = academic_term_obj.get('slot') # Get the string
                academicTerm_slot_minutes = _convert_slot_to_minutes(academicTerm_slot_str) # Convert to minutes

                # WLoad Typologies (List)
                wload_typologies_list = wload_data.get('wLoadTypologies')
                wLoadTypologies_numSlots = _extract_and_concat(wload_typologies_list, 'numSlots')
                typology_ids = _extract_nested_and_concat(wload_typologies_list, 'typology', 'id')
                typology_names = _extract_nested_and_concat(wload_typologies_list, 'typology', 'name')

                # Weeks (List)
                weeks_list = wload_data.get('weeks')
                weeks_ids = _extract_and_concat(weeks_list, 'id')
                weeks_startDates = _extract_and_format_dates(weeks_list, 'startDate')

                # --- Iterate through WL Sessions (Level 1) ---
                wl_sessions = wload_data.get('wlSessions')
                if not isinstance(wl_sessions, list):
                    logging.warning(f"WLoad {wload_id} for module {module_identifier} does not contain a list of 'wlSessions'. Skipping sessions for this WLoad.")
                    continue # Skip processing sessions/sections for this WLoad

                for session in wl_sessions:
                    if not isinstance(session, dict):
                         logging.warning(f"Skipping non-dictionary item in wlSessions for WLoad {wload_id}: {session}")
                         continue # Skip to next session

                    wlSession_id = session.get('id')
                    wlSession_name = session.get('name')

                    # --- Iterate through WLS Sections (Level 2) ---
                    wls_sections = session.get('wlsSections')
                    if not isinstance(wls_sections, list):
                        logging.warning(f"WLSession {wlSession_id} in WLoad {wload_id} does not contain a list of 'wlsSections'. Skipping sections for this session.")
                        continue # Skip processing sections for this Session

                    for section in wls_sections:
                        if not isinstance(section, dict):
                            logging.warning(f"Skipping non-dictionary item in wlsSections for WLSession {wlSession_id}: {section}")
                            continue # Skip to next section

                        wlsSection_id = section.get('id')
                        wlsSection_name = section.get('name')
                        wlsSection_numStudents = section.get('numStudents')
                        wlsSection_conector = section.get('conector')

                        # Student Groups (List within Section)
                        student_groups_list = section.get('studentGroups')
                        studentGroup_ids = _extract_and_concat(student_groups_list, 'id')
                        studentGroup_names = _extract_and_concat(student_groups_list, 'name')
                        studentGroup_state = _extract_and_concat(student_groups_list, 'active')

                        # --- Append enriched section data to the list ---
                        all_enriched_wls_sections.append({
                            # WLoad Level
                            constants.WLOAD_ID: wload_id,
                            constants.WLOAD_NAME: wload_name,
                            constants.MODULE_ID: module_id, # From nested module object
                            constants.MODULE_NAME: module_Name, # From nested module object
                            constants.MODULE_CODE: module_Code, # From nested module object
                            constants.ACADEMIC_TERM_SLOT: academicTerm_slot_minutes, # Use the converted minutes value
                            constants.TYPOLOGY_NUM_SLOTS: wLoadTypologies_numSlots, # Corrected constant name usage if it was also wrong
                            constants.TYPOLOGY_IDS: typology_ids,
                            constants.TYPOLOGY_NAMES: typology_names,
                            constants.WEEKS_IDS: weeks_ids,
                            constants.WEEKS_START_DATES: weeks_startDates,
                            # Session Level
                            constants.WL_SESSION_ID: wlSession_id,
                            constants.WL_SESSION_NAME: wlSession_name,
                            # Section Level
                            constants.WLS_SECTION_ID: wlsSection_id,
                            constants.WLS_SECTION_NAME: wlsSection_name,
                            constants.WLS_SECTION_NUM_STUDENTS: wlsSection_numStudents,
                            constants.WLS_SECTION_CONECTOR: wlsSection_conector,
                            constants.STUDENT_GROUP_IDS: studentGroup_ids,
                            constants.STUDENT_GROUP_NAMES: studentGroup_names,
                            constants.STUDENT_GROUP_STATE: studentGroup_state
                        })
            # --- End of loop through WLoads ---

        elif isinstance(wload_response, dict) and 'data' in wload_response and \
             isinstance(wload_response['data'], list) and len(wload_response['data']) == 0:
             logging.warning(f"Received empty data list for WLoads module {module_identifier}, term {academic_term_identifier}.")
             return [] # Return empty list, not None, as the call was successful but yielded no data
        else:
            logging.warning(f"Received unexpected format from WLoad endpoint for module {module_identifier}, term {academic_term_identifier}. Expected structure like {{'data': [...]}}.")
            logging.debug(f"Received data: {wload_response}")
            return None # Indicate an error in response format

        # logging.info(f"Successfully extracted {len(all_enriched_wls_sections)} WLSections in total for module {module_identifier}, term {academic_term_identifier} across all returned WLoads.")
        return all_enriched_wls_sections

    except Exception as e:
        logging.error(f"Failed to fetch or process WLoads for module {module_identifier}, term {academic_term_identifier}: {e}")
        return None # Return None on error

def fetch_teachers_for_wload(api_client: ApiClient, wload_id: str | int) -> list | None:
    """
    Fetches teacher group data for a specific WLoad ID. Aggregates teacher info
    (IDs, names, codes) per WLSection name within that WLoad.

    Args:
        api_client: An initialized ApiClient instance.
        wload_id: The identifier of the WLoad.

    Returns:
        A list of dictionaries, each representing a WLSection with associated teachers:
        {'wload_id', 'wls_section_name', 'teacher_ids', 'teacher_names', 'teacher_codes'}.
        Teacher info is concatenated into comma-separated strings.
        Returns None on error, empty list if no associations found.
    """
    if not wload_id:
        logging.error("WLoad ID cannot be empty.")
        return None

    try:
        endpoint_path = config.TEACHER_GROUPS_ENDPOINT_TEMPLATE.format(
            wLoadIdentifier=wload_id
        )
        logging.info(f"Attempting to fetch Teacher Groups using GET from: {endpoint_path}")
        response = api_client.get_data(endpoint_path)

        if not response or not isinstance(response, dict) or 'data' not in response:
            logging.warning(f"No valid data received for Teacher Groups (WLoad ID: {wload_id}). Response: {response}")
            return []

        teacher_group_list = response['data']
        if not isinstance(teacher_group_list, list) or not teacher_group_list:
             logging.warning(f"No teacher groups found in 'data' array for WLoad ID: {wload_id}.")
             return []

        # Map: section_name -> set of (teacher_id, teacher_name, teacher_code) tuples
        section_teacher_map = defaultdict(set)

        for group in teacher_group_list:
            if not isinstance(group, dict): continue

            teachers = group.get('teachers')
            sections_in_group = group.get('wlsSections')

            # Only proceed if both teachers and sections are present in this group
            if isinstance(teachers, list) and teachers and isinstance(sections_in_group, list) and sections_in_group:
                # Extract teacher details for this group once
                group_teacher_details = set()
                for teacher in teachers:
                    if isinstance(teacher, dict):
                        teacher_id = teacher.get('id')
                        teacher_name = teacher.get('name')
                        teacher_code = teacher.get('code')
                        teacher_state = teacher.get('active')
                        if teacher_id is not None: # Require ID
                             # Store as tuple for hashing in set
                            group_teacher_details.add((str(teacher_id), str(teacher_name or ''), str(teacher_code or ''), str(teacher_state) if teacher_state is not None else ''))

                # Add these teachers to all sections listed in this group
                for section in sections_in_group:
                     if isinstance(section, dict):
                         section_name = section.get('name')
                         if section_name is not None:
                             section_teacher_map[section_name].update(group_teacher_details) # Use update for sets

        # --- Aggregate results ---
        aggregated_teacher_data = []
        for section_name, teacher_details_set in section_teacher_map.items():
            if not teacher_details_set: continue # Skip sections with no associated teachers mapped

            # Sort tuples (e.g., by ID) before extracting to ensure consistent order? Optional.
            # sorted_teachers = sorted(list(teacher_details_set), key=lambda t: int(t[0]))
            sorted_teachers = list(teacher_details_set) # Keep order as is for now

            teacher_ids = [t[0] for t in sorted_teachers]
            teacher_names = [t[1] for t in sorted_teachers]
            teacher_codes = [t[2] for t in sorted_teachers]
            teacher_states = [t[3] for t in sorted_teachers]

            aggregated_teacher_data.append({
                constants.WLOAD_ID: wload_id,
                constants.WLS_SECTION_NAME: section_name,
                constants.TEACHER_IDS: ",".join(teacher_ids),
                constants.TEACHER_NAMES: ",".join(teacher_names),
                constants.TEACHER_CODES: ",".join(teacher_codes),
                constants.TEACHER_STATE: ",".join(teacher_states)
            })

        logging.info(f"Aggregated teacher info for {len(aggregated_teacher_data)} sections in WLoad ID: {wload_id}.")
        return aggregated_teacher_data

    except Exception as e:
        logging.error(f"Failed to fetch or process Teacher Groups for WLoad ID {wload_id}: {e}")
        return None # Return None on error

# --- Other processing functions remain as placeholders ---
# def process_and_prepare_updates(academic_terms, modules, wloads_data): ... 