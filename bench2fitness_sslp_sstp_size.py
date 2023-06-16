import pickle,os,random,sys
import numpy as np
import time
from profilehooks import profile
'''根据sslp sstp size实例计算目标函数值'''
# from numba import jit

# 生成解，根据问题信息
# @jit
# @profile
def generate_sol(meta_infor_benchfunc,sol_num,stage):
    if stage == "2stage":
        sol_dim_x = meta_infor_benchfunc["x_num"]
        sol_dim_y = meta_infor_benchfunc["y_num"]
        sol_gen_x = np.zeros([sol_num,sol_dim_x])
        for i in range(sol_num):
            for j in range(sol_dim_x):
                if meta_infor_benchfunc["x_type"][j] =="Bin":
                    sol_gen_x[i,j] = np.random.randint(0,2)
                if meta_infor_benchfunc["x_type"][j] =="Int":
                    sol_gen_x[i,j] = np.random.randint(meta_infor_benchfunc["x_LP"][j],meta_infor_benchfunc["x_UP"][j])
                if meta_infor_benchfunc["x_type"][j] =="Cont":
                    sol_gen_x[i,j] = np.random.uniform(meta_infor_benchfunc["x_LP"][j],meta_infor_benchfunc["x_UP"][j])
        sol_gen_y = np.zeros([sol_num,meta_infor_benchfunc["scen_num"],sol_dim_y])
        for i in range(sol_num):
            for j in range(meta_infor_benchfunc["scen_num"]):
                for k in range(sol_dim_y):
                    if meta_infor_benchfunc["y_type"][k] =="Bin":
                        sol_gen_y[i,j,k] = np.random.randint(0,2)
                    if meta_infor_benchfunc["y_type"][k] =="Int":
                        sol_gen_y[i,j,k] = np.random.randint(meta_infor_benchfunc["y_LP"][k],meta_infor_benchfunc["y_UP"][k])
                    if meta_infor_benchfunc["y_type"][k] =="Cont":
                        sol_gen_y[i,j,k] = np.random.uniform(meta_infor_benchfunc["y_LP"][k],meta_infor_benchfunc["y_UP"][k])
        return sol_gen_x,sol_gen_y
