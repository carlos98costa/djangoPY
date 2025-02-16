import mysql.connector
from mysql.connector import Error
import PySimpleGUI as sg
import datetime
import imdb

ia = imdb.IMDb()

def create_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456',
            database='new_schema',
        )
    except Error as err:
        sg.popup_error(f"Error: '{err}'")
        return None

def read_query(conexao, query):
    cursor = conexao.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Error as err:
        sg.popup_error(f"Error: '{err}'")
        return []

def update_series_list(window, conexao):
    results = read_query(conexao, "SELECT nome_filme_serie FROM filmesseries ORDER BY nome_filme_serie ASC;")
    series_list = [i[0] for i in results]
    window['-LISTSERIES-'].update(series_list)

def make_window1():
    sg.theme('Dark')
    layout_1 = [[sg.T('Lista de Animes/Filmes/Series')],
                [sg.LB(values=[], size=(24, 10), k='-LISTSERIES-'), sg.Button('Atualizar')],
                [sg.Button('Adicionar'), sg.Button('Editar'), sg.Button('Deletar'), sg.Button('Sair')]]
    return sg.Window('CarBOT', layout=layout_1, finalize=True)

def make_window2():
    sg.theme('Dark')
    layout_2 = [[sg.T('Adicionar Serie')],
                [sg.T('Informe o título:'), sg.Input(size=(23, 1), key='-TITULO-')],
                [sg.T('Informe o Status'), sg.Combo(['Cancelada', 'Em andamento', 'Finalizada'], default_value='Em andamento', key='-KSTATUS-')],
                [sg.T('Data lançamento novos episódios:'),
                 sg.T('D'), sg.Combo([f'{i:02}' for i in range(1, 32)], default_value='01', key='-KDIA-'),
                 sg.T('M'), sg.Combo([f'{i:02}' for i in range(1, 13)], default_value='01', key='-KMES-'),
                 sg.T('A'), sg.Combo([str(i) for i in range(2022, 2031)], default_value='2022', key='-KANO-')],
                [sg.T('Nota'), sg.Combo([str(i) for i in range(1, 11)], default_value='1', key='-KNOTA-')],
                [sg.Button('Adicionar'), sg.Button('Voltar')]]
    return sg.Window('Adicionar Série', layout=layout_2, finalize=True)

def make_window3(serie):
    sg.theme('Dark')
    layout_3 = [[sg.T('Editar Série')],
                [sg.T('ID:'), sg.Input(serie[0], disabled=True, key='-IDSAVE-')],
                [sg.T('Título:'), sg.Input(serie[1], key='-TITEDIT-')],
                [sg.T('Informe o Status'), sg.Combo(['Cancelada', 'Em andamento', 'Finalizada'], default_value=serie[4], key='-STATUSEDIT-')],
                [sg.T('Data próximo lançamento:'), sg.Input(serie[2].strftime('%d/%m/%Y'), key='-DATAEDIT-')],
                [sg.T('Nota'), sg.Combo([str(i) for i in range(1, 11)], default_value=str(serie[3]), key='-NOTAEDIT-')],
                [sg.Button('Salvar'), sg.Button('Voltar')]]
    return sg.Window('Editar Série', layout=layout_3, finalize=True)

def add_series(conexao, values):
    titulo = values['-TITULO-']
    status = values['-KSTATUS-']
    dia = values['-KDIA-']
    mes = values['-KMES-']
    ano = values['-KANO-']
    data = f'{dia}/{mes}/{ano}'
    newData = datetime.datetime.strptime(data, '%d/%m/%Y').date()
    newNota = values['-KNOTA-']

    if not titulo:
        sg.popup_error("O título não pode estar vazio.")
        return

    comando = 'INSERT INTO filmesseries (nome_filme_serie, StatusFilmeSerie, dataFilmeSerie, FilmesSeriesNota) VALUES (%s, %s, %s, %s);'
    cursor = conexao.cursor()
    cursor.execute(comando, (titulo, status, newData, newNota,))
    conexao.commit()
    sg.popup('Dados inseridos com sucesso!')

def edit_series(conexao, values):
    idNew = values['-IDSAVE-']
    nameNew = values['-TITEDIT-']
    statusNew = values['-STATUSEDIT-']
    dataNew = values['-DATAEDIT-']
    newNota = values['-NOTAEDIT-']

    if not nameNew:
        sg.popup_error("O título não pode estar vazio.")
        return

    comando = f'UPDATE filmesseries SET nome_filme_serie= %s, StatusFilmeSerie= %s, dataFilmeSerie= %s, FilmesSeriesNota= %s WHERE idFilmesSeries = %s;'
    cursor = conexao.cursor()
    cursor.execute(comando, (nameNew, statusNew, dataNew, newNota, idNew))
    conexao.commit()
    sg.popup('Dados atualizados com sucesso!')

def delete_series(conexao, title):
    comando = f'DELETE FROM filmesseries WHERE nome_filme_serie = %s;'
    cursor = conexao.cursor()
    cursor.execute(comando, (title,))
    conexao.commit()
    sg.popup('Dados deletados com sucesso!')

def main():
    conexao = create_connection()
    if conexao is None:
        return

    janela1 = make_window1()
    janela2 = None  # Inicializa janela2 como None
    janela3 = None  # Inicializa janela3 como None
    update_series_list(janela1, conexao)

    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED or event == 'Sair':
            break

        if window == janela1 and event == 'Atualizar':
            update_series_list(window, conexao)

        if window == janela1 and event == 'Adicionar':
            janela2 = make_window2()
            janela1.hide()

        if window == janela1 and event == 'Deletar':
            title = values['-LISTSERIES-']
            if title:
                delete_series(conexao, title[0])
                update_series_list(janela1, conexao)

        if window == janela2 and event == 'Voltar':
            if janela2:  # Verifica se janela2 foi criada
                janela2.hide()
                janela1.un_hide()

        if window == janela2 and event == 'Adicionar':
            add_series(conexao, values)
            update_series_list(janela1, conexao)
            janela2.hide()
            janela1.un_hide()

        if window == janela1 and event == 'Editar':
            title = values['-LISTSERIES-']
            if title:
                results = read_query(conexao, f'SELECT * FROM filmesseries WHERE nome_filme_serie = "{title[0]}";')
                if results:
                    janela3 = make_window3(results[0])
                    janela1.hide()

        if window == janela3 and event == 'Voltar':
            if janela3:  # Verifica se janela3 foi criada
                janela3.hide()
                janela1.un_hide()

        if window == janela3 and event == 'Salvar':
            edit_series(conexao, values)
            update_series_list(janela1, conexao)
            janela3.hide()
            janela1.un_hide()

    conexao.close()

if __name__ == "__main__":
    main()