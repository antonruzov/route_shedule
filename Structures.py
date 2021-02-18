import numpy as np
import pandas as pd


class Block_SubBlock:
    def __init__(self, df):
        self.df = df # Исходные данные. Таблица с полями: SubBlock, Block, Terminal
        
        self.subblock_index_dct = self.subblock_index()
        self.subblock_terminal_dct = self.subblock_terminal()
        self.block_subblock_dct = self.block_subblock()
        
    def subblock_index(self):
        """
        Функция, которая формирует словарь:
        key - index
        value - name_subblock
        """
        subblock_index_dct = {i : name for i, name in enumerate(set(self.df['SubBlock'].values))}
        return subblock_index_dct
    
    
    def subblock_terminal(self):
        """
        Функция, которая формирует словарь:
        key - index_subblock
        value - terminal_subblock
        """
        subblock_terminal_dct = {}
        for index, name_subblock in self.subblock_index_dct.items():
            terminal = self.df[self.df['SubBlock'] == name_subblock]['Terminal'].values
            if len(terminal) > 1:
                print('Double terminal at the subblock')
                break
            else:
                subblock_terminal_dct[index] = terminal[0]
        return subblock_terminal_dct
                
    
    def block_subblock(self):
        """
        Функция, которая формирует словарь:
        key - name_block
        value = list of index subblock
        """
        block_subblock_dct = {}
        for block in set(self.df['Block'].values):
            subblocks = self.df[self.df['Block'] == block]['SubBlock'].values
            subblocks_index = []
            for subblock in subblocks:
                for index, name_subblock in self.subblock_index_dct.items():
                    if subblock == name_subblock:
                        subblocks_index.append(index)
            block_subblock_dct[block] = subblocks_index
        return block_subblock_dct


class RouteBlock:
    def __init__(self, df):
        self.df = df # Исходные данные. Таблица с полями: Terminal, Route_block, Pharmacy, Distance, Volume
        
        self.routeblock_index_dct = self.routeblock_index()
        self.routeblock_terminal_dct = self.routeblock_terminal()
        self.routeblock_distance_dct = self.routeblock_distance()
        self.routeblock_volume_dct = self.routeblock_volume()
        self.routeblock_adjacency_matrix = self.routeblock_adjacency()
        
        
    def routeblock_index(self):
        """
        Функция, которая формирует словарь:
        key - index_routeblock
        value = name_routeblock
        """
        routeblock_index_dct = {i : name for i, name in enumerate(set(self.df['Route_block'].values))}
        return routeblock_index_dct
        
    
    def routeblock_adjacency(self):
        """

        Матрица смежности блоков.
        Размерность nxn, где n - количество мал. блоков
        Если блоки смежные, то 1, иначе 0.
        Матрица симметричная.
        -------
        None.

        """
        n = len(self.routeblock_index_dct)
        routeblock_adjacency_matrix = np.zeros(shape=(n, n))
        for index, routeblock in self.routeblock_index_dct.items():
            pharmacys = set(self.df[self.df['Route_block'] == routeblock]['Pharmacy'].values)
            for index1, routeblock1 in self.routeblock_index_dct.items():
                pharmacys_adj = set(self.df[self.df['Route_block'] == routeblock1]['Pharmacy'].values)
                if len(pharmacys.intersection(pharmacys_adj)) > 0:
                    routeblock_adjacency_matrix[index][index1] = 1
        return routeblock_adjacency_matrix
    
    
    def routeblock_terminal(self):
        routeblock_terminal_dct = {}
        for index, routeblock in self.routeblock_index_dct.items():
            terminals = set(self.df[self.df['Route_block'] == routeblock]['Terminal'].values)
            if len(terminals) > 1:
                print('Один малотоннажный блок соответсвует двум терминалам')
                break
            routeblock_terminal_dct[index] = list(terminals)[0]
        return routeblock_terminal_dct


    def routeblock_distance(self):
        routeblock_distace_dct = {index : self.df[self.df['Route_block'] == routeblock]['Distance'].sum() \
                                 for index, routeblock in self.routeblock_index_dct.items()}
        return routeblock_distace_dct


    def routeblock_volume(self):
        routeblock_volume_dct = {index : self.df[self.df['Route_block'] == routeblock]['Volume'].sum() \
                                  for index, routeblock in self.routeblock_index_dct.items()}
        return routeblock_volume_dct
            
                    
class Terminal:
    def __init__(self, df):
        self.df = df # Исходные данные. Таблица с полями: Terminal, SmallCar
        
        self.terminal_count_car_dct = self.terminal_count_car()
        
    
    def terminal_count_car(self):
        terminal_count_car_dct = {terminal : len(self.df[self.df['Terminal'] == terminal]['Car'].values) \
                                  for terminal in set(self.df['Terminal'].values)}
        return terminal_count_car_dct
        
    
    
if __name__ == "__main__":
    
    df = pd.read_excel(r'data.xlsx', sheet_name='route_block')
    RB = RouteBlock(df)
    
    print('Индексы мал. блоков: ', RB.routeblock_index_dct)
    print('Связь мал. блоков и терминала: ', RB.routeblock_terminal_dct)
    print('Расстояние мал. блоков: ', RB.routeblock_distance_dct)
    print('Объемы мал. блоков: ', RB.routeblock_volume_dct)
    print('Смежность блоков:', RB.routeblock_adjacency_matrix)
    
    data_block = pd.read_excel(r'data.xlsx', sheet_name='subblock')
    SUBBLOCK = Block_SubBlock(data_block)
    print('Индексы подблоков: ', SUBBLOCK.subblock_index_dct)
    print('Связь блоков и подблоков: ', SUBBLOCK.block_subblock_dct)
    print('Связь подблоков и терминалов: ', SUBBLOCK.subblock_terminal_dct)
    
    data_car_terminal = pd.read_excel(r'data.xlsx', sheet_name='small_cars_terminal')
    Terminal = Terminal(data_car_terminal)
    print('Возможности филиального транспорта: ', Terminal.terminal_count_car_dct)
                
                
                
                
                
                
            
        
        