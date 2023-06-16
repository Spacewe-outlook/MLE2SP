# -*- encoding: utf-8 -*-
'''
@filename        :rSSTP.py
@notion          :      
@time            :2023/05/20 21:26:25
@author          :spc
@version         :1.0
@Contact         :spacewe@outlook.com
'''




import os,sys
import numpy as np
def read_SSTP_sto(sto_path):
    instance_scen_dict = {}
    f = open(sto_path)               # 返回一个文件对象 
    lines = f.readlines()               # 调用文件的 readline()方法 
    linelist = lines[0].split()
    instance_scen_dict["NAME"] = linelist[1]
    secn_num = 0
    prob = []
    first_SC_loc = 0
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "PERIOD2" in linelist:
            first_SC_loc = i
            break
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "PERIOD2" in linelist:
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
            if "PERIOD2" in linelist:
                sc_num = sc_num + 1
                if secn_data_num>0:
                    secn_data_num_list.append(secn_data_num)
                start_one_secn = 1
                secn_data_num = 0
            if "PERIOD2" not in linelist and start_one_secn==1 and len(linelist)==3:
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
            if "PERIOD2" in linelist:
                data_loc = 0
                if i != first_SC_loc:
                    secn_loc = secn_loc + 1
            if "PERIOD2" not in linelist and len(linelist)==3:
                secn_data[secn_loc,data_loc] = float(linelist[2])
                data_loc = data_loc + 1
    instance_scen_dict['SCEN'] = secn_data
    # print(instance_scen_dict)
    f.close()
    return instance_scen_dict
def read_SSTP_cor(cor_path):
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
        if "RHS" in linelist and len(linelist)==1:
            var_end_loc = i
        if "COLUMNS" in linelist and len(linelist)==1:
            var_start_loc = i
    Var_Name = [] # 所有变量名
    Var_type = [] # 所有变量的类型
    for i in range(var_start_loc+1,var_end_loc):
        linelist = lines[i].split()
        if "\'MARKER\'" not in linelist:
            if linelist[0] not in Var_Name:
                Var_Name.append(linelist[0])
                Var_type.append("Cont")
    var_num = len(Var_Name) # 变量个数
    instance_dict["VAR_NAME"]  = Var_Name
    instance_dict["VAR_TYPE"]  = Var_type
    instance_dict["VAR_NUM"]  = var_num
    # 变量的上下界约束
    
    Var_LP = np.zeros(var_num) # 下界约束
    Var_UP = np.ones(var_num)*np.inf # 上界约束，初始为无穷大
    instance_dict["VAR_LP"]  = Var_LP
    instance_dict["VAR_UP"]  = Var_UP

    # RHS值
    rhs_val = np.zeros(Cstr_num)
    rhs_name = []
    for i in range(len(lines)):
        linelist = lines[i].split()
        if "RHS" in linelist and len(linelist)!=1:
            if len(linelist) ==5:
                first_rhs_cstr = linelist[1]
                first_rhs_cstr_loc = Cstr_ind.index(first_rhs_cstr)
                rhs_val[first_rhs_cstr_loc] = float(linelist[2])
                if first_rhs_cstr not in rhs_name:
                    rhs_name.append(first_rhs_cstr)  # 记录约束的名字
                second_rhs_cstr = linelist[3]
                second_rhs_cstr_loc = Cstr_ind.index(second_rhs_cstr)
                rhs_val[second_rhs_cstr_loc] = float(linelist[4])
                if second_rhs_cstr not in rhs_name:
                    rhs_name.append(second_rhs_cstr) 
            if len(linelist) ==3:
                first_rhs_cstr = linelist[1]
                first_rhs_cstr_loc = Cstr_ind.index(first_rhs_cstr)
                rhs_val[first_rhs_cstr_loc] = float(linelist[2])
                if first_rhs_cstr not in rhs_name:
                    rhs_name.append(first_rhs_cstr)
    instance_dict["RHS"]  = rhs_val
    instance_dict["RHS_NAME"]  = rhs_name
    Obj_cor = np.zeros(var_num)
    # 目标函数中每个变量的系数
    numnum = 0
    for i in range(var_start_loc+1,var_end_loc):
        linelist = lines[i].split()
        if "OBJ" in linelist:
            cur_var = linelist[0]
            cur_var_loc = Var_Name.index(cur_var)
            Obj_cor[cur_var_loc] = float(linelist[2])
            numnum = numnum + 1
    # print(numnum)
    instance_dict["OBJ_COR"]  = Obj_cor
    Cstr_cor = np.zeros([Cstr_num,var_num])
    for i in range(var_start_loc+1,var_end_loc):
        linelist = lines[i].split()
        list_len = len(linelist)

        if list_len == 5:
            if "OBJ" in linelist:
                cstr_name_temp = linelist[3]
                cstr_name_temp_loc = Cstr_ind.index(cstr_name_temp)
                var_name_temp = linelist[0]
                var_name_temp_loc = Var_Name.index(var_name_temp)
                Cstr_cor[cstr_name_temp_loc,var_name_temp_loc] = float(linelist[4])
            else:
                cstr_name_temp = linelist[3]
                cstr_name_temp_loc = Cstr_ind.index(cstr_name_temp)
                var_name_temp = linelist[0]
                var_name_temp_loc = Var_Name.index(var_name_temp)
                Cstr_cor[cstr_name_temp_loc,var_name_temp_loc] = float(linelist[4])

                cstr_name_temp1 = linelist[1]
                cstr_name_temp_loc11 = Cstr_ind.index(cstr_name_temp1)
                var_name_temp1 = linelist[0]
                var_name_temp_loc1 = Var_Name.index(var_name_temp1)
                Cstr_cor[cstr_name_temp_loc11,var_name_temp_loc1] = float(linelist[2])
        if list_len == 3:
            cstr_name_temp = linelist[1]
            cstr_name_temp_loc = Cstr_ind.index(cstr_name_temp)
            var_name_temp = linelist[0]
            var_name_temp_loc = Var_Name.index(var_name_temp)
            Cstr_cor[cstr_name_temp_loc,var_name_temp_loc] = float(linelist[2])
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
    cor_path = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\storm\stormG2.cor"
    sto_path = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\storm\stormG2_125.sto"
    sstp_dict = read_SSTP_cor(cor_path)
    print(sstp_dict)
    sstp_sto_dict = read_SSTP_sto(sto_path)
    print(sstp_sto_dict)
