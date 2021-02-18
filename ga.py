import numpy as np
import matplotlib.pyplot as plt


def get_fitness(population):
    fitness_score = np.power(population.sum(), 2)
    return fitness_score


class GA:
    def __init__(self, count_block, count_route_block, size_population=100, 
                 mutation_rate=0.01, num_epoch=200):
        # Параметры, которыми инициализируется класс
        self.count_block = count_block # Количество доступных крупнотоннажных машин
        self.num_gen = count_route_block # Количество малотоннажных блоков
        self.size_population = int((size_population // 2) * 2) # Размер популяции. Должен быть четным числом
        self.mutation_rate = mutation_rate # Вероятность мутации в генотипе
        self.num_epoch = num_epoch # Количество эпох
        # Прочие параметры
        self.num_parents = int(self.size_population / 2) # Количество родителей соответсвует размеру популяции
        self.num_offsprings = self.size_population # Количество детей соответсвует размеру популяции
        self.initial_population = self.create_initial_population()
    
    
    def create_initial_population(self):
        """
        Функция возвращает начальную популяцию
        """
        return np.random.randint(0, self.count_block, 
                                 size=(self.size_population, self.num_gen))
    
    
    def cal_fitness(self, get_fitness, population):
        """
        Функция оценки приспособленности каждой особи в популяции.
        population : популяция
        get_fitness : ВНЕШНЯЯ ФУНКЦИЯ, которая оценивает приспособленность
        """
        fitness = np.empty(population.shape[0])
        for i in range(fitness.shape[0]):
            fitness[i] = get_fitness(population[i])
        return fitness
    
    
    def selection(self, population, fitness):
        """
        Функция выбора лучших родителей
        """
        fitness = list(fitness)
        parents = np.empty(shape=(self.num_parents, self.num_gen))
        for i in range(self.num_parents):
            max_fitness_idx = np.where(fitness == np.max(fitness))
            parents[i, :] = population[max_fitness_idx[0][0], :]
            fitness[max_fitness_idx[0][0]] = -1000
        parents = parents.astype(int)
        return parents
    
    
    def roulette_selection(self):
        """
        Имитация рулеточного отбора для скрещивания родителей
        """
        probability_choice = np.arange(self.num_parents, 0, -1) * 2/(self.num_parents*(self.num_parents+1))
        parents_idx = np.random.choice(np.arange(0, self.num_parents), 
                                       size=self.num_parents, 
                                       p=probability_choice)
        return parents_idx
    
    
    def crossover(self, parents):
        offsprings = []
        crossover_point = np.random.randint(0, parents.shape[1]) # Точка скрещивания родителей
        """
        Функция скрещивания родителей.
        Родители выбираются на основании рулеточного отбора.
        Пара родителей пораждает пару детей, 
        таким образом сохраняется размерность популяции.
        """
        parents_idx = self.roulette_selection()
        #print(parents)
        
        while len(offsprings) < self.num_offsprings:
            parents_1 = parents_idx[np.random.randint(0, parents.shape[0])]
            parents_2 = parents_idx[np.random.randint(0, parents.shape[0])]
            count_while = 0
            while parents_1 == parents_2:
                parents_2 = parents_idx[np.random.randint(0, parents.shape[0])]
                count_while += 1
                # Может получится так, что в популяции нет разных родителей.
                # Это означает, что, скорее всего достигнут оптимум.
                if count_while == 1000:
                    break
            children_1 = parents[parents_1]
            children_1[crossover_point:] = parents[parents_2, crossover_point:]
            children_2 = parents[parents_2]
            children_2[crossover_point:] = parents[parents_1, crossover_point:]
            offsprings.append(children_1)
            offsprings.append(children_2)
        offsprings = np.array(offsprings)
        offsprings = offsprings.astype(int)
        return offsprings
    
    
    def mutation(self, offsprings):
        """
        Функция мутации случайного гена
        """
        mutants = offsprings
        for i in range(mutants.shape[0]):
            prob = np.random.randint(0, 1)
            if prob > self.mutation_rate:
                continue
            idx_random_value = np.random.randint(0, mutants.shape[1])
            mutants[i, idx_random_value] = np.random.randint(0, self.count_block)
        return mutants
    
    
    def optimize(self, get_fitness, population):
        fitness_history = []
        for i in range(self.num_epoch):
            fitness = self.cal_fitness(get_fitness, population)
            fitness_history.append(fitness)
            parents = self.selection(population, fitness)
            offsprings = self.crossover(parents)
            mutants = self.mutation(offsprings)
            population = mutants
        
        #print('Last generation: \n{}\n'.format(population)) 
        fitness_last_gen = self.cal_fitness(get_fitness, population)      
        print('Fitness of the last generation: \n{}\n'.format(fitness_last_gen))
        max_fitness_idx = np.where(fitness_last_gen == np.max(fitness_last_gen))
        best_fitness = fitness_last_gen[max_fitness_idx[0][0]]
        best_person = population[max_fitness_idx[0][0]]
        print('Best person: \n', best_person)
        return best_person, best_fitness#fitness_history
    
if __name__ == "__main__":
    
    # Тестирование класса на примере решения поиска максимальной последовательности единиц.
    # ONE-MAX ЗАДАЧА.
    
    ga = GA(count_block=2, count_route_block=50, size_population=60, num_epoch=100)
    best_person, fitness_history = ga.optimize(get_fitness, ga.initial_population)
    
    fitness_history_mean = [np.mean(fitness) for fitness in fitness_history]
    fitness_history_max = [np.max(fitness) for fitness in fitness_history]
    plt.hlines(np.power(ga.num_gen, 2), xmin=0, xmax=ga.num_epoch, color='red', label='best score')
    plt.plot(list(range(ga.num_epoch)), fitness_history_mean, label = 'Mean Fitness')
    plt.plot(list(range(ga.num_epoch)), fitness_history_max, label = 'Max Fitness')
    plt.legend(loc='best')
    plt.title('Fitness through the generations')
    plt.xlabel('Generations')
    plt.ylabel('Fitness')
    plt.show()
    

        
        
        