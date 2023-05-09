import openpyxl
import time

# 엑셀 파일 열기
wb = openpyxl.load_workbook('C:/Users/정현제/Pictures/Desktop/230326/intersection.xlsx')

Car_Y = wb['coordinateY']


# 시작 열의 인덱스
start_col = 2

# 시작 행의 인덱스
start_row = 2

# 결과를 저장할 리스트
result_list = []

while True:
    # 지정한 행의 값을 가져와서 리스트에 추가
    row_values = []
    for idx, cell in enumerate(Car_Y[start_row]):
        if cell.value is None:
            row_values.append(None)
        else:
            row_values.append(cell.value)

    # 결과 리스트에 추가
    result_list.append(row_values)
    Car_Y_list = []

    # 결과 출력

    Car_Y_list = {index: value for index, value in enumerate(row_values) if value is not None}



    break

    # 일정 시간(1초) 대기 후 행 인덱스 조절
    # time.sleep(1)
    # print('------------------')
    # start_row += 2  # 2씩 증가