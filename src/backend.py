import gspread
import pandas as pd
import re
import numpy as np
def number(value):
    if '%' in value:
        return float(''.join(re.findall(r'\d+', value)))/(10**len(re.findall(r'\d+', value)[-1]))/((len(re.findall(r'\d+', value)) > 1)*(99)+1)
    elif ',' in value:
        return float(''.join(re.findall(r'\d+', value)))/(10**len(re.findall(r'\d+', value)[-1]))
    else:
        return int(''.join(re.findall(r'\d+', value)))
def date(value):
    import locale
    import datetime
    locale.setlocale(locale.LC_ALL, 'pt_br.UTF-8')
    return datetime.datetime.strptime(''.join(re.findall(r'\w+', value)), '%b%y')
def delta_t(start, end):
    from datetime import datetime
    res_months = (end.year - start.year) * 12 + (end.month - start.month)
    return res_months
def data_processing(data, type_list, pos = 0):
    cols = data.columns
    if pos == 0:
        for j, col in enumerate(cols):
            data[col] = [number(data[col][i]) if (type_list[j] == 'number') else date(data[col][i]) if (type_list[j] == 'date') else data[col][i] for i in range(len(data))]
    else:
        data[cols[pos]] = [number(data[cols[pos]][i]) if (type_list[i] == 'number') else date(data[cols[pos]][i]) if (type_list[i] == 'date') else data[cols[pos]][i] for i in range(len(data[cols[pos]]))]
    return data

class OpenFile:
    def __init__(
        self,
        sheet_name = "Estudo Financeiro - Dados Iniciais",
        access = "service_account.json"
        ):

        self.sheet_name = sheet_name
        self.access = access

    # def initialization(self):
        service_account = gspread.service_account(filename=self.access)
        self.spreadsheet = service_account.open(self.sheet_name)

    def get_data(
        self,
        data_range = ['C1:I300', 'O1:R6', 'O9:P22', 'L1:M', 'O25:R28', 'O31:R34'], 
        data_type = [
            ['string', 'number', 'number', 'number', 'date', 'string', 'number'], 
            ['string'] + ['number'] * 3 , 
            ['number' if ((i != 7) and (i != 11)) else 'date' for i in range(13)], 
            ['number', 'date'], 
            ['number', 'number', 'date', 'number'], 
            ['number', 'number', 'date', 'number'],
            ], 
        data_axis = [0 if (i != 2) else 1 for i in range(6)],
        worksheet_name = "Paiva QS 2"):
        self.worksheet_name = worksheet_name
        self.worksheet = self.spreadsheet.worksheet(self.worksheet_name)
        self.data = [
            data_processing(
                pd.DataFrame(
                    data=self.worksheet.get(data_range[i])[1:], 
                    columns=self.worksheet.get(data_range[i])[0]),
                data_type[i],
                data_axis[i]) 
            for i in range(len(data_axis))]

