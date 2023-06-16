# -*- encoding: utf-8 -*-
'''
@filename        :bench2data.py
@notion          :      
@time            :2023/05/20 19:43:09
@author          :spc
@version         :1.0
@Contact         :spacewe@outlook.com
'''
import os,sys
import pickle
'''把数据文件转成字典存储，后边读取到gurobi中求解，再保存mps格式，保存求解结果'''
from rSSLP import read_SSLP_cor,read_SSLP_sto
from rSSTP import read_SSTP_cor,read_SSTP_sto
from rSIZE import read_SIZE_cor,read_SIZE_sto
import numpy as np
# 遍历SSLP文件夹，读出来存起来

def SSLP2data(sslppath,savepath):
    g = os.walk(sslppath)  
    # print(g)
    alread_list=[]
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            # 
            if ".cor" in file_name:
                inst_sslp = {}
                inst_name = file_name.split(".")[0]
                # print(inst_name)
                first_val_num = inst_name.split("_")[1]
                scen_num = inst_name.split("_")[3]
                cor_path = os.path.join(path, file_name) #模型路径
                sto_name = inst_name+".sto"
                sto_path = os.path.join(path, sto_name) # 对应的场景的路径
                # print(cor_path,sto_path)
                # 读数据去
                sto_data = read_SSLP_sto(sto_path)
                cor_data = read_SSLP_cor(cor_path)
                # print(sto_data,cor_data)
                inst_sslp["name"] = inst_name
                inst_sslp["first_val_num"] = first_val_num
                inst_sslp["scen_num"] = scen_num
                inst_sslp["sto"] = sto_data
                inst_sslp["cor"] = cor_data
                # print(inst_sslp)
                f_save = open(os.path.join(savepath, inst_name+'.pkl'), 'wb')
                pickle.dump(inst_sslp, f_save)
                f_save.close()
            # break

def SSTP2data(sstppath,savepath):
    # 先读cor文件
    g = os.walk(sstppath)      
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            # 
            if ".cor" in file_name:
                # inst_sstp = {}
                cor_path = os.path.join(path, file_name) #模型路径
                cor_data = read_SSTP_cor(cor_path)
                # print(cor_data)
    g1 = os.walk(sstppath)
    for path,dir_list,file_list in g1:  
        for file_name in file_list:  
            # 
            print(file_name)
            if ".sto" in file_name:
                inst_sstp = {}
                inst_name = file_name.split(".")[0]
                
                sto_path = os.path.join(path, file_name) # 对应的场景的路径
                sto_data = read_SSTP_sto(sto_path)
                if sto_data["SNUM"] == np.size(sto_data["SCEN"],0):
                    scen_num = sto_data["SNUM"]
                else:
                    print(r"场景数量不一致！")
                    sys.exit(0)
                save_name = "sstp_"+str(121)+"_S2_"+str(scen_num)
                inst_sstp["name"] = save_name
                inst_sstp["first_val_num"] = 121
                inst_sstp["scen_num"] = scen_num
                inst_sstp["sto"] = sto_data
                inst_sstp["cor"] = cor_data
                print(save_name)
                # print(inst_sslp)
                f_save = open(os.path.join(savepath, save_name+'.pkl'), 'wb')
                pickle.dump(inst_sstp, f_save)
                f_save.close()

def SIZE2Data(sizepath,savepath):
    # 先读cor文件
    g = os.walk(sizepath)      
    for path,dir_list,file_list in g:  
        for file_name in file_list:  
            # 
            if ".cor" in file_name:
                # inst_sstp = {}
                cor_path = os.path.join(path, file_name) #模型路径
                cor_data = read_SIZE_cor(cor_path)
    g1 = os.walk(sizepath)
    for path,dir_list,file_list in g1:  
        for file_name in file_list:  
            # 
            print(file_name)
            if ".sto" in file_name:
                inst_size = {}
                inst_name = file_name.split(".")[0]
                
                sto_path = os.path.join(path, file_name) # 对应的场景的路径
                sto_data = read_SIZE_sto(sto_path)
                if sto_data["SNUM"] == np.size(sto_data["SCEN"],0):
                    scen_num = sto_data["SNUM"]
                else:
                    print(r"场景数量不一致！")
                    sys.exit(0)
                save_name = "size_"+str(75)+"_75_"+str(scen_num)
                inst_size["name"] = save_name
                inst_size["first_val_num"] = 75
                inst_size["scen_num"] = scen_num
                inst_size["sto"] = sto_data
                inst_size["cor"] = cor_data
                print(save_name)
                # print(inst_sslp)
                f_save = open(os.path.join(savepath, save_name+'.pkl'), 'wb')
                pickle.dump(inst_size, f_save)
                f_save.close()
                # print(cor_data)
    pass
if __name__ == '__main__':
    sslppath = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\sslp_data"
    sstppath = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\sstp_data"
    sizepath = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\size_data"
    savepath = r"D:\VScode_workspace\P1_Revise_more_theory\CODE\bench2SP_data"
    # sslp_dict = read_SSLP_cor(cor_path)
    # SSLP2data(sslppath,savepath)
    # SSTP2data(sstppath,savepath)
    SIZE2Data(sizepath,savepath)
    print("1")