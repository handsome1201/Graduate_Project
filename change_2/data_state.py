import Speed_state
import CPU_state
import X_state
import Y_state
import numpy as np
import time


# ExcelReader 클래스의 인스턴스 생성
Speed_excel_reader = Speed_state.ExcelReader()
CPU_excel_reader = CPU_state.ExcelReader()
X_excel_reader = X_state.ExcelReader()
Y_excel_reader = Y_state.ExcelReader()
# 1초마다 result3_list의 값을 출력하는 루프



Speed_result_list = Speed_excel_reader.get_result_list()
Cpu_result_list = CPU_excel_reader.get_result_list()
X_result_list = X_excel_reader.get_result_list()
Y_result_list = Y_excel_reader.get_result_list()

car_count=len(Speed_result_list)