class SalesTable:
    def __init__(self, data) -> None:
        self.df                    = data[0]
        self.payment_options       = data[1]
        self.business_conditions   = data[2]
        self.construction_schedule = data[3]
        self.investiment_input     = data[4]
        self.investiment_output    = data[5]

        # Dicionário com Dados do Empreendimento
        dt, self.names = {}, []
        p = self.payment_options.to_dict()
        perc, parc, freq = ['%', 'Parcelas', 'Frequencia']
        for key, val in p['Tipo'].items():
            self.names.append(val)
            dt[val] = {perc: p['Porcentagem'][key], parc: p['Número de Parcelas'][key], freq: p['Frequência'][key]}

        b = self.business_conditions.to_dict()
        for k, v in b['Tipo'].items():
            dt[v] =  b['Valor'][k]
        del(p, b)

        # Criando novas colunas e Datas e outras variáveis
        self.t0 = min(self.df['Data Venda'].min(), dt['Data Inv. Inic.'], dt['Data Início Obra'])
        self.inicio_obra = delta_t(self.t0, dt['Data Início Obra'])
        self.fim_obra = self.inicio_obra + dt['Obra'][parc]
        self.df['Diff Início Obra'] = round((self.df['Data Venda'] - dt['Data Início Obra'])/np.timedelta64(1,'M'),0)
        self.df['Diff Início Obra'] = self.df['Diff Início Obra'].astype('int64')
        self.df['Diff t0'] = round((self.df['Data Venda'] - self.t0)/np.timedelta64(1,'M'),0)
        self.df['Diff t0'] = self.df['Diff t0'].astype('int64')
        m, n = 'Mês ', 'N. '
        name_ent, name_obr, name_chv, name_int, name_pos = self.names
        col = self.df.columns
        # - Valor a Vista
        incc = dt['INCC atual']/dt['INCC base']
        name_vav = 'Valor a Vista'
        self.df[name_vav] = self.df[col[1]] * self.df[col[2]] * incc

        # - Entrada
        self.df[name_ent] = [self.df[name_vav][i] * dt[name_ent][perc]  if self.df['Observação'][i] == 'Venda' else 0 for i in range(len(self.df))]
        self.df[n + name_ent] = [dt[name_ent][parc] if self.df['Observação'][i] == 'Venda' else 0 for i in range(len(self.df))]

        conditions = [
            (self.df[name_ent] == 0),
            (self.df[name_ent] != 0),
        ]

        values = [
            "-", 
            self.df['Diff t0'], 
        ]

        self.df[m + name_ent] = np.select(conditions, values)
        self.df[freq + ' ' + name_ent] = dt[name_ent][freq]

        # - Obra
        conditions = [
            (self.df['Observação'] != 'Venda'),
            (self.df['Diff Início Obra'] < 0),
            (self.df['Diff Início Obra'] <= dt['Tempo Limite']),
            (self.df['Diff Início Obra'] > dt['Tempo Limite'])
        ]

        values1 = [
            0, 
            dt[name_obr][parc], 
            dt[name_obr][parc] - self.df['Diff Início Obra'], 
            0
        ]

        self.df[n + name_obr]   = np.select(conditions, values1)

        values2 = [
            0, 
            self.df[name_vav] * dt[name_obr][perc] / self.df[n + name_obr], 
            self.df[name_vav] * dt[name_obr][perc] / self.df[n + name_obr], 
            0
        ]
        values3 = [
            "-",
            self.inicio_obra,
            self.df['Diff t0'],
            "-"
        ]

        self.df[name_obr]     = np.select(conditions, values2)
        self.df[m + name_obr] = np.select(conditions, values3)
        self.df[freq + ' ' + name_obr] = dt[name_obr][freq]

        # - Chaves
        conditions = [
            (self.df['Observação'] != 'Venda') | (dt[name_chv][perc] == 0) | (dt[name_chv][parc] == 0),
            (self.df['Diff Início Obra'] <= dt[name_obr][parc]),
            (self.df['Diff Início Obra'] > dt[name_obr][parc])
        ]

        values1 = [
            0,
            self.df[name_vav] * dt[name_chv][perc] / dt[name_chv][parc],
            0,
        ]
        values2 = [
            0,
            dt[name_chv][parc],
            0
        ]
        values3 = [
            "-",
            self.fim_obra,
            "-",
        ]

        self.df[name_chv] = np.select(conditions, values1)
        self.df[n + name_chv] = np.select(conditions, values2)
        self.df[m + name_chv] = np.select(conditions, values3)
        self.df[freq + ' ' + name_chv] = dt[name_chv][freq]

        # - Pós-Obra
        taxas = dt['Capitalização'] + dt['IPCA/IGPM']  # Sem capitalização = 0
        aux = self.df[name_vav] - self.df[name_ent]*self.df[n + name_ent] - self.df[name_obr]*self.df[n + name_obr] - self.df[name_chv]*self.df[n + name_chv] - self.df[name_vav]*dt[name_int][perc]

        conditions = [
            (self.df['Observação'] != 'Venda') | (dt[name_pos][perc] == 0) | (dt[name_pos][parc] == 0),
            (self.df['Diff Início Obra'] <= dt[name_obr][parc]),
            (self.df['Diff Início Obra'] > dt[name_obr][parc])
        ]
        values1 = [
            0,
            dt[name_pos][parc],
            dt[name_pos][parc] - (self.df['Diff Início Obra'] - dt[name_obr][parc]),
        ]

        self.df[n + name_pos] = np.select(conditions, values1)

        values2 = [
            0,
            (taxas)/(1-(1+(taxas))**(-dt[name_pos][parc]))*(aux),
            (taxas)/(1-(1+(taxas))**(-self.df[n + name_pos]))*(aux)
        ]

        values3 = [
            "-",
            self.fim_obra,
            self.df['Diff t0']
        ]

        self.df[name_pos] = np.select(conditions, values2)
        self.df[m + name_pos] = np.select(conditions, values3)
        self.df[freq + ' ' + name_pos] = dt[name_pos][freq]

        # - Pós-Obra Descapitalizado
        
        conditions = [
            (self.df['Observação'] != 'Venda') | (dt[name_pos][perc] == 0) | (dt[name_pos][parc] == 0),
            (self.df['Diff Início Obra'] <= dt[name_obr][parc]),
            (self.df['Diff Início Obra'] > dt[name_obr][parc])
        ]
        values1 = [
            0,
            dt[name_pos][parc],
            dt[name_pos][parc] - (self.df['Diff Início Obra'] - dt[name_obr][parc]),
        ]

        self.df[n + name_pos + ' 2'] = np.select(conditions, values1)

        values2 = [
            0,
            (self.df[name_vav] - self.df[name_ent] * self.df[n + name_ent] - self.df[name_obr] * self.df[n + name_obr] - self.df[name_chv] * self.df[n + name_chv] - self.df[name_vav] * dt[name_int]['%']) / self.df[n + name_pos + ' 2'], 
            (self.df[name_vav] - self.df[name_ent] * self.df[n + name_ent] - self.df[name_obr] * self.df[n + name_obr] - self.df[name_chv] * self.df[n + name_chv] - self.df[name_vav] * dt[name_int]['%']) / self.df[n + name_pos + ' 2'], 
        ]
        
        values3 = [
            "-",
            self.fim_obra,
            self.df['Diff t0']
        ]

        self.df[name_pos + ' 2'] = np.select(conditions, values2)
        self.df[m + name_pos + ' 2'] = np.select(conditions, values3)
        self.df[freq + ' ' + name_pos + ' 2'] = dt[name_pos][freq]

        # - Intercaladas
        conditions = [
            (self.df['Observação'] != 'Venda') | (dt[name_int][perc] == 0) | (dt[name_int][parc] == 0),
            (self.df['Diff Início Obra'] <= dt[name_obr][parc]),
            (self.df['Diff Início Obra'] > dt[name_obr][parc])
        ]

        values1 = [
            0,
            round(self.df[n + name_pos]/dt[name_int][freq]-1),
            round(self.df[n + name_pos]/dt[name_int][freq]-1),
        ]

        self.df[n + name_int] = np.select(conditions, values1)

        values2 = [
            0,
            ((1+(taxas))**(dt[name_int][freq])-1)/(1-(1+((1+(taxas))**(dt[name_int][freq])-1))**(-self.df[n + name_int]))*self.df[name_vav]*dt[name_int][perc],
            ((1+(taxas))**(dt[name_int][freq])-1)/(1-(1+((1+(taxas))**(dt[name_int][freq])-1))**(-self.df[n + name_int]))*self.df[name_vav]*dt[name_int][perc]
        ]

        values3 = [
            0,
            dt[name_int][freq],
            dt[name_int][freq]
        ]

        values4 = [
            "-",
            self.fim_obra,
            self.df['Diff t0']
        ]

        self.df[name_int] = np.select(conditions, values2)
        self.df[freq + ' ' + name_int] = np.select(conditions, values3)
        self.df[m + name_int] = np.select(conditions, values4)

        # - Intercaladas Descapitalizadas
        conditions = [
            (self.df['Observação'] != 'Venda') | (dt[name_int][perc] == 0) | (dt[name_int][parc] == 0),
            (self.df['Diff Início Obra'] <= dt[name_obr][parc]),
            (self.df['Diff Início Obra'] > dt[name_obr][parc])
        ]

        values1 = [
            0,
            round(self.df[n + name_pos]/dt[name_int][freq]-1),
            round(self.df[n + name_pos]/dt[name_int][freq]-1),
        ]

        self.df[n + name_int + ' 2'] = np.select(conditions, values1)

        values2 = [
            0,
            self.df[name_vav] * dt[name_int][perc] / self.df[n + name_int], 
            self.df[name_vav] * dt[name_int][perc] / self.df[n + name_int], 
        ]

        values3 = [
            0,
            dt[name_int][freq],
            dt[name_int][freq]
        ]

        values4 = [
            "-",
            self.fim_obra,
            self.df['Diff t0']
        ]

        self.df[name_int + ' 2'] = np.select(conditions, values2)
        self.df[freq + ' ' + name_int + ' 2'] = np.select(conditions, values3)
        self.df[m + name_int + ' 2'] = np.select(conditions, values4)

        # Período
        conditions = [
            (self.df['Diff Início Obra'] < 0),
            (self.df['Diff Início Obra'] <= dt[name_obr][parc]),
            (self.df['Diff Início Obra'] > dt[name_obr][parc])
        ]

        values = [
            "Antes da Obra",
            "Durante a Obra",
            "Pós Obra",
        ]

        self.df['Periodo'] = np.select(conditions, values)

        self.table = self.df
        self.dt = dt

