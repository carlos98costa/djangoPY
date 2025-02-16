import mysql.connector
from mysql.connector import Error
import PySimpleGUI as sg
import datetime
import imdb

ia = imdb.IMDb()

conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    database='new_schema',
)

cursor = conexao.cursor()
def read_query(conexao, query):
    cursor = conexao.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

puxarDados = """
                SELECT *
                FROM filmesseries
                ORDER BY nome_filme_serie ASC;
                """
results = read_query(conexao, puxarDados)

listaSeries = []
for i in results:
    listaSeries.append(i[1])
listNotas = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
listStatus = ['Cancelada', 'Em andamento', 'Finalizada']
listDays = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
            '10', '11', '12', '13', '14', '15', '16', '17', '18',
            '19', '20', '21', '22', '23', '24', '25', '26', '27',
            '28', '29', '30', '31']
listMes = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
            '10', '11', '12']
listAnos = ['2022', '2023', '2024', '2025', '2026', '2027', '2028',
            '2029', '2030']

def update_series_list(window, conexao):
    results = read_query(conexao, "SELECT nome_filme_serie FROM filmesseries ORDER BY nome_filme_serie ASC;")
    series_list = [i[0] for i in results]
    window['-LISTSERIES-'].update(series_list)

def make_window1():
    sg.theme('Dark')
    layout_1 = [[sg.T('Lista de Animes/Filmes/Series')],
                [sg.LB(values=listaSeries, size=(24,10), k='-LISTSERIES-'), sg.Button('Atualizar')],
                [sg.Button('Adicionar'), sg.Button('Editar'), sg.Button('Deletar') ,sg.Button('Sair')]]
    return sg.Window('CarBOT', layout=layout_1, finalize=True)

def make_window2():
    sg.theme('Dark')
    layout_2 = [[sg.T('Adicionar Serie')],
                    [sg.T('Informe o titulo ao lado:'), sg.Input(size=(23, 1), enable_events=True, key='-TITULO-')],
                    [sg.T('Informe o Status'), sg.Combo(listStatus, default_value=listStatus[0], k='-KSTATUS-'), sg.Button('Selecionar')],
                    [sg.T('Data lançamento novos episodios:'),
                     sg.T('D'), sg.Combo(listDays, default_value=listDays[0], k='-KDIA-', disabled=True),
                     sg.T('M'), sg.Combo(listMes, default_value=listMes[0], k='-KMES-', disabled=True),
                     sg.T('A'), sg.Combo(listAnos, default_value=listAnos[0], k='-KANO-', disabled=True)],
                [sg.T('Nota'), sg.Combo(listNotas, default_value=listNotas[0], k='-KNOTA-'),],
                   [sg.Button('Adicionar'), sg.Button('Voltar')]]
    return sg.Window('Series', layout=layout_2, finalize=True)

def make_window3():
    sg.theme('Dark')
    layout_3 = [[sg.T('Editar Serie')],
                    [[sg.T('Serie ID:'), sg.Input(serieID, disabled=True, disabled_readonly_background_color='gray', k='-IDSAVE-')]],
                    [sg.T('Titulo:'), sg.Input(serieName, disabled=True, disabled_readonly_background_color='gray', k='-TITEDIT-'), sg.Button('Editar')],
                    [sg.T('Informe o Status'), sg.Combo(listStatus, default_value=serieStatus, k='-STATUSEDIT-')],
                    [sg.T('Data proximo lançamento:') ,sg.Input(serieData, k='-DATAEDIT-')],
                    [sg.T('Nota'), sg.Combo(listNotas, default_value=serieNota, k='-NOTAEDIT-')],
                   [sg.Button('Salvar'), sg.Button('Voltar')]]
    return sg.Window('Series', layout=layout_3, finalize=True)

janela1 ,janela2, janela3 = make_window1(), None, None



