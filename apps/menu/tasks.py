import pickle

from celery import shared_task
from openpyxl import Workbook


@shared_task(bind=True)
def gen_excel_task(self, data):
    full_menus_data = pickle.loads(data)
    workbook = Workbook()
    worksheet = workbook.active
    empty_cell = ''
    for menu in full_menus_data:
        worksheet.append([menu.id.hex, menu.title, menu.description])
        for submenu in menu.submenus:
            worksheet.append([empty_cell, submenu.id.hex,
                             submenu.title, submenu.description])
            for dish in submenu.dishes:
                worksheet.append(
                    [
                        empty_cell,
                        empty_cell,
                        dish.id.hex,
                        dish.title,
                        dish.description,
                        dish.price,
                    ]
                )
    workbook.save(f'{self.request.id}.xlsx')
