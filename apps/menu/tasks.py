import os.path
import pickle

from celery import shared_task
from openpyxl import Workbook

from core.settings import GENERATED_FILES_DIRNAME


@shared_task(bind=True)
def gen_excel_task(self, data):
    full_menus_data = pickle.loads(data)
    workbook = Workbook()
    worksheet = workbook.active
    empty_cell = ''
    column_dimensions = {'A': 5, 'B': 12, 'C': 25, 'D': 30, 'E': 70, 'F': 10}

    for col, value in column_dimensions.items():
        worksheet.column_dimensions[col].width = value

    for m_num, menu in enumerate(full_menus_data, start=1):
        worksheet.append([m_num, menu.title, menu.description])
        for s_num, submenu in enumerate(menu.submenus, start=1):
            worksheet.append(
                [empty_cell, s_num, submenu.title, submenu.description])
            for d_num, dish in enumerate(submenu.dishes, start=1):
                worksheet.append(
                    [empty_cell, empty_cell, d_num, dish.title, dish.description, dish.price])
    if not os.path.exists(GENERATED_FILES_DIRNAME):
        os.mkdir(GENERATED_FILES_DIRNAME)
    file_path = os.path.join(GENERATED_FILES_DIRNAME, self.request.id)
    workbook.save(f'{file_path}.xlsx')
