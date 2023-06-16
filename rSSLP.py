# -*- encoding: utf-8 -*-
'''
@filename        :rSSLP.py
@notion          :      
@time            :2023/05/04 21:41:25
@author          :spc
@version         :1.0
@Contact         :spacewe@outlook.com
@data set        :https://www2.isye.gatech.edu/~sahmed/siplib/sslp/sslp.html
'''

import os,sys
import numpy as np

def read_SSLP_sto(sto_apth):
    instance_scen_dict = {}
    f = open(sto_apth)               # 返回一个文件对象 
    lines = f.readlines()               # 调用文件的 readline()方法 
    linelist = lines[0].split()
    instance_scen_dict["NAME"] = linelist[1]
    secn_num = 0
    prob = []
    first_SC_loc = 0
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "SC" in linelist:
            first_SC_loc = i
            break
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "SC" in linelist:
            secn_num = secn_num + 1
            prob.append(float(linelist[3]))
    # 数据准确性验证,取消这个，以sto文件为准
    # if prob!=1/secn_num:
    #     print("instance secn data error p1!")
    #     sys.exit(0)
    start_one_secn = 0
    secn_data_num = 0
    secn_data_num_list = []
    secn_type = []
    secn_type_name = []
    sc_num = 0
    for i in range(first_SC_loc,len(lines)):
        linelist = lines[i].split()
        if "ENDATA" not in linelist:
            if "SC" in linelist:
                sc_num = sc_num + 1
                if secn_data_num>0:
                    secn_data_num_list.append(secn_data_num)
                start_one_secn = 1
                secn_data_num = 0
            if "SC" not in linelist and start_one_secn==1:
                secn_data_num = secn_data_num + 1
                if sc_num==1:
                    secn_type.append(linelist[0])
                # print(linelist)
                    if linelist[1] not in secn_type_name:
                        secn_type_name.append(linelist[1])
    if secn_data_num_list[0]!=np.mean(secn_data_num_list):
        print("instance secn data error p2!")
        sys.exit(0)

    secn_data_num = secn_data_num_list[0]
    instance_scen_dict["TYPE"] = secn_type
    instance_scen_dict["TYPE_NAME"] = secn_type_name
    instance_scen_dict["PROB"] = prob
    instance_scen_dict["SNUM"] = secn_num
    # 读取数据
    secn_data = np.zeros([secn_num,secn_data_num])
    secn_loc = 0
    for i in range(first_SC_loc,len(lines)):
        linelist = lines[i].split()
        if "ENDATA" not in linelist:
            if "SC" in linelist:
                data_loc = 0
                if i != first_SC_loc:
                    secn_loc = secn_loc + 1
            if "SC" not in linelist and len(linelist)==3:
                secn_data[secn_loc,data_loc] = int(linelist[2])
                data_loc = data_loc + 1
    instance_scen_dict['SCEN'] = secn_data
    # print(instance_scen_dict)
    f.close()
    return instance_scen_dict
