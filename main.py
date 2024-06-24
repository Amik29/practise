from flask import Flask,jsonify,render_template,session,request
from flask_restful import Api
import numpy as np
import random

app = Flask(__name__)
api = Api()

api.init_app(app)
app.secret_key = 'BAD_SECRET_KEY'

@app.route('/')
def responser():
    return render_template('index.html') # Рендер базовой страницы


@app.route('/<string:data_name>/<float:step>/')
@app.route('/<string:data_name>/<int:step>/')
def Data_Post_Uniform(data_name,step):
    if data_name == 'destinations':
        data = destinations
    elif data_name == 'asimuts': #Выбор нужного массива для отправки
        data = asimuts
    dataToSend = Uniform_histogram(step,data) #Построение словаря с подписями интервалов и количествами попадания в них для слуая с step=const.
    return jsonify(dataToSend) #Отправка 

@app.route('/<string:data_name>/list')
def Data_Post_Intervals(data_name):
    if data_name == 'destinations':
        data = destinations
    elif data_name == 'asimuts': #Выбор нужного массива для отправки
        data = asimuts
    list_intervals = session['intervals']
    dataToSend = Interval_histogram(list_intervals,data) # Рассчет значений корзин для заданных интервалов 
    print(dataToSend) #Log_print()
    return jsonify(dataToSend) #Отправка



@app.route('/<string:data_name>/postlist',methods=['POST'])
def Get_Intervals(data_name):
    session['intervals'] = sorted(request.get_json()['array'], key=lambda x: int(x.split('-')[0]))
    print("Intervals_get") #Log_print()
    return jsonify({'message': 'Данные получены' + data_name})
    
@app.route('/RoseDiag/',methods=['POST'])
def Get_RoseDiag():
    print("RoseDiag: data_send") #Log_print()
    return jsonify((RoseDiag(asimuts,destinations,float(request.get_json()['stepAsim']),float(request.get_json()['stepDest'])))) #Отправка 


@app.route('/PercentDiag',methods=['POST'])
def Get_Percent_diag():
    match request.get_json()["data_name"]:
        case "destinations":
            data = destinations
        case "asimuts":
            data = asimuts
    percent = float(request.get_json()["percent"])
    num_bins = int(request.get_json()["num_bins"])
    dataToSend = custom_histogram(data,percent,num_bins)
    return jsonify(dataToSend)



#numba needed
def Uniform_histogram(step:float,data:list) ->dict:
    i = 0
    uniform_bins = {} #создаем словарь
    while i*step <= data[-1]:
        uniform_bins[i] = [f'{i*step}-{(i+1)*step}',0] # задаем стартовые значения для корзин {i:int : interval:str, count:int}
        i+=1
    for el in data:
       uniform_bins[el//step][1]+=1   #Равномерный шаг позволяет сделать не прогонку по всем корзинам, а по кратности шагу то есть 0-250 при step=250, имеет i = 0, O(N)
    data_new = [value for value in uniform_bins.values()]
    data_labels = [data_new[i][0] for i in range(len(data_new))]
    data_bins = [data_new[i][1] for i in range(len(data_new))] #Преобразуем данные для отправки
    return {"labels":data_labels,"values":data_bins} #Заполнение словаря перед отправкой


def RoseDiag(data_asim:list,data_dest:list,step_asim:float,step_dest:float) -> list:
    i = 0
    j = 0
    #bins = {(index_bin_asim, index_bin_dest) : count} 
    bins = {} # Создание корзин для диаграммы
    while i*step_asim <= data_asim[-1]:
        j=0
        while j*step_dest <= data_dest[-1]:
            bins[(i,j)] = 0 #Заполнение ее ключами
            j+=1
        i+=1
    
    for k in range(len(data_asim)):
        bins[(int(data_asim[k]//step_asim),int(data_dest[k]//step_dest))]+=1 #Считывание массива данных и заполнение словаря
    
    list_response = []
    data_size = len(data_asim)
    theta = []
    for i_iter in range(i):
        theta.append(f'{i_iter*step_asim} - {(i_iter+1)*step_asim}')  #Парсинг данных для json формата для передачи на клиент
    for i_iter in range(i):
        for j_iter in range(j):
            r = [0]*i
            r[i_iter] = float((j_iter+1)*step_dest)
            list_response.append(
                {
                    "r": r,
                    "theta": theta,
                    "name": f"{j_iter*step_dest} - {(j_iter+1)*step_dest} , {i_iter*step_asim} - {(i_iter+1)*step_asim}",
                    "marker": {"color": f"rgb(20,50,{bins[(i_iter,j_iter)]/(data_size/4) * 255})"},
                    "type": "barpolar"
                }
            )
    return list_response[::-1]



def Interval_histogram(intervals:list,data:list) -> dict:   
    bins = {} #Создание корзин
    borders = [] # Создание списка интервалов
    i=0
    for el in intervals:
        bins[i] = [intervals[i],0]
        borders.append(list(map(float,el.split('-')))) # при помощи операции Split формируем интервалы
        i+=1   
    for el in data:
        i = 0
        for border in borders:
            if el<=border[1] and el>=border[0]:
                bins[i][1]+=1 # заполнение корзин 
                break
            i+=1
    data_new = [value for value in bins.values()]
    data_labels = [data_new[i][0] for i in range(len(data_new))] #Преобразования словаря
    data_bars = [data_new[i][1] for i in range(len(data_new))]
    return({"labels":data_labels,"values":data_bars}) #Заполнение словаря перед отправкой

def custom_histogram(data, deviation_percent, n_bins) -> dict:  
    data_length = len(data) 
    max_value = data[-1] 
 
     
    bin_sizes = [data_length // n_bins] * n_bins 
    remainder = data_length % n_bins 
    for i in range(remainder): 
        bin_sizes[i] += 1 
 
     
    for i in range(n_bins): 
        if i > 0 and bin_sizes[i] == bin_sizes[i - 1]: 
            adjustment = 1 
            while bin_sizes[i] == bin_sizes[i - 1]: 
                adjustment *= -1 
                bin_sizes[i] += adjustment 
 
    data_labels = [] 
    data_bins = [] 
    bin_counts = [] 
 
     
    bin_edges = [data[sum(bin_sizes[:i])] for i in range(1, n_bins + 1)] 
 
    
    bin_counts.append(sum(data[0] <= data_value < bin_edges[0] for data_value in data)) 
 
     
    for i in range(1, n_bins): 
        deviation = random.uniform(-deviation_percent / 100, deviation_percent / 100) 
        bin_count = int(bin_counts[0] * (1 + deviation) + 0.5) 
        bin_counts.append(bin_count) 
 
     
    prev_bin_max = data[0] 
    cumulative_count = 0   
    for i in range(n_bins): 
         
        bin_max = data[min(cumulative_count + bin_counts[i] - 1, data_length - 1)]   
 
        data_labels.append(f"{prev_bin_max:.2f}-{bin_max:.2f}") 
        data_bins.append((prev_bin_max, bin_max)) 
 
        prev_bin_max = bin_max 
        cumulative_count += bin_counts[i]
    bin_counts = list(map(int,bin_counts))
    return ({"labels": data_labels, "values": bin_counts})




if __name__ == '__main__':
    destinations, asimuts = np.loadtxt('Hists_local.txt',skiprows=1,usecols=(2,3),unpack=True) #Считываем файл
    destinations = np.sort(np.array(destinations))  
    asimuts = np.sort(np.array(asimuts)) #Сортируем данные
    app.run(debug=True,port=3000,host='127.0.0.1')

