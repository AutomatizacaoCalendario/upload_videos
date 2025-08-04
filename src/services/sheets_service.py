from googleapiclient.errors import HttpError
from src import config

def update_calendar_entry(service_sheets, date_obj, video_link, class_name):
    """
    Encontra a célula correta na planilha e a atualiza com link/nome da aula.
    """
    # mapear mês inglês (python) -> português (sheets)
    month_map = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho', 'July': 'Julho',
        'August': 'Agosto', 'September': 'Setembro', 'October': 'Outubro',
        'November': 'Novembro', 'December': 'Dezembro'
    }
    month_name_en = date_obj.strftime('%B')
    sheet_name = month_map.get(month_name_en)
    
    day_number_str = str(date_obj.day)
    
    if not sheet_name:
        print(f"Mapping error: '{month_name_en}'")
        return

    print(f"Procurando dia {day_number_str} na aba '{sheet_name}'")

    try:
        # range suficiente pra cobrir todo o calendário do mês
        range_to_read = f"'{sheet_name}'!A1:G31"

        result = service_sheets.spreadsheets().values().get(
            spreadsheetId=config.SPREADSHEET_ID,
            range=range_to_read).execute()
        
        values = result.get('values', [])

        target_row_idx = -1
        target_col_idx = -1

        # encontra lin, col do dia
        for r_idx, row in enumerate(values):
            for c_idx, cell in enumerate(row):
                if cell.strip() == day_number_str:
                    target_row_idx = r_idx
                    target_col_idx = c_idx
                    break
            if target_row_idx != -1:
                break
        
        if target_row_idx == -1:
            print(f"ERRO: Não foi possível encontrar o dia {day_number_str} na aba '{sheet_name}'.")
            return

        # calcula a posição das células de link e nome da aula
        col_letter = chr(ord('A') + target_col_idx)
        link_cell_row = target_row_idx + 2  # +2 pq a API da google é 0-based
        aula_cell_row = target_row_idx + 3
        
        link_cell_range = f"'{sheet_name}'!{col_letter}{link_cell_row}"
        aula_cell_range = f"'{sheet_name}'!{col_letter}{aula_cell_row}"
        
        # garante que não vai sobrescrever
        current_data = service_sheets.spreadsheets().values().batchGet(
            spreadsheetId=config.SPREADSHEET_ID,
            ranges=[link_cell_range, aula_cell_range]
        ).execute().get('valueRanges', [])
        
        current_link_text = ""
        if len(current_data) > 0 and 'values' in current_data[0]:
            current_link_text = current_data[0]['values'][0][0]

        current_aula_text = ""
        if len(current_data) > 1 and 'values' in current_data[1]:
            current_aula_text = current_data[1]['values'][0][0]

        # anexa o novo conteúdo
        new_link_text = f"{current_link_text}\n{video_link}".strip()
        new_aula_text = f"{current_aula_text}\n{class_name}".strip()

        # prepara a atualização em lote
        update_body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [
                {'range': link_cell_range, 'values': [[new_link_text]]},
                {'range': aula_cell_range, 'values': [[new_aula_text]]}
            ]
        }
        
        service_sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=config.SPREADSHEET_ID,
            body=update_body
        ).execute()

        print(f"Success. Google Sheets: dia {day_number_str} / {sheet_name}.")

    except HttpError as err:
        print(f"Error: Google Sheets: {err}")