# 目标函数 Size
# @jit
# @profile
def fitfunc_size(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen):
    # f_read = open(benchpkl_path, 'rb')
    # inst_dict = pickle.load(f_read)
    # f_read.close()
    # print(inst_dict)
    # 读第一阶段目标系数
    # 读第二阶段目标系数
    all_fitness = np.zeros(np.size(sol_gen_x,0))
    all_cstrst = np.zeros(np.size(sol_gen_x,0))
    all_fitness_onlyx = np.zeros(np.size(sol_gen_x,0))
    all_cv = np.zeros(np.size(sol_gen_x,0))
    for i in range(np.size(sol_gen_x,0)):
        cv_now = []
        first_x_num = meta_infor_benchfunc["x_num"]
        second_y_num = meta_infor_benchfunc["y_num"]
        scen_num = meta_infor_benchfunc["scen_num"]
        cstr_num = inst_dict["cor"]["CSTR_NUM"]
        cstr_name = inst_dict["cor"]["CSTR_NAME"]
        rhs_type_name = inst_dict["sto"]["TYPE_NAME"]
        Obj_cor=  inst_dict["cor"]["OBJ_COR"]
        obj_cor_x = Obj_cor[:first_x_num]
        # 适应不同大小的输入
        if y_scen>1:
            now_allsol_y = sol_gen_y[i,:,:]
            now_sol_x = sol_gen_x[i,:]
        else:
            now_allsol_y = sol_gen_y
            now_sol_x = sol_gen_x
        fitness_x = 0
        fitness_x = np.sum(obj_cor_x*now_sol_x)
        # for j in range(first_x_num):
        #     fitness_x= fitness_x +obj_cor_x[j]*now_sol_x[j]
        
        # 遍历每个场景
        obj_cor_y = Obj_cor[first_x_num:]
        fitness_all_y = 0 
        for k in range(scen_num):
            now_onesol_y = now_allsol_y[k,:]
            fitness_one_y = 0
            fitness_one_y = np.sum(obj_cor_y*now_onesol_y)
            # for yd in range(second_y_num):
            #     fitness_one_y = fitness_one_y + obj_cor_y[yd]*now_onesol_y[yd]
            fitness_all_y = fitness_all_y + inst_dict["sto"]["PROB"][k]*fitness_one_y
        all_fitness[i] = fitness_x+ fitness_all_y
        all_fitness_onlyx[i] = fitness_x
        # 处理约束
        all_cstr_cor = inst_dict["cor"]["CSTR_COR"]
        rhs_nowscen_num= 0
        rhs_nowscen_flag = 0
        for cons in range(cstr_num):
            now_cstr_cor = all_cstr_cor[cons,:]
            now_cstr_cor_x = now_cstr_cor[:first_x_num]
            now_cstr_cor_y = now_cstr_cor[first_x_num:]
            
            for sc in range(scen_num):
                now_cor_times_x = 0
                now_cor_times_y = 0
                
                now_onesol_y = now_allsol_y[sc,:]
                now_cor_times_x =np.sum(now_cstr_cor_x*now_sol_x)
                # for i_cons in range(first_x_num):
                #     now_cor_times_x = now_cor_times_x + now_cstr_cor_x[i_cons]*now_sol_x[i_cons]
                now_cor_times_y = np.sum(now_cstr_cor_y*now_onesol_y)
                # for i_cons in range(second_y_num):
                #     now_cor_times_y = now_cor_times_y + now_cstr_cor_y[i_cons]*now_onesol_y[i_cons]
                # if now_cor_times_x+now_cor_times_y>0:
                #     print(now_cor_times_x+now_cor_times_y)
                if cstr_name[cons] in rhs_type_name:
                    rhs_nowscen_flag = 1 
                    now_scen_rhs = inst_dict["sto"]["SCEN"][sc,rhs_nowscen_num]
                    # print("now_scen_rhs : ",now_scen_rhs)
                    if inst_dict["cor"]["CSTR_GEL"][cons] == "G":
                        if now_cor_times_x+now_cor_times_y<now_scen_rhs:
                            cv_now.append((now_scen_rhs-(now_cor_times_x+now_cor_times_y)))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "E":
                        if now_cor_times_x+now_cor_times_y!=now_scen_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-tolerance))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "L":
                        if now_cor_times_x+now_cor_times_y>now_scen_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-now_scen_rhs))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    
                else:
                    now_rhs = inst_dict["cor"]["RHS"][cons]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "G":
                        if now_cor_times_x+now_cor_times_y<now_rhs:
                            cv_now.append((now_rhs-(now_cor_times_x+now_cor_times_y)))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "E":
                        if now_cor_times_x+now_cor_times_y!=now_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-tolerance))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "L":
                        if now_cor_times_x+now_cor_times_y>now_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-now_rhs))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
            if rhs_nowscen_flag==1:
                rhs_nowscen_num=  rhs_nowscen_num+1 
                rhs_nowscen_flag = 0
        cv_now_max = np.max(cv_now)
        if cv_now_max>0:
            for icv in range(len(cv_now)):
                all_cv[i] =all_cv[i]+cv_now[icv]/cv_now_max
            all_cv[i] = all_cv[i]/len(cv_now)
        else:
            all_cv[i]=0
        # sys.exit(0)
        # print(all_fitness[i],all_cstrst[i],all_fitness_onlyx[i])
    return all_fitness,all_cstrst,all_fitness_onlyx,all_cv
