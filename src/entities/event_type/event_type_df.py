from src.utils.librarys import(
DataFrame
)
from src.variables.mod_variables import *


def event_type_df_from_json(event_type : list):

    df = DataFrame(columns = [v_id_best,
                              v_name_best])
    
    for i in range (len(event_type)):
    
        id_event_type = event_type[i][v_id_dto]
        name_event_type = event_type[i][v_name_dto]
        

        df.loc[len(df), df.columns] = id_event_type, name_event_type

    

    return(df)