from src.utils.librarys import(
DataFrame
)
from src.variables.mod_variables import *


def academic_year_df_from_json(academic_year : list):

    df = DataFrame(columns = [v_id_best,
                              v_name_best])

                               
    for item in academic_year:
    
        id_academic_year = item.get(v_id_dto)
        name_academic_year = item.get(v_name_dto)
        
        df.loc[len(df), df.columns] =   id_academic_year, \
                                        name_academic_year  

    
    return(df)