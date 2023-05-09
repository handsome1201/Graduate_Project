import openpyxl
import time

class ExcelReader:
    def __init__(self):
        # 엑셀 파일 열기
        self.wb = openpyxl.load_workbook('C:/Users/정현제/Pictures/Desktop/230326/intersection.xlsx')

        self.Car_Speed = self.wb['speed']

        # 시작 열의 인덱스
        self.start_col = 2

        # 시작 행의 인덱스
        self.start_row = 3

        # 결과를 저장할 리스트
        self.result_list = []

        self.result3_list = []

    def get_result_list(self):
        # 지정한 행의 값을 가져와서 리스트에 추가
        row_values = []
        for idx, cell in enumerate(self.Car_Speed[self.start_row]):
            if cell.value is None:
                row_values.append(None)
            else:
                row_values.append(cell.value)

        # 결과 리스트에 추가
        self.result3_list.append(row_values)

        Car_Speed_list = { value for index, value in enumerate(row_values) if value is not None}

        self.start_row += 1

        # result3_list 반환
        return Car_Speed_list


