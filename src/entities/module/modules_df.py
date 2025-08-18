from src.utils.librarys import(
DataFrame,
ast
)
from src.variables.mod_variables import *

def parse_list_mod_to_df (module : list, flag_need_id : bool = False):

    df = DataFrame(module)

    columns_used_from_json = [v_id_dto,
                              v_name_dto,
                              v_code_dto,
                              v_acronym_dto,
                              v_scientif_area_dto
                              ]
    
    if not df.empty:

        #Filter DataFrame Values
        df = df [columns_used_from_json].copy()

        #Extract values from object/Dict

        ## - SingleValues Dict: - ##

        #Module
        df[v_academic_area_best] =  df[v_scientif_area_dto].apply(lambda x: x.get(v_name_dto))

        #DropColumnsObjects

        columns_to_drop = [     
                            v_scientif_area_dto
                            
                        ]

        df.drop(columns=columns_to_drop, inplace=True)

        columns_to_rename = {   
                                v_id_dto : v_id_best,
                                v_name_dto : v_name_best, 
                                v_code_dto : v_code_best,
                                v_acronym_dto : v_acronym_best,
                                
                            }


        df.rename(columns=columns_to_rename, inplace = True)
        df[v_priority_mod_best] = ''

        order_columns_df = [v_id_best, 
                            v_name_best, 
                            v_acronym_best,
                            v_code_best,
                            v_priority_mod_best,
                            v_academic_area_best
                            ]

        df = df [order_columns_df].copy()

        if not flag_need_id:

            df.drop(columns=v_id_best, inplace=True)

        else:

            df.drop(columns=[v_name_best,v_acronym_best,v_priority_mod_best, v_academic_area_best], inplace=True)

    else:

        order_columns_df = [v_id_best, 
                            v_name_best, 
                            v_acronym_best,
                            v_code_best,
                            v_priority_mod_best,
                            v_academic_area_best
                            ]

        df = DataFrame(columns=order_columns_df)

        if not flag_need_id:

            df.drop(columns=v_id_best, inplace=True)

        else:

            df.drop(columns=[v_name_best,v_acronym_best,v_priority_mod_best, v_academic_area_best], inplace=True)


    return(df)