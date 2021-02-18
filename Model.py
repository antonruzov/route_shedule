import numpy as np
import pandas as pd
import Structures


class Allocation:
    def __init__(self,
                 subblock_index_dct, subblock_terminal_dct, block_subblock_dct,
                 routeblock_index_dct, routeblock_terminal_dct,
                 routeblock_distance_dct, routeblock_volume_dct,
                 routeblock_adjacency_matrix,
                 terminal_count_car_dct,
                 count_day,
                 max_distance=500, max_volume=70, margin=10
                 ):
        self.subblock_index_dct = subblock_index_dct
        self.subblock_terminal_dct = subblock_terminal_dct
        self.block_subblock_dct = block_subblock_dct
        
        self.routeblock_index_dct = routeblock_index_dct
        self.routeblock_terminal_dct = routeblock_terminal_dct
        self.routeblock_distance_dct = routeblock_distance_dct
        self.routeblock_volume_dct = routeblock_volume_dct
        self.routeblock_adjacency_matrix = routeblock_adjacency_matrix
        
        self.terminal_count_car_dct = terminal_count_car_dct
        
        self.count_day = count_day
        
        self.max_distance = max_distance
        self.max_volume = max_volume
        self.margin = margin
        
        self.all_state = self.matrix_all_state()
        
        
    def matrix_all_state(self):
        n, m  = len(self.subblock_index_dct), self.count_day
        all_state = np.arange(0, n * m).reshape(m, n).T
        return all_state
    
    
    def get_correct_subblock(self, terminal):
        """
        Функция получения корректных подблоков на основании терминала.
        """
        correct_subblocks_index = []
        for index, terminal_subblock in self.subblock_terminal_dct.items():
            if terminal == terminal_subblock:
                correct_subblocks_index.append(index)
        return correct_subblocks_index
    

    def get_false_routeblock_subblock(self, state):
        """
        Каждому мал. блоку должен соответствовать корректный по терминалу подблок.
        Parameters
        ----------
        state : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        count_false_routeblock_subblock = 0
        for rb, subblock in enumerate(state):
            terminal_rb = self.routeblock_terminal_dct[rb]
            correct_idx_subblocks = self.get_correct_subblock(terminal_rb)
            if subblock not in self.all_state[correct_idx_subblocks]:
                count_false_routeblock_subblock += 1
        return count_false_routeblock_subblock
            
    
    def get_false_double_routeblock(self, state):
        """
        Функция оценки количества ошибок несоответствия интревалам доставки.
        Смежные мал. блоки не должны быть в одном подблоке 
        и доставляться с интервалом минимум 3 дня.
        """
        count_false_double_routeblock = 0
        for routeblock, subblock in enumerate(state):
            subblock_idx, day_routeblock = np.where(self.all_state==subblock)
            subblock_idx, day_routeblock = subblock_idx[0], day_routeblock[0]
            for routeblock_ad, subblock_ad in enumerate(state):
                if routeblock == routeblock_ad:
                    continue
                if self.routeblock_adjacency_matrix[routeblock][routeblock_ad] == 1:
                    subblock_idx_ad, day_routeblock_ad = np.where(self.all_state==subblock_ad)
                    subblock_idx_ad, day_routeblock_ad = subblock_idx_ad[0], day_routeblock_ad[0]
                    # Подблоки двух смежных мал. блоков не должны совпадать
                    if (subblock_idx == subblock_idx_ad) or \
                       (np.abs(day_routeblock-day_routeblock_ad) < 3):
                           count_false_double_routeblock += 1
        return count_false_double_routeblock
    
    
    def get_false_workload_terminal(self, state):
        """
        Функция оценки возможности филиального транспорта.
        Для каждого терминала, посчитаем нагрузку на каждый день.
        """
        count_false_workload_terminal = 0
        for terminal, count_car in self.terminal_count_car_dct.items():
            terminal_workload = dict.fromkeys([i for i in range(self.count_day)], [])
            for routeblock, subblock in enumerate(state):
                if terminal == self.routeblock_terminal_dct[routeblock]:
                    subblock_idx, day_routeblock = np.where(self.all_state==subblock)
                    subblock_idx, day_routeblock = subblock_idx[0], day_routeblock[0]
                    workload = terminal_workload[day_routeblock]
                    workload.append(self.routeblock_distance_dct[routeblock])
                    terminal_workload[day_routeblock] = workload
                balance = 0
                for i in range(self.count_day):
                    fact_workload = sum([1 + wrk // self.max_distance for wrk in terminal_workload[i]])
                    new_workload = balance + fact_workload
                    if new_workload <= count_car:
                        balance = 0
                    else:
                        balance += new_workload - count_car
                if balance > 0:
                    count_false_workload_terminal += 1
        return count_false_workload_terminal
    
    
    def get_false_double_block_next_day(self, state):
        """
        Блоки с двумя терминалами должны приезжать на следующий день.
        """
        count_false_double_block_next_day = 0
        for block, subblocks in self.block_subblock_dct.items():
            if len(subblocks) == 1:
                continue
            if len(subblocks) > 2 or len(subblocks) == 0:
                print('Error count subblocks in block')
            subblock1 = subblocks[0]
            subblock2 = subblocks[1]
            subblock1_day, subblock2_day = -1, -1
            for routeblock, subblock in enumerate(state):
                subblock_idx, day_routeblock = np.where(self.all_state==subblock)
                subblock_idx, day_routeblock = subblock_idx[0], day_routeblock[0]
                if subblock1 == subblock_idx:
                    subblock1_day = day_routeblock
                if subblock2 == subblock_idx:
                    subblock2_day = day_routeblock
            if (subblock1_day < 0) or (subblock2_day < 0):
                count_false_double_block_next_day += 1   
            if np.abs(subblock1_day-subblock2_day) != 1:
                count_false_double_block_next_day += 1
        return count_false_double_block_next_day
    
    
    def get_false_fulness_block(self, state):
        """
        Оценка наполненности блоков.
        """
        count_false_fulness_block = 0
        subblock_routeblock_volume_dct = dict.fromkeys(self.subblock_index_dct.keys(), [])
        for routeblock, subblock in enumerate(state):
            subblock_idx, day_routeblock = np.where(self.all_state==subblock)
            subblock_idx, day_routeblock = subblock_idx[0], day_routeblock[0]
            routeblocks_volume = subblock_routeblock_volume_dct[subblock_idx]
            routeblocks_volume.append(self.routeblock_volume_dct[routeblock])
            subblock_routeblock_volume_dct[subblock_idx] = routeblocks_volume
        for subblocks in self.block_subblock_dct.values():
            volume_block = 0
            for subblock in subblocks:
                volume_block += sum(subblock_routeblock_volume_dct[subblock])
            if (volume_block < self.max_volume - self.margin) or \
               (volume_block > self.max_volume + self.margin):
                   count_false_fulness_block += 1
        return count_false_fulness_block


    def get_fitness_glob(self, state):
        base_fitness = -9999
        fitness = self.get_false_routeblock_subblock(state) * base_fitness + \
                  self.get_false_double_routeblock(state) * base_fitness + \
                  self.get_false_workload_terminal(state) * base_fitness + \
                  self.get_false_double_block_next_day(state) * base_fitness + \
                  self.get_false_fulness_block(state) 
        return fitness
    
        
    def finale_check(self, final_state):
        """
        Функция финально проверки.
        """
        # В решении не должно быть состояний больше, чем подблоков.
        if len(set(final_state)) != len(self.subblock_index_dct):
            print('Ошибка решения, возможные состояния не соответсвуют количеству подблоков ')
        else:
            print('Correct')
            
    
    def form_shedule(self, final_state):
        routeblock_day = {}
        routeblock_subblock = {}
        block_subblock = {}
        for block, values in self.block_subblock_dct.items():
            for value in values:
                block_subblock[self.subblock_index_dct[value]] = block
        for routeblock, subblock in enumerate(final_state):
            subblock_idx, day_routeblock = np.where(self.all_state==subblock)
            subblock_idx, day_routeblock = subblock_idx[0], day_routeblock[0]
            
            routeblock_day[self.routeblock_index_dct[routeblock]] = day_routeblock
            routeblock_subblock[self.routeblock_index_dct[routeblock]] = self.subblock_index_dct[subblock_idx]
            
        return routeblock_day, routeblock_subblock, block_subblock
            
            
if __name__ == "__main__":
    
    
    df = pd.read_excel(r'data.xlsx', sheet_name='route_block')
    RB = Structures.RouteBlock(df)
    
    #print('Индексы мал. блоков: ', RB.routeblock_index_dct)
    #print('Связь мал. блоков и терминала: ', RB.routeblock_terminal_dct)
    #print('Расстояние мал. блоков: ', RB.routeblock_distance_dct)
    #print('Объемы мал. блоков: ', RB.routeblock_volume_dct)
    #print('Смежность блоков:', RB.routeblock_adjacency_matrix)
    
    data_block = pd.read_excel(r'data.xlsx', sheet_name='subblock')
    SUBBLOCK = Structures.Block_SubBlock(data_block)
    #print('Индексы подблоков: ', SUBBLOCK.subblock_index_dct)
    #print('Связь блоков и подблоков: ', SUBBLOCK.block_subblock_dct)
    #print('Связь подблоков и терминалов: ', SUBBLOCK.subblock_terminal_dct)
    
    data_car_terminal = pd.read_excel(r'data.xlsx', sheet_name='small_cars_terminal')
    Terminal = Structures.Terminal(data_car_terminal)
    #print('Возможности филиального транспорта: ', Terminal.terminal_count_car_dct)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
                        
            
            
            
            

