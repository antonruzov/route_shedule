import pandas as pd
import Structures
import Model
import ga


def write_result(df, name):
    path = 'results/{}.xlsx'.format(name)
    writer = pd.ExcelWriter(path)
    df.to_excel(writer)
    writer.save()
    writer.close()
    
    
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
    
    count_subblock = len(SUBBLOCK.subblock_index_dct)
    count_route_block = len(RB.routeblock_index_dct)
    
    for count_day in range(7, 8):
        print(count_day)
        alloc = Model.Allocation(SUBBLOCK.subblock_index_dct, 
                                 SUBBLOCK.subblock_terminal_dct,
                                 SUBBLOCK.block_subblock_dct,
                                 RB.routeblock_index_dct, 
                                 RB.routeblock_terminal_dct,
                                 RB.routeblock_distance_dct,
                                 RB.routeblock_volume_dct,
                                 RB.routeblock_adjacency_matrix,
                                 Terminal.terminal_count_car_dct,
                                 count_day)
        genetic = ga.GA(count_subblock * count_day, count_route_block)
        best_person, best_fitness = genetic.optimize(alloc.get_fitness_glob, genetic.initial_population)
        
        routeblock_day, routeblock_subblock, block_subblock = alloc.form_shedule(best_person)
        
        df_new = df.copy()
        df_new['day'] = df_new['Route_block'].replace(routeblock_day)
        df_new['subblock'] = df_new['Route_block'].replace(routeblock_subblock)
        df_new['block'] = df_new['subblock'].replace(block_subblock)
        write_result(df_new, 'Количество дней {}'.format(count_day))
        
        alloc.finale_check(best_person)
        
        print()
    
    
    