# sslp的目标函数
# @jit
# @profile
def fitfunc_sslp(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen):
    # f_read = open(benchpkl_path, 'rb')
    # inst_dict = pickle.load(f_read)
    # f_read.close()
    all_fitness = np.zeros(np.size(sol_gen_x,0))
    all_cstrst = np.zeros(np.size(sol_gen_x,0))
    all_fitness_onlyx = np.zeros(np.size(sol_gen_x,0))
    all_cv = np.zeros(np.size(sol_gen_x,0))
    for i in range(np.size(sol_gen_x,0)):
        cv_now = []
        first_x_num = meta_infor_benchfunc["x_num"]
        second_y_num = meta_infor_benchfunc["y_num"]
        scen_num = meta_infor_benchfunc["scen_num"]
        cstr_num = inst_dict["cor"]["CSTR_NUM"]
        cstr_name = inst_dict["cor"]["CSTR_NAME"]
        rhs_type_name = inst_dict["sto"]["TYPE_NAME"]
        Obj_cor=  inst_dict["cor"]["OBJ_COR"]
        obj_cor_x = Obj_cor[:first_x_num]
        # 适应不同大小的输入
        if y_scen>1:
            now_allsol_y = sol_gen_y[i,:,:]
            now_sol_x = sol_gen_x[i,:]
        else:
            now_allsol_y = sol_gen_y
            now_sol_x = sol_gen_x
        fitness_x = 0
        fitness_x = np.sum(obj_cor_x*now_sol_x)
        # for j in range(first_x_num):
        #     fitness_x= fitness_x +obj_cor_x[j]*now_sol_x[j]
        
        # 遍历每个场景
        obj_cor_y = Obj_cor[first_x_num:]
        fitness_all_y = 0 
        for k in range(scen_num):
            now_onesol_y = now_allsol_y[k,:]
            fitness_one_y = 0
            fitness_one_y = np.sum(obj_cor_y*now_onesol_y)
            # for yd in range(second_y_num):
            #     fitness_one_y = fitness_one_y + obj_cor_y[yd]*now_onesol_y[yd]
            fitness_all_y = fitness_all_y + inst_dict["sto"]["PROB"][k]*fitness_one_y
        all_fitness[i] = fitness_x+ fitness_all_y
        all_fitness_onlyx[i] = fitness_x
        # 处理约束
        all_cstr_cor = inst_dict["cor"]["CSTR_COR"]
        rhs_nowscen_num= 0
        rhs_nowscen_flag = 0
        for cons in range(cstr_num):
            now_cstr_cor = all_cstr_cor[cons,:]
            now_cstr_cor_x = now_cstr_cor[:first_x_num]
            now_cstr_cor_y = now_cstr_cor[first_x_num:]
            
            for sc in range(scen_num):
                now_cor_times_x = 0
                now_cor_times_y = 0
                
                now_onesol_y = now_allsol_y[sc,:]
                now_cor_times_x = np.sum(now_cstr_cor_x*now_sol_x)
                now_cor_times_y = np.sum(now_cstr_cor_y*now_onesol_y)
                # for i_cons in range(first_x_num):
                #     now_cor_times_x = now_cor_times_x + now_cstr_cor_x[i_cons]*now_sol_x[i_cons]
                # for i_cons in range(second_y_num):
                #     now_cor_times_y = now_cor_times_y + now_cstr_cor_y[i_cons]*now_onesol_y[i_cons]
                # if now_cor_times_x+now_cor_times_y>0:
                #     print(now_cor_times_x+now_cor_times_y)
                if cstr_name[cons] in rhs_type_name:
                    rhs_nowscen_flag = 1 
                    now_scen_rhs = inst_dict["sto"]["SCEN"][sc,rhs_nowscen_num]
                    # print("now_scen_rhs : ",now_scen_rhs)
                    if inst_dict["cor"]["CSTR_GEL"][cons] == "G":
                        if now_cor_times_x+now_cor_times_y<now_scen_rhs:
                            cv_now.append((now_scen_rhs-(now_cor_times_x+now_cor_times_y)))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "E":
                        if now_cor_times_x+now_cor_times_y!=now_scen_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-tolerance))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "L":
                        if now_cor_times_x+now_cor_times_y>now_scen_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-now_scen_rhs))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    
                else:
                    now_rhs = inst_dict["cor"]["RHS"][cons]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "G":
                        if now_cor_times_x+now_cor_times_y<now_rhs:
                            cv_now.append((now_rhs-(now_cor_times_x+now_cor_times_y)))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "E":
                        if now_cor_times_x+now_cor_times_y!=now_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-tolerance))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "L":
                        if now_cor_times_x+now_cor_times_y>now_rhs:
                            cv_now.append((now_cor_times_x+now_cor_times_y-now_rhs))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
            if rhs_nowscen_flag==1:
                rhs_nowscen_num=  rhs_nowscen_num+1 
                rhs_nowscen_flag = 0
        cv_now_max = np.max(cv_now)
        if cv_now_max>0:
            for icv in range(len(cv_now)):
                all_cv[i] =all_cv[i]+cv_now[icv]/cv_now_max
            all_cv[i] = all_cv[i]/len(cv_now)
        else:
            all_cv[i]=0
        # sys.exit(0)
        # print(all_fitness[i],all_cstrst[i],all_fitness_onlyx[i])
    return all_fitness,all_cstrst,all_fitness_onlyx,all_cv

