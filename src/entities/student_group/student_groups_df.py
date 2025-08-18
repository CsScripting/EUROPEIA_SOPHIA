from src.utils.librarys import(
DataFrame
)
from src.variables.mod_variables import *

def parse_list_student_groups_to_df (st_group : list, flag_need_id : bool = False):

    df = DataFrame(st_group)

    columns_used_from_json = [v_id_dto,
                              v_name_dto,
                              v_code_dto,
                              v_curricular_plan_dto,
                              v_num_students_event_dto,
                              v_daily_limit_dto,
                              v_consecutive_limit_dto
                              ]
    

    if not df.empty:

        #Filter DataFrame Values
        df = df [columns_used_from_json].copy()

        #Extract values from object/Dict

        ## - SingleValues Dict: - ##

        #Course
        df[v_plan_code_best] =  df[v_curricular_plan_dto].apply(lambda x: x.get(v_code_dto))

        #DropColumnsObjects

        columns_to_drop = [     
                            v_curricular_plan_dto
                            
                        ]

        df.drop(columns=columns_to_drop, inplace=True)

        columns_to_rename = {   
                                v_id_dto : v_id_best,
                                v_name_dto : v_name_best, 
                                v_code_dto : v_code_best,
                                v_num_students_event_dto : v_students_number_best,
                                v_daily_limit_dto : v_daily_limit_best,
                                v_consecutive_limit_dto : v_consecutive_limit_best
                                
                            }


        df.rename(columns=columns_to_rename, inplace = True)
        

        order_columns_df = [ 
                            v_id_best, 
                            v_name_best, 
                            v_code_best,
                            v_plan_code_best,
                            v_students_number_best,
                            v_daily_limit_best,
                            v_consecutive_limit_best
                            ]


        df = df [order_columns_df].copy()

        if not flag_need_id:

            df.drop(columns=v_id_best, inplace=True)


        else:

            df.drop(columns=[v_code_best,v_plan_code_best,v_students_number_best, v_daily_limit_best, v_consecutive_limit_best], inplace=True)

    else:

        order_columns_df = [ 
                            v_id_best, 
                            v_name_best, 
                            v_code_best,
                            v_plan_code_best,
                            v_students_number_best,
                            v_daily_limit_best,
                            v_consecutive_limit_best
                            ]

        df = DataFrame(columns=order_columns_df)

        if not flag_need_id:

            df.drop(columns=v_id_best, inplace=True)


        else:

            df.drop(columns=[v_code_best,v_plan_code_best,v_students_number_best, v_daily_limit_best, v_consecutive_limit_best], inplace=True)


    
    return(df)