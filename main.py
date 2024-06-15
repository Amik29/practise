from flask import Flask,jsonify,render_template,request
from flask_restful import Api
import numpy as np


app = Flask(__name__)
api = Api()

api.init_app(app)

@app.route('/')
def responser():
    return render_template('index.html')



@app.route('/<string:data_name>/<float:step>/')
@app.route('/<string:data_name>/<int:step>/')
def Data_Post_Uniform(data_name,step):
    if data_name == 'destinations':
        data = destinations
    elif data_name == 'asimuts': #Выбор нужного массива для отправки
        data = asimuts
    dataToSend = Uniform_histogram(step,data) #Построение словаря с подписями интервалов и количествами попадания в них для слуая с step=const.
    return jsonify(dataToSend)

@app.route('/<string:data_name>/list', methods=['POST'])
def Data_Post_Intervals(data_name):
    if data_name == 'destinations':
        data = destinations
    elif data_name == 'asimuts': #Выбор нужного массива для отправки
        data = asimuts
    list_intervals = request.json['intervals']
    dataToSend = Interval_histogram(list_intervals,data) #Построение словаря с подписями интервалов и количествами попадания в них для слуая с интервалами
    return jsonify(dataToSend)
    
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


def Interval_histogram(intervals:list,data:list):   
    bins = {}
    borders = []
    i=0
    for el in intervals:
        bins[i] = [intervals[i],0]
        borders.append(list(map(float,el.split('-'))))
        i+=1   
    for el in data:
        i = 0
        for border in borders:
            if el<=border[1] and el>=border[0]:
                bins[i][1]+=1
                break
            i+=1
    data_new = [value for value in bins.values()]
    data_labels = [data_new[i][0] for i in range(len(data_new))]
    data_bars = [data_new[i][1] for i in range(len(data_new))]
    return({"labels":data_labels,"values":data_bars})


def Reading_file():
    destination = []
    asimuts = []
    with open('Hists_base.txt', 'r') as file:
        next(file)
        for line in file:
            data = line.split()
            destination.append(float(data[2]))
            asimuts.append(float(data[3]))
    return destination, asimuts


if __name__ == '__main__':
    destinations, asimuts = Reading_file() #Считываем файл
    destinations = np.sort(np.array(destinations))  
    asimuts = np.sort(np.array(asimuts)) #Сортируем данные
    app.run(debug=True,port=3000,host='127.0.0.1')