# sstp的目标函数
# @jit
# @profile
def fitfunc_sstp(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen):
    # f_read = open(benchpkl_path, 'rb')
    # inst_dict = pickle.load(f_read)
    # f_read.close()
    all_fitness = np.zeros(np.size(sol_gen_x,0))
    all_cstrst = np.zeros(np.size(sol_gen_x,0))
    all_cv = np.zeros(np.size(sol_gen_x,0))
    all_fitness_onlyx = np.zeros(np.size(sol_gen_x,0))
    for i in range(np.size(sol_gen_x,0)):
        cv_now = []
        first_x_num = meta_infor_benchfunc["x_num"]
        second_y_num = meta_infor_benchfunc["y_num"]
        scen_num = meta_infor_benchfunc["scen_num"]
        cstr_num = inst_dict["cor"]["CSTR_NUM"]
        cstr_name = inst_dict["cor"]["CSTR_NAME"]
        rhs_type_name = inst_dict["sto"]["TYPE_NAME"]
        Obj_cor=  inst_dict["cor"]["OBJ_COR"]
        obj_cor_x = Obj_cor[:first_x_num]
        if y_scen>1:
            now_allsol_y = sol_gen_y[i,:,:]
            now_sol_x = sol_gen_x[i,:]
        else:
            now_allsol_y = sol_gen_y
            now_sol_x = sol_gen_x
        fitness_x = 0
        fitness_x = np.sum(obj_cor_x*now_sol_x)
        # for j in range(first_x_num):
        #     fitness_x= fitness_x +obj_cor_x[j]*now_sol_x[j]
        
        # 遍历每个场景

        obj_cor_y = Obj_cor[first_x_num:]
        fitness_all_y = 0 
        for k in range(scen_num):
            now_onesol_y = now_allsol_y[k,:]
            fitness_one_y = 0
            fitness_one_y = np.sum(obj_cor_y*now_onesol_y)
            # for yd in range(second_y_num):
            #     fitness_one_y = fitness_one_y + obj_cor_y[yd]*now_onesol_y[yd]
            fitness_all_y = fitness_all_y + inst_dict["sto"]["PROB"][k]*fitness_one_y
        all_fitness[i] = fitness_x+ fitness_all_y
        all_fitness_onlyx[i] = fitness_x
         # 处理约束
        all_cstr_cor = inst_dict["cor"]["CSTR_COR"]
        rhs_nowscen_num= 0
        rhs_nowscen_flag = 0
        for cons in range(cstr_num):
            now_cstr_cor = all_cstr_cor[cons,:]
            now_cstr_cor_x = now_cstr_cor[:first_x_num]
            now_cstr_cor_y = now_cstr_cor[first_x_num:]
            
            for sc in range(scen_num):
                now_cor_times_x = 0
                now_cor_times_y = 0
                
                now_onesol_y = now_allsol_y[sc,:]
                now_cor_times_x = np.sum(now_cstr_cor_x*now_sol_x)
                now_cor_times_y = np.sum(now_cstr_cor_y*now_onesol_y)
                # for i_cons in range(first_x_num):
                #     now_cor_times_x = now_cor_times_x + now_cstr_cor_x[i_cons]*now_sol_x[i_cons]
                # for i_cons in range(second_y_num):
                #     now_cor_times_y = now_cor_times_y + now_cstr_cor_y[i_cons]*now_onesol_y[i_cons]
                # if now_cor_times_x+now_cor_times_y>0:
                #     print(now_cor_times_x+now_cor_times_y)
                if cstr_name[cons] in rhs_type_name:
                    rhs_nowscen_flag = 1 
                    now_scen_rhs = inst_dict["sto"]["SCEN"][sc,rhs_nowscen_num]
                    # print("now_scen_rhs : ",now_scen_rhs)
                    if inst_dict["cor"]["CSTR_GEL"][cons] == "G":
                        if now_cor_times_x+now_cor_times_y<now_scen_rhs:
                            cv_now.append(abs(now_scen_rhs-(now_cor_times_x+now_cor_times_y)))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "E":
                        if now_cor_times_x+now_cor_times_y!=now_scen_rhs:
                            cv_now.append(abs(now_cor_times_x+now_cor_times_y-tolerance))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "L":
                        if now_cor_times_x+now_cor_times_y>now_scen_rhs:
                            cv_now.append(abs(now_cor_times_x+now_cor_times_y-now_scen_rhs))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    
                else:
                    now_rhs = inst_dict["cor"]["RHS"][cons]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "G":
                        if now_cor_times_x+now_cor_times_y<now_rhs:
                            cv_now.append(abs(now_rhs-(now_cor_times_x+now_cor_times_y)))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "E":
                        if now_cor_times_x+now_cor_times_y!=now_rhs:
                            cv_now.append(abs(now_cor_times_x+now_cor_times_y-tolerance))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
                    if inst_dict["cor"]["CSTR_GEL"][cons]  == "L":
                        if now_cor_times_x+now_cor_times_y>now_rhs:
                            cv_now.append(abs(now_cor_times_x+now_cor_times_y-now_rhs))
                            # all_cstrst[i] = all_cstrst[i]+10*inst_dict["sto"]["PROB"][sc]
        
            if rhs_nowscen_flag==1:
                rhs_nowscen_num=  rhs_nowscen_num+1 
                rhs_nowscen_flag = 0
        cv_now_max = np.max(cv_now)
        if cv_now_max>0:
            for icv in range(len(cv_now)):
                all_cv[i] =all_cv[i]+cv_now[icv]/cv_now_max
            all_cv[i] = all_cv[i]/len(cv_now)
        else:
            all_cv[i]=0
        # sys.exit(0)
        # print(all_fitness[i],all_cstrst[i],all_fitness_onlyx[i])
    return all_fitness,all_cstrst,all_fitness_onlyx,all_cv
