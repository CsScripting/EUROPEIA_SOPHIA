from src.variables.mod_variables import *


# 24 Colunas a Considerar em DataFrame

filter_data_schedules = [   v_course_code, 
                            v_course_name,  
                            v_mod_code, 
                            v_mod_name,
                            v_mod_id_uxxi,
                            v_year,
                            v_mod_typologie,
                            v_students_number,
                            v_activity_code,
                            v_activity_id,
                            v_student_group_code,
                            v_student_group,
                            v_student_group_name,
                            v_week_begin,
                            v_week_end, 
                            v_day, 
                            v_hourBegin_split,
                            v_minute_begin_split, 
                            v_hourEnd_split, 
                            v_minute_end_split,
                            v_teacher_name,
                            v_teacher_code,  
                            v_classroom_name, 
                            v_control_comun_mod,
                            v_center]


not_null_columns = [    v_course_code, 
                        v_course_name,  
                        v_mod_code, 
                        v_mod_name,
                        v_mod_id_uxxi,
                        v_year,
                        v_mod_typologie,
                        #v_students_number, SE NULO ATRIBUO VALOR DE 0
                        v_activity_code,
                        v_activity_id,
                        v_student_group_code,
                        v_student_group,
                        #v_student_group_name, NÃO EXISTE -  'SIN_NOMBRE_GRUPO_UXXI'
                        v_week_begin,
                        v_week_end, 
                        v_day, 
                        v_hourBegin_split,
                        v_minute_begin_split, 
                        v_hourEnd_split, 
                        v_minute_end_split,
                        # v_teacher_name,  NÃO EXISTE -  'SIN_PROF'
                        # v_teacher_code,  NÃO EXISTE -  'SIN_PROF'
                        # v_classroom_name, NÃO EXISTE -  'SIN_CLASS'
                        # v_control_comun_mod, NÃO EXISTE - 'No Aplica'
                        v_center
                        ]





agg_weeks = [   v_course_code,   # APENAS NÂO CONSIDERADAS AS SEMANAS
                v_course_name,  
                v_mod_code, 
                v_mod_name,
                v_mod_id_uxxi,
                v_year,
                v_mod_typologie,
                v_students_number,
                v_activity_code,
                v_activity_id,
                v_student_group_code,
                v_student_group,
                v_student_group_name,
                # v_week_begin,
                # v_week_end, 
                v_day, 
                v_hourBegin_split,
                v_minute_begin_split, 
                v_hourEnd_split, 
                v_minute_end_split,
                v_teacher_name,
                v_teacher_code,  
                v_classroom_name, 
                v_control_comun_mod,
                v_center]


agg_all_data = [    #v_course_code,        # ATIVIDADES QUE SE PASSEM NO MESMO: DIA ; HORA e DATAS  --> POSSO TER SESSIONES DIFERENTES MESMA ACTIVIDADE
                    #v_course_name,  
                    #v_mod_code, 
                    #v_mod_name,
                    #v_mod_id_uxxi,
                    #v_year,
                    #v_mod_typologie,
                    #v_students_number,
                    v_activity_code,
                    v_activity_id,
                    v_student_group_code,
                    v_student_group,
                    v_student_group_name,
                    #v_student_group_best,
                    #v_student_group_temp_BI, Imserido para gerir os casos de INGLES
                    v_weeks, ### ENTRETANTO SEMANAS JA AGREGADAS 
                    v_day, 
                    v_hourBegin_split,
                    v_minute_begin_split, 
                    v_hourEnd_split, 
                    v_minute_end_split,
                    #v_teacher_name,
                    #v_teacher_code,  
                    #v_classroom_name, 
                    #v_control_comun_mod
                    #v_center,
                    ]



filter_data_schedules_after_groups_bullet = [   v_course_code, 
                                                v_course_name,  
                                                v_mod_code, 
                                                v_mod_name,
                                                v_mod_id_uxxi,
                                                v_year,
                                                v_mod_typologie,
                                                v_students_number,
                                                v_activity_code,
                                                v_activity_id,
                                                v_student_group_code,
                                                v_student_group,
                                                v_student_group_name,
                                                v_student_group_temp_BI,
                                                v_student_group_best,
                                                v_weeks,
                                                v_day, 
                                                v_hourBegin_split,
                                                v_minute_begin_split, 
                                                v_hourEnd_split, 
                                                v_minute_end_split,
                                                v_teacher_name,
                                                v_teacher_code,  
                                                v_classroom_name, 
                                                v_control_comun_mod,
                                                v_center]


agg_teacher_classroom_data = [  v_course_code,        # ATIVIDADES QUE SE PASSEM NO MESMO: DIA ; HORA e DATAS  --> POSSO TER SESSIONES DIFERENTES MESMA ACTIVIDADE
                                v_course_name,  
                                v_mod_code, 
                                v_mod_name,
                                v_mod_id_uxxi,
                                v_year,
                                v_mod_typologie,
                                v_students_number,
                                v_activity_code,
                                v_activity_id,
                                v_student_group_code,
                                v_student_group,
                                v_student_group_name,
                                v_student_group_best,
                                v_student_group_temp_BI, #Inserido para gerir os casos de INGLES
                                v_weeks, ### ENTRETANTO SEMANAS JA AGREGADAS 
                                v_day, 
                                v_hourBegin_split,
                                v_minute_begin_split, 
                                v_hourEnd_split, 
                                v_minute_end_split,
                                #v_teacher_name,
                                #v_teacher_code,  
                                #v_classroom_name, 
                                v_control_comun_mod,
                                v_center,
                                ]


filter_data_bwp =  [    v_course_code,        # ATIVIDADES QUE SE PASSEM NO MESMO: DIA ; HORA e DATAS  --> POSSO TER SESSIONES DIFERENTES MESMA ACTIVIDADE
                        v_course_name,  
                        v_mod_code, 
                        v_mod_name,
                        v_mod_id_uxxi,
                        v_year,
                        v_mod_typologie,
                        v_id_uxxi_event,
                        v_activity_code,
                        v_activity_id,
                        v_student_group_code,
                        v_student_group,
                        v_student_group_name,
                        v_student_group_best,
                        v_plan_code_best_new,
                        v_student_number_uxxi,
                        v_weeks_general,
                        v_weeks_duration,
                        v_rule_weeks,
                        v_hours_duration_best,
                        v_session_best_number,
                        v_center,
                        v_control_comun_mod

                        ]



agg_mutual_modules_data =  [    #v_course_code,        # ATIVIDADES QUE SE PASSEM NO MESMO: DIA ; HORA e DATAS  --> POSSO TER SESSIONES DIFERENTES MESMA ACTIVIDADE
                                #v_course_name,  
                                #v_mod_code, 
                                #v_mod_name,
                                #v_mod_id_uxxi,
                                #v_year,
                                v_mod_typologie,
                                v_id_uxxi_event,
                                v_activity_code,
                                v_activity_id,
                                v_student_group_code,
                                v_student_group,
                                v_student_group_name,
                                #v_student_group_best,
                                #v_plan_code_best_new,
                                v_weeks_general,
                                v_weeks_duration,
                                v_rule_weeks,
                                v_hours_duration_best,
                                v_session_best_number,
                                #v_center
                        ]