while True:
    window, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED or event == 'Sair':
        cursor.close()
        conexao.close()
        break
    if window == janela1 and event == 'Atualizar':
        puxarDados = """
                SELECT *
                FROM filmesseries
                ORDER BY nome_filme_serie ASC;
                """
        results = read_query(conexao, puxarDados)
        listaSeries = []
        for i in results:
            listaSeries.append(i[1])
        window['-LISTSERIES-'].update(listaSeries)

    if window == janela1 and event == 'Adicionar':
        janela1.hide()
        janela2 = make_window2()

    if window == janela1 and event == 'Deletar':
        title = values['-LISTSERIES-']
        nomeSeriex = title[0]
        comando = f'DELETE FROM filmesseries WHERE nome_filme_serie = "{nomeSeriex}";'
        cursor.execute(comando)
        conexao.commit()

        puxarDados = """
        SELECT *
        FROM filmesseries;
        """
        results = read_query(conexao, puxarDados)
        listaSeries = []
        for i in results:
            listaSeries.append(i[1])

        sg.popup('Dados deletados com sucesso!')
        window['-LISTSERIES-'].update(listaSeries)
    if window == janela2 and event == 'Selecionar':
        if values['-KSTATUS-'] == 'Em andamento':
            window['-KDIA-'].update(disabled=False)
            window['-KMES-'].update(disabled=False)
            window['-KANO-'].update(disabled=False)
        else:
            window['-KDIA-'].update(disabled=True)
            window['-KMES-'].update(disabled=True)
            window['-KANO-'].update(disabled=True)

    if window == janela2 and event == 'Voltar':
        janela2.hide()
        janela1 = make_window1()

    if window == janela2 and event == 'Adicionar':
        titulo = values['-TITULO-']
        status = values['-KSTATUS-']
        dia = values['-KDIA-']
        mes = values['-KMES-']
        ano = values['-KANO-']
        data = f'{dia}/{mes}/{ano}'
        newData = datetime.datetime.strptime(data, '%d/%m/%Y').date()
        newNota = values['-KNOTA-']

        comando = 'INSERT INTO filmesseries (nome_filme_serie, StatusFilmeSerie, dataFilmeSerie, FilmesSeriesNota) VALUES (%s, %s, %s, %s);'
        cursor.execute(comando, (titulo, status, newData, newNota,))
        conexao.commit()

        puxarDados = """
                SELECT *
                FROM filmesseries;
                """
        results = read_query(conexao, puxarDados)
        print(results)
        listaSeries = []
        for i in results:
            listaSeries.append(i[1])

        sg.popup('Dados inseridos com sucesso!')
        janela1.un_hide()
        janela2.hide()
        update_series_list(janela1, conexao)

    if window == janela1 and event == 'Editar':
        title = values['-LISTSERIES-']
        nomeSeriex = title[0]
        puxarDados = f"""
                SELECT *
                FROM filmesseries WHERE nome_filme_serie = "{nomeSeriex}";
                """
        results = read_query(conexao, puxarDados)
        serieID = results[0][0]
        serieName = results[0][1]
        serieData = results[0][2]
        serieNota = results[0][3]
        serieStatus = results[0][4]
        print(serieData)
        dataNewSTR = str(serieData)
        print(type(dataNewSTR))

        #
        janela1.hide()
        janela3 = make_window3()
    if window == janela3 and event == 'Voltar':
        janela3.hide()
        janela1.un_hide()
    if window == janela3 and event == 'Editar':
        window['-TITEDIT-'].update(disabled=False)
    if window == janela3 and event == 'Salvar':
        idNew = values['-IDSAVE-']
        nameNew = values['-TITEDIT-']
        statusNew = values['-STATUSEDIT-']
        dataNew = values['-DATAEDIT-']
        newNota = values['-NOTAEDIT-']
        print(nameNew)
        print(statusNew)
        print(dataNew)
        comandoEditar0 = f'UPDATE filmesseries SET nome_filme_serie= "{nameNew}" WHERE idFilmesSeries = "{idNew}";'
        comandoEditar1 = f'UPDATE filmesseries SET StatusFilmeSerie= "{statusNew}" WHERE idFilmesSeries = "{idNew}";'
        comandoEditar2 = f'UPDATE filmesseries SET dataFilmeSerie= "{dataNew}" WHERE idFilmesSeries = "{idNew}";'
        comandoEditar3 = f'UPDATE filmesseries SET FilmesSeriesNota= "{newNota}" WHERE idFilmesSeries = "{idNew}";'
        cursor.execute(comandoEditar0)
        cursor.execute(comandoEditar1)
        cursor.execute(comandoEditar2)
        cursor.execute(comandoEditar3)
        conexao.commit()
        sg.popup('Dados atualizados com sucesso!')
        janela3.hide()
        janela1.un_hide()
        update_series_list(janela1, conexao)

cursor.close()
conexao.close()