# @profile
def fitfunc_smlp(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen):
    # 根据类型调用不同的函数
    inst_type = meta_infor_benchfunc["type"]

    if "sstp" in inst_type:
        all_fitness,all_cstrst,all_fitness_onlyx,all_cv = fitfunc_sstp(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen)
        return all_fitness,all_cstrst,all_fitness_onlyx,all_cv
    elif "sslp" in inst_type:
        all_fitness,all_cstrst,all_fitness_onlyx,all_cv = fitfunc_sslp(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen)
        return all_fitness,all_cstrst,all_fitness_onlyx,all_cv
    elif "size" in inst_type:
        all_fitness,all_cstrst,all_fitness_onlyx,all_cv = fitfunc_size(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen)
        return all_fitness,all_cstrst,all_fitness_onlyx,all_cv
    else:
        print(r"fitfunc_smlp : 问题类型不匹配！")
        sys.exit(0)
    

# 根据实例文件，获得解构建信息
# @jit
# @profile
def get_metadata(inst_dict,file_name):
    meta_infor_benchfunc = {}
    if "size" in file_name:
        # print(inst_dict)
        # 第一阶段变量长度
        all_val_len = len((inst_dict["cor"]["VAR_NAME"]))
        first_x_type = []
        first_bin = 0
        for i in range(inst_dict["first_val_num"]):
            if inst_dict["cor"]["VAR_TYPE"][i] == "Int":
                first_x_type.append("Bin")
                first_bin = first_bin + 1
            elif inst_dict["cor"]["VAR_TYPE"][i] == "DIS":
                first_x_type.append("Int")
            else:
                first_x_type.append("Cont")
        second_y_type = []
        second_bin = 0
        for i in range(all_val_len -inst_dict["first_val_num"]):
            if inst_dict["cor"]["VAR_TYPE"][i+inst_dict["first_val_num"]] == "Int":
                second_y_type.append("Bin")
                second_bin = second_bin + 1
            elif inst_dict["cor"]["VAR_TYPE"][i+inst_dict["first_val_num"]] == "DIS":
                second_y_type.append("Int")
            else:
                second_y_type.append("Cont")
        # print(all_val_len)
        first_x_LP = np.zeros(inst_dict["first_val_num"])
        first_x_UP = np.zeros(inst_dict["first_val_num"])
        for i in range(inst_dict["first_val_num"]):
            if i<first_bin:
                first_x_UP[i] = 1
            else:
                first_x_UP[i] = 1000 # 一个大数
        second_y_LP = np.zeros(all_val_len - inst_dict["first_val_num"])
        second_y_UP = np.zeros(all_val_len - inst_dict["first_val_num"])
        for i in range(all_val_len - inst_dict["first_val_num"]):
            if i<second_bin:
                second_y_UP[i] = 1
            else:
                second_y_UP[i] = 500 # 一个大数
        
        meta_infor_benchfunc["type"] = inst_dict["name"]
        meta_infor_benchfunc["x_num"] = inst_dict["first_val_num"]#first_x_num
        meta_infor_benchfunc["y_num"] = all_val_len - inst_dict["first_val_num"]
        meta_infor_benchfunc["scen_dim"] = np.size(inst_dict["sto"]["SCEN"],1)
        meta_infor_benchfunc["scen_num"] = inst_dict["scen_num"]
        meta_infor_benchfunc["x_type"] = first_x_type
        meta_infor_benchfunc["y_type"] = second_y_type
        meta_infor_benchfunc["x_LP"] = first_x_LP
        meta_infor_benchfunc["y_LP"] = second_y_LP
        meta_infor_benchfunc["x_UP"] = first_x_UP
        meta_infor_benchfunc["y_UP"] = second_y_UP
        # print(meta_infor_benchfunc)
    if "sslp" in file_name:
        # print(inst_dict)
        first_x_num = int(inst_dict["first_val_num"])
        all_val_len = len(inst_dict["cor"]["VAR_NAME"])
        first_x_type = []
        for i in range(first_x_num):
            if inst_dict["cor"]["VAR_TYPE"][i] == "Int":
                first_x_type.append("Bin")
            elif inst_dict["cor"]["VAR_TYPE"][i] == "DIS":
                first_x_type.append("Int")
            else:
                first_x_type.append("Cont")
        second_y_type = []
        second_bin = 0
        for i in range(all_val_len -first_x_num):
            if inst_dict["cor"]["VAR_TYPE"][i+first_x_num] == "Int":
                second_y_type.append("Bin")
                second_bin = second_bin + 1
            elif inst_dict["cor"]["VAR_TYPE"][i+first_x_num] == "DIS":
                second_y_type.append("Int")
            else:
                second_y_type.append("Cont")
        first_x_LP = np.zeros(first_x_num)
        first_x_UP = np.zeros(first_x_num)
        for i in range(first_x_num):
            first_x_UP[i] = 1 # 类型已经确定了，对于全二进制遍历，生成解的地方这个不影响
        second_y_LP = np.zeros(all_val_len - first_x_num)
        second_y_UP = np.zeros(all_val_len - first_x_num)
        for i in range(all_val_len - first_x_num):
            if i<second_bin:
                second_y_UP[i] = 1
            else:
                second_y_UP[i] = 500 # 一个大数
        meta_infor_benchfunc["type"] = inst_dict["name"]
        meta_infor_benchfunc["x_num"] = first_x_num#first_x_num
        meta_infor_benchfunc["y_num"] = all_val_len - first_x_num
        meta_infor_benchfunc["scen_dim"] = np.size(inst_dict["sto"]["SCEN"],1)
        meta_infor_benchfunc["scen_num"] = int(inst_dict["scen_num"])
        meta_infor_benchfunc["x_type"] = first_x_type
        meta_infor_benchfunc["y_type"] = second_y_type
        meta_infor_benchfunc["x_LP"] = first_x_LP
        meta_infor_benchfunc["y_LP"] = second_y_LP
        meta_infor_benchfunc["x_UP"] = first_x_UP
        meta_infor_benchfunc["y_UP"] = second_y_UP
    if "sstp" in file_name:
        # print(inst_dict)
        first_x_num = int(inst_dict["first_val_num"])
        all_val_len = len((inst_dict["cor"]["VAR_NAME"]))
        first_x_type = []
        for i in range(first_x_num):
            if inst_dict["cor"]["VAR_TYPE"][i] == "Int":
                first_x_type.append("Bin")
            elif inst_dict["cor"]["VAR_TYPE"][i] == "DIS":
                first_x_type.append("Int")
            else:
                first_x_type.append("Cont")
        second_y_type = []
        for i in range(all_val_len -first_x_num):
            if inst_dict["cor"]["VAR_TYPE"][i+first_x_num] == "Int":
                second_y_type.append("Bin")
            elif inst_dict["cor"]["VAR_TYPE"][i+first_x_num] == "DIS":
                second_y_type.append("Int")
            else:
                second_y_type.append("Cont")
        first_x_LP = np.zeros(first_x_num)
        first_x_UP = np.zeros(first_x_num)
        for i in range(first_x_num):
            first_x_UP[i] = 500 # 一个大数
        second_y_LP = np.zeros(all_val_len - first_x_num)
        second_y_UP = np.zeros(all_val_len - first_x_num)
        for i in range(all_val_len - first_x_num):
            second_y_UP[i] = 500 # 一个大数
        meta_infor_benchfunc["type"] = inst_dict["name"]
        meta_infor_benchfunc["x_num"] = first_x_num#first_x_num
        meta_infor_benchfunc["y_num"] = all_val_len - first_x_num
        meta_infor_benchfunc["scen_dim"] = np.size(inst_dict["sto"]["SCEN"],1)
        meta_infor_benchfunc["scen_num"] = int(inst_dict["scen_num"])
        meta_infor_benchfunc["x_type"] = first_x_type
        meta_infor_benchfunc["y_type"] = second_y_type
        meta_infor_benchfunc["x_LP"] = first_x_LP
        meta_infor_benchfunc["y_LP"] = second_y_LP
        meta_infor_benchfunc["x_UP"] = first_x_UP
        meta_infor_benchfunc["y_UP"] = second_y_UP
    return meta_infor_benchfunc

if __name__ == '__main__':
    drlp_pkl_path = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\test"
    g = os.walk(drlp_pkl_path)  
    os.chdir(sys.path[0]) # 定位到当前路径
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            # if "sstp" in file_name:
            f_read = open(os.path.join(path, file_name), 'rb')
            inst_dict = pickle.load(f_read)
            f_read.close()
            print(r"实例：",file_name)
            meta_infor_benchfunc = get_metadata(inst_dict,file_name)
            sol_num = 10
            stage = "2stage"
            tolerance = 10e-4
            y_scen = sol_num
            sol_gen_x,sol_gen_y = generate_sol(meta_infor_benchfunc,sol_num,stage)
            # print(sol_gen_x,sol_gen_y)
            start = time.time()
            all_fitness,all_cstrst,all_fitness_onlyx,all_cv = fitfunc_smlp(inst_dict,meta_infor_benchfunc,sol_gen_x,sol_gen_y,tolerance,y_scen)
            print(all_fitness,"\n",all_cstrst,"\n",all_fitness_onlyx,"\n",all_cv)
            end = time.time()
            print("time : ",end-start)
        # break