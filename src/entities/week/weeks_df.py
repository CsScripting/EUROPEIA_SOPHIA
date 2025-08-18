from src.utils.librarys import(
DataFrame
)
from src.variables.mod_variables import *


def weeks_df_from_json(weeks : list):

    df = DataFrame(columns = [v_id_best,
                              v_name_best])
    
    for i in range (len(weeks)):
    
        id_weeks = weeks[i][v_id_dto]
        name_weeks = weeks[i][v_start_date_dto]
        


        df = df.append({v_id_best : id_weeks,
                        v_name_best : name_weeks}, 
                        ignore_index = True)    

    

    return(df)


def parse_list_weeks_to_df (weeks : list):

    df = DataFrame(weeks)

    columns_used_from_json = [
                              v_id_dto,
                              v_start_date_dto,
                              ]
    

    #Filter DataFrame Values
    df = df [columns_used_from_json].copy()


    columns_to_rename = {   
                            
                            v_id_dto : v_id_best,
                            v_start_date_dto : v_name_best,
       
                        }

    df.rename(columns=columns_to_rename, inplace = True)

    
    return(df)