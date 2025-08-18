from src.utils.librarys import(
DataFrame
)
from src.variables.mod_variables import *


def parse_list_typologies_to_df (typologie : list, flag_need_id : bool = False):

    df = DataFrame(typologie)

    columns_used_from_json = [
                              v_id_dto,
                              v_name_dto,
                              v_description_dto
                              ]
    
    if not df.empty:
    

        #Filter DataFrame Values
        df = df [columns_used_from_json].copy()


        columns_to_rename = {   
                                
                                v_id_dto : v_id_best,
                                v_name_dto : v_name_best,
                                v_description_dto : v_description_typologie_best,
        
                            }


        df.rename(columns=columns_to_rename, inplace = True)

        if not flag_need_id:

            df.drop(columns=v_id_best, inplace=True)

        else:

            df.drop(columns=[v_description_typologie_best], inplace=True)

    else:

        df_columns = [v_id_best, v_name_best, v_description_typologie_best]

        df = DataFrame(columns=df_columns)

        if not flag_need_id:

            df.drop(columns=v_id_best, inplace=True)

        else:

            df.drop(columns=[v_description_typologie_best], inplace=True)
  

    return(df)