def read_SSLP_cor(cor_path):
    instance_dict ={} # 存储测试用例

    f = open(cor_path)               # 返回一个文件对象 
    lines = f.readlines()               # 调用文件的 readline()方法 
    linelist = lines[0].split()
    if "NAME" in linelist:
        instance_dict["NAME"] = linelist[1]
    # 先读一遍，看有多少个约束，多少个变量
    Cstr_ind = [] # 约束的名称
    Cstr_GEL = [] # 约束是大于还是小于
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "G" in linelist or "E" in linelist or "L" in linelist:
            Cstr_ind.append(linelist[1])
            Cstr_GEL.append(linelist[0])
        if "COLUMNS" in linelist or "columns" in linelist:
            break
    Cstr_num = len(Cstr_ind) # 多少个约束
    instance_dict["CSTR_NAME"] = Cstr_ind
    instance_dict["CSTR_GEL"]  = Cstr_GEL
    instance_dict["CSTR_NUM"]  = Cstr_num
    

    var_start_loc = 0 
    var_end_loc = 0
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "RHS" in linelist:
            var_end_loc = i
        if "COLUMNS" in linelist:
            var_start_loc = i
    Var_Name = [] # 所有变量名
    Var_type = [] # 所有变量的类型
    intflag = 0
    for i in range(var_start_loc+1,var_end_loc):
        linelist = lines[i].split()
        if "\'INTORG\'" in linelist:
            intflag = 1
        if "\'INTEND\'" in linelist:
            intflag = 0
        if "\'MARKER\'" not in linelist:
            if linelist[0] not in Var_Name:
                Var_Name.append(linelist[0])
                if intflag == 1:
                    Var_type.append('Int')
                else:
                    Var_type.append('Cont')
    var_num = len(Var_Name) # 变量个数
    instance_dict["VAR_NAME"]  = Var_Name
    instance_dict["VAR_TYPE"]  = Var_type
    instance_dict["VAR_NUM"]  = var_num
    # 变量的上下界约束
    
    Var_LP = np.zeros(var_num) # 下界约束
    Var_UP = np.ones(var_num)*np.inf # 上界约束，初始为无穷大
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "UP" in linelist:
            # print(linelist)
            var_loc = Var_Name.index(linelist[2])
            Var_UP[var_loc] = int(linelist[3])
    instance_dict["VAR_LP"]  = Var_LP
    instance_dict["VAR_UP"]  = Var_UP
    # RHS值
    rhs_val = np.zeros(Cstr_num)
    rhs_name = []
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "rhs" in linelist:
            if len(linelist) ==5:
                first_rhs_cstr = linelist[1]
                first_rhs_cstr_loc = Cstr_ind.index(first_rhs_cstr)
                rhs_val[first_rhs_cstr_loc] = int(linelist[2])
                if first_rhs_cstr not in rhs_name:
                    rhs_name.append(first_rhs_cstr)  # 记录约束的名字
                second_rhs_cstr = linelist[3]
                second_rhs_cstr_loc = Cstr_ind.index(second_rhs_cstr)
                rhs_val[second_rhs_cstr_loc] = int(linelist[4])
                if second_rhs_cstr not in rhs_name:
                    rhs_name.append(second_rhs_cstr) 
            if len(linelist) ==3:
                first_rhs_cstr = linelist[1]
                first_rhs_cstr_loc = Cstr_ind.index(first_rhs_cstr)
                rhs_val[first_rhs_cstr_loc] = int(linelist[2])
                if first_rhs_cstr not in rhs_name:
                    rhs_name.append(first_rhs_cstr)
    instance_dict["RHS"]  = rhs_val
    instance_dict["RHS_NAME"]  = rhs_name
    Obj_cor = np.zeros(var_num)
    # 目标函数中每个变量的系数
    for i in range(var_start_loc+1,var_end_loc):
        linelist = lines[i].split()
        if "obj" in linelist:
            cur_var = linelist[0]
            cur_var_loc = Var_Name.index(cur_var)
            Obj_cor[cur_var_loc] = int(linelist[2])
    instance_dict["OBJ_COR"]  = Obj_cor
    Cstr_cor = np.zeros([Cstr_num,var_num])
    for i in range(var_start_loc+1,var_end_loc):
        linelist = lines[i].split()
        list_len = len(linelist)
        if "\'MARKER\'" not in linelist:
            if list_len == 5:
                if "obj" in linelist:
                    cstr_name_temp = linelist[3]
                    cstr_name_temp_loc = Cstr_ind.index(cstr_name_temp)
                    var_name_temp = linelist[0]
                    var_name_temp_loc = Var_Name.index(var_name_temp)
                    Cstr_cor[cstr_name_temp_loc,var_name_temp_loc] = int(linelist[4])
            if list_len == 3:
                cstr_name_temp = linelist[1]
                cstr_name_temp_loc = Cstr_ind.index(cstr_name_temp)
                var_name_temp = linelist[0]
                var_name_temp_loc = Var_Name.index(var_name_temp)
                Cstr_cor[cstr_name_temp_loc,var_name_temp_loc] = int(linelist[2])
    instance_dict["CSTR_COR"]  = Cstr_cor
    f.close() 
    # 字典准确性验证
    if len(instance_dict["CSTR_NAME"]) ==len(instance_dict["CSTR_GEL"]) and len(instance_dict["VAR_NAME"])==len(instance_dict["VAR_TYPE"]) and \
        np.size(instance_dict["VAR_LP"],0)==np.size(instance_dict["VAR_UP"],0) and len(instance_dict["CSTR_NAME"])==np.size(instance_dict["RHS"],0)\
        and np.size(instance_dict["OBJ_COR"],0)==np.size(instance_dict["CSTR_COR"],1):
        return instance_dict
    else:
        print("instance dict construct error!")
        sys.exit(0)

if __name__ == '__main__':
    cor_path = "D:\VScode_workspace\P1_Revise_more_theory\sslp_data\sslp_5_25_50.cor"
    sto_path = "D:\VScode_workspace\P1_Revise_more_theory\sslp_data\sslp_5_25_100.sto"
    # sslp_dict = read_SSLP_cor(cor_path)
    read_SSLP_sto(sto_path)
