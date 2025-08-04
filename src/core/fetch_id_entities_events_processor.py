import pandas as pd
from src.api.client import ApiClient
import src.entities.academic_year.academic_year_df as dfAcadYear



def academic_year (df_event : pd.DataFrame, api_client: ApiClient):

    #1. Get Academic Year from API
    response = api_client._make_request("GET", "/AcademicYear")
    if isinstance(response, dict) and 'data' in response:
        academic_year_list = response['data']
        df_academic_year_best = dfAcadYear.academic_year_df_from_json(academic_year_list)
    
        df_academic_year_best.rename(columns={'name': 'academicYear_name',
                                              'id' : 'academicYear_id'}, inplace=True)

                 
        df_event = pd.merge(left=df_event, right=df_academic_year_best, on = 'academicYear_name', how='left', indicator = True)

        df_event_with_id = df_event[df_event['_merge'] == 'both'].copy() 
        df_event_without_id = df_event[df_event['_merge'] == 'left_only'].copy() 

        return (df_event_with_id, df_event_without_id )






