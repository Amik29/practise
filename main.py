from flask import Flask,jsonify,render_template,session,request
from flask_restful import Api
import numpy as np
from numba import njit

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
    return jsonify(dataToSend)

@app.route('/<string:data_name>/list')
def Data_Post_Intervals(data_name):
    if data_name == 'destinations':
        data = destinations
    elif data_name == 'asimuts': #Выбор нужного массива для отправки
        data = asimuts
    list_intervals = session['intervals']
    dataToSend = Interval_histogram(list_intervals,data) # Рассчет значений корзин для заданных интервалов 
    print(dataToSend)
    return jsonify(dataToSend)



@app.route('/<string:data_name>/postlist',methods=['POST'])
def Get_Intervals(data_name):
    session['intervals'] = sorted(request.get_json()['array'], key=lambda x: int(x.split('-')[0]))
    print("Intervals_get")
    return jsonify({'message': 'Данные получены' + data_name})
    
@app.route('/RoseDiag/',methods=['POST'])
def Get_RoseDiag():
    print("RoseDiag: data_send")
    return jsonify((RoseDiag(asimuts,destinations,float(request.get_json()['stepAsim']),float(request.get_json()['stepDest']))))



#numba needed
def Uniform_histogram(step,data):
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
    return {"labels":data_labels,"values":data_bins}


def RoseDiag(data_asim,data_dest,step_asim,step_dest):
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
        theta.append(f'{i_iter*step_asim} - {(i_iter+1)*step_asim}')
    print(bins)
    for i_iter in range(i):
        for j_iter in range(j):
            r = [0]*j
            r[i_iter] = float((j_iter+1)*step_dest)
            list_response.append(
                {
                    "r": r,
                    "theta": theta,
                    "name": f"{j_iter*step_dest} - {(j_iter+1)*step_dest} , {i_iter*step_asim} - {(i_iter+1)*step_asim}",
                    "marker": {"color": f"rgb({bins[(i_iter,j_iter)]/(data_size/2) * 255},0,0)"},
                    "type": "barpolar"
                }
            )
    return list_response[::-1]



def Interval_histogram(intervals:list,data:list):   
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
    data_labels = [data_new[i][0] for i in range(len(data_new))]
    data_bars = [data_new[i][1] for i in range(len(data_new))]
    return({"labels":data_labels,"values":data_bars}) 



if __name__ == '__main__':
    destinations, asimuts = np.loadtxt('Hists_base.txt',skiprows=1,usecols=(2,3),unpack=True) #Считываем файл
    destinations = np.sort(np.array(destinations))  
    asimuts = np.sort(np.array(asimuts)) #Сортируем данные
    app.run(debug=True,port=3000,host='127.0.0.1')

