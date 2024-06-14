var chart;
var dataset_destinations = []
var dataset_asimuts = []

function list_detection(id){
  var cur_dataset
  var list
  if (id == 1){
    list =
    document.getElementById("destinations_list");
    cur_dataset = dataset_destinations
  }
  else {
    list =
    document.getElementById("asimuts_list");
    cur_dataset = dataset_asimuts
  }
  return [list,cur_dataset];
}

function openDialog(id){
  if (id == 1){
    document.getElementById("Interval_dest_dialog").showModal();
  }
  else {
    document.getElementById("Interval_asim_dialog").showModal();
  }
  var tmp = list_detection(id);
  list_display(tmp[0],tmp[1],id)
}

function list_display(list,dataset,id){
  list.innerHTML='';
  for (i=0;i<dataset.length;i++){
      let li =
          document.createElement("li");
      li.innerText = dataset[i];
      li.id = id;
      let button = document.createElement('button');
      button.innerText = 'x';
      button.addEventListener('click', function(e) {
        tmp_id = e.currentTarget.parentNode.id;
        tmp_list = list_detection(tmp_id);
        tmp_list[1].splice(e.currentTarget.innerText,1);
        list_display(tmp_list[0],tmp_list[1],id);
      });
      li.appendChild(button);
      list.appendChild(li);
  };
};

function valid_range(min,max){
  return max>min;
}

function addInterval(id) {
  var form
  try{
  if (id == 1){
    form = new FormData(document.getElementById("dest_form"));
    if (!valid_range(form.get('min'),form.get('max')))
    {
      throw "Неправильные границы"
    }
    dataset_destinations.push(form.get('min') + '-' + form.get('max'))
  }
  else {
    form = new FormData(document.getElementById("asimut_form"));
    if (!valid_range(form.get('min'),form.get('max')))
    {
      throw "Неправильные границы"
    }
    dataset_asimuts.push(form.get('min') + '-' + form.get('max'))
    
  }
  var tmp = list_detection(id)
  list_display(tmp[0],tmp[1],id)
  }
  catch(error){
    alert(error);
  }
};



function fetchData(Id) {
  var chart = Chart.getChart('myChart' + Id);
  if(chart){
    chart.destroy();
  }
  if (Id == 1){
    var url = 'http://127.0.0.1:3000/destinations/40'
  }
  else {
    var url = 'http://127.0.0.1:3000/asimuts/10.0';
  }
  fetch(url)
  .then(response => response.json())
  .then(data => {
      // Данные успешно получены, теперь можно отобразить график
      drawChart(data,Id);
  })
  .catch(error => {
      console.error('Произошла ошибка при получении данных:', error);
  });
}

function drawChart(data,Id) {
  var ctx = document.getElementById('myChart' + Id).getContext('2d');
  var label = '';
  if (Id==1){
    label = 'Удаления'
  }
  else{
    label = 'Азимут'
  }
  var chart = new Chart(ctx, {
      type: 'bar',
      data: {
          labels: data.labels,
          datasets: [{
              label: label,
              data: data.values,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
          }]
      },
      options: {
          scales: {
              yAxes: [{
                  ticks: {
                      beginAtZero: true
                  }
              }]
          }
      }
  });
}