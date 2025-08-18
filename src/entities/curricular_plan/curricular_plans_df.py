from src.utils.librarys import(
DataFrame
)
from src.variables.mod_variables import *

def parse_list_plan_to_df (plan : list, flag_need_id : bool = False):

    df = DataFrame(plan)

    columns_used_from_json = [v_id_dto,
                              v_name_dto,
                              v_code_dto,
                              v_year_dto,
                              v_course_dto
                              ]
    

    if not df.empty:

        #Filter DataFrame Values
        df = df [columns_used_from_json].copy()

        #Extract values from object/Dict

        ## - SingleValues Dict: - ##

        #Course
        df[v_course_code_best] =  df[v_course_dto].apply(lambda x: x.get(v_code_dto))

        #DropColumnsObjects

        columns_to_drop = [     
                            v_course_dto
                            
                          ]

        df.drop(columns=columns_to_drop, inplace=True)

        columns_to_rename = {   
                                v_id_dto : v_id_best,
                                v_name_dto : v_name_best, 
                                v_code_dto : v_code_best,
                                v_year_dto : v_year_best,
                                  
                            }


        df.rename(columns=columns_to_rename, inplace = True)
        

        if not flag_need_id:


          order_columns_df = [ 
                              v_name_best, 
                              v_code_best,
                              v_year_best,
                              v_course_code_best
                              ]
          
        else:
          
          order_columns_df = [ 
                              v_id_best,
                              v_name_best, 
                              v_code_best,
                              v_year_best,
                              v_course_code_best
                              ]
          



        df = df [order_columns_df].copy()

    else:
       
      if not flag_need_id:


          order_columns_df = [ 
                              v_name_best, 
                              v_code_best,
                              v_year_best,
                              v_course_code_best
                              ]
          
      else:
          
          order_columns_df = [ 
                              v_id_best,
                              v_name_best, 
                              v_code_best,
                              v_year_best,
                              v_course_code_best
                              ]
       
      df = DataFrame(columns=order_columns_df)


    
    return(df)