class CashFlow:
    def __init__(self, sales):

        m, n, freq = 'Mês ', 'N. ', 'Frequencia'
        _, _, _, name_int, name_pos = sales.names

        # Novo Dataframe
        df2 = pd.DataFrame()

        # Obra / Saída
        col3 = sales.construction_schedule.columns
        sales.construction_schedule['Diff t0'] = sales.construction_schedule[col3[1]].apply(lambda x: delta_t(sales.t0, x))
        sales.construction_schedule['R$'] = sales.dt['Valor Obra'] * sales.construction_schedule[col3[0]] * sales.dt['INCC atual']/sales.dt['INCC base']

        cols = ['Mês', 'Tipo', 'Tipo Parcela', 'Origem', 'Valor', 'Impostos', ]

        df2[cols[0]] = sales.construction_schedule['Diff t0']
        df2[cols[1]] = 'Saída'
        df2[cols[2]] = 'Obra'
        df2[cols[3]] = 'Obra'
        df2[cols[4]] = sales.construction_schedule['R$']
        df2[cols[5]] = 0.0

        # Investimento Inicial / Saída
        inv_ini = [
            delta_t(sales.t0, sales.dt['Data Inv. Inic.']), 
            'Saída', 
            'Inv. Inicial', 
            'Inv. Inicial',
            sales.dt['Inv. Inicial'],
            0.0
        ]

        df2.loc[len(df2)] = inv_ini

        # Corretagem / Saída
        corretagem = pd.DataFrame()
        corretagem[cols[0]] = sales.df['Diff t0']
        corretagem[cols[1]] = 'Saída'
        corretagem[cols[2]] = 'Corretagem'
        corretagem[cols[3]] = 'Obra'
        corretagem[cols[4]] = (sales.df['Observação'] == 'Venda') * (sales.df['Corretagem'] * sales.df['Valor a Vista'])
        corretagem[cols[5]] = 0.0

        df2 = pd.concat([df2, corretagem], ignore_index=True)
        df3 = df2[:]

        # Entradas
        def flowSet(df, tipo, num, t_0 = 0, tax = sales.dt['Impostos']):
            df_aux = pd.DataFrame()

            frequency              = df.loc[num, freq + ' ' + tipo]
            df_aux['Mês']          = [int(df.loc[num, m + tipo]) + i*frequency + t_0 for i in range(int(df.loc[num, n + tipo]))]
            df_aux['Tipo']         = 'Entrada'
            df_aux['Tipo Parcela'] = tipo
            df_aux['Origem']       = df.iloc[num, 0]
            df_aux['Valor']        = df.loc[num, tipo]
            df_aux['Impostos']     = df.loc[num, tipo] * tax
            return df_aux

        for num in range(len(sales.df)):
            for name in sales.names:
                if name == name_int:
                    df2 = pd.concat([df2, flowSet(sales.df, name, num, t_0 = 12)], ignore_index=True)
                else:
                    df2 = pd.concat([df2, flowSet(sales.df, name, num)], ignore_index=True) 
        
        self.in_out = [[], []]
        self.in_out[0] = df2[:]

        for num in range(len(sales.df)):
            for name in sales.names:
                if name == name_int:
                    df3 = pd.concat([df3, flowSet(sales.df, name + ' 2', num, t_0 = 12)], ignore_index=True)
                elif name == name_pos:
                    df3 = pd.concat([df3, flowSet(sales.df, name + ' 2', num)], ignore_index=True) 
                else:
                    df3 = pd.concat([df3, flowSet(sales.df, name, num)], ignore_index=True) 

        self.in_out = [[], []]
        self.in_out[0] = df2[:]
        self.in_out[1] = df3[:]
        self.cols = cols
        self.sales = sales
        self.investiment_input = sales.investiment_input
        self.investiment_output = sales.investiment_output
        self.input_value = 0
        self.output_value = 0

        ####################### FLUXO #######################
    def Run(self, interest = True):
        i = 1 - interest * 1
        cols = self.cols
        aporte = self.investiment_input
        remuneracao = self.investiment_output

        df = [pd.DataFrame(), pd.DataFrame()]
        df[i][cols[0]] = [i for i in range(int(self.in_out[i][cols[0]].max()) + 1)]
        df[i]['Data'] = df[i]['Mês'].apply(lambda x: pd.to_datetime(self.sales.t0)+pd.DateOffset(months=x))
        df[i]['Impostos'] = self.in_out[i].groupby(cols[0])['Impostos'].sum().fillna(0)
        df[i]['Entradas'] = self.in_out[i][self.in_out[i]['Tipo'] == 'Entrada'].groupby(cols[0])['Valor'].sum().fillna(0)
        df[i]['Saídas']   = self.in_out[i][(self.in_out[i]['Tipo'] == 'Saída') & (self.in_out[i]['Tipo Parcela'] != 'Corretagem')].groupby(cols[0])['Valor'].sum()
        df[i]['Comissões'] = self.in_out[i][(self.in_out[i]['Tipo'] == 'Saída') & (self.in_out[i]['Tipo Parcela'] == 'Corretagem')].groupby(cols[0])['Valor'].sum()
        df[i] = df[i].fillna(0)
        df[i]['Fluxo'] = df[i]['Entradas'] - df[i]['Saídas'] - df[i]['Impostos'] - df[i]['Comissões']
        df[i]['Fluxo Acumulado'] = df[i]['Fluxo'].cumsum()
        df[i]['Aportes Necessários'] = df[i]['Fluxo'].loc[df[i]['Fluxo'] < 0]

        self.input_demand = df[i]['Aportes Necessários'].sum()
        if self.input_value == 0:
            from math import ceil
            factor = 6
            self.input_value = ceil((df[i]['Aportes Necessários'].sum()**2)**(1/2)/10**factor)*10**factor

        if self.output_value == 0:
            from math import ceil
            self.output_value = df[i]['Fluxo Acumulado'].iloc[-1] + self.input_value

        # Preparando aportes e remunerações
        aporte[cols[0]] = [delta_t(self.sales.t0, aporte['Data Inicial'][i]) for i in range(len(aporte))]
        aporte['Mês'] = [delta_t(self.sales.t0, aporte['Data Inicial'][i]) for i in range(len(aporte))]
        aporte['Valor'] = aporte['Taxas'] * self.input_value / aporte['Parcelas']
        aporte_flow = [[[aporte['Mês'][j] + i*aporte['Periodicidade'][j], aporte['Valor'][j]] for i in range(aporte['Parcelas'][j])] for j in range(len(aporte))]
        title = ['Mês', 'Aporte']
        df_aporte = pd.concat([pd.DataFrame(aporte_flow[i], columns = title) for i in range(len(aporte_flow))], ignore_index=True).groupby('Mês').sum()

        df[i] = df[i].merge(df_aporte.groupby('Mês').sum(), on = 'Mês', how='outer')

        remuneracao[cols[0]] = [delta_t(self.sales.t0, remuneracao['Data Inicial'][i]) for i in range(len(remuneracao))]
        remuneracao['Mês'] = [delta_t(self.sales.t0, remuneracao['Data Inicial'][i]) for i in range(len(remuneracao))]
        remuneracao['Valor'] = remuneracao['Taxas'] * self.output_value / remuneracao['Parcelas']
        remuneracao_flow = [[[remuneracao['Mês'][j] + i*remuneracao['Periodicidade'][j], remuneracao['Valor'][j]] for i in range(remuneracao['Parcelas'][j])] for j in range(len(remuneracao))]
        title = ['Mês', 'Remuneração']
        df_remuneracao = pd.concat([pd.DataFrame(remuneracao_flow[i], columns = title) for i in range(len(remuneracao_flow))], ignore_index=True).groupby('Mês').sum()

        df[i] = df[i].merge(df_remuneracao.groupby('Mês').sum(), on = 'Mês', how='outer').fillna(0)

        df[i]['Fluxo com Investidor'] = df[i]['Fluxo'] + df[i]['Aporte'] - df[i]['Remuneração']

        self.table = df[i]

class Save():
    def __init__(self) -> None:
        pass

class Investiment():
    def __init__(self):
        self.file = OpenFile() # Caso seja usado google sheets.
        self.file.get_data() # Caso seja usado google sheets.
        self.sales = SalesTable(self.file.data)
        self.cash_flow = CashFlow(self.sales) # input, output
        self.cash_flow.Run()
        self.cash_flow.table
        Save()
