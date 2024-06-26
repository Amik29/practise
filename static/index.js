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

function valid_range(min,max,data){
  console.log(data);
  for (i=0;i<data.length;i++){
    borders = data[i].split('-');
    if (min>=borders[0] && min<borders[1] || max<=borders[1] && max>borders[0])
      return false;
  }
  return max>min;
}

function addInterval(id) {
  var form
  var cur_dataset
  try{
  if (id == 1){
    form = new FormData(document.getElementById("dest_form"));
    cur_dataset = list_detection(id)[1];
    if (!valid_range(Number(form.get('min')),Number(form.get('max')),cur_dataset))
    {
      throw "Неправильные границы"
    }
    dataset_destinations.push(form.get('min') + '-' + form.get('max'))
  }
  else {
    form = new FormData(document.getElementById("asimut_form"));
    cur_dataset = list_detection(id)[1];
    if (!valid_range(Number(form.get('min')),Number(form.get('max')),cur_dataset))
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

function changeChart(){
  var dropdown = document.getElementById("chartType")
  var selectedElement = dropdown.options[dropdown.selectedIndex].value;
  
  var chart1 = document.getElementById("DestinationsChart");
  var chart2 = document.getElementById("AsimutsChart"); 
  var chart3 = document.getElementById("PercentegeChart");
  var chart4 = document.getElementById("RoseChart");

  chart1.style.display = "none";
  chart2.style.display = "none";
  chart3.style.display = "none";
  chart4.style.display = "none";

  switch(selectedElement) {
    case "destinations":
      chart1.style.display = "block";
      break;
    case "asimuts":
      chart2.style.display = "block";
      break;
    case "percentege":
      chart3.style.display = "block";
      break;
    case "rose":
      chart4.style.display = "block";
      break;
  }
}

function Submit_data_intervals(id){
    let arr = [];
    if (id == 1)
    {
      arr = dataset_destinations;
      var url = 'http://127.0.0.1:3000/destinations/postlist'
    } 
    else 
    {
      arr = dataset_asimuts;
      var url = 'http://127.0.0.1:3000/destinations/postlist'
    }
    fetch(url,{
      method:'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({array: arr})
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error =>console.error('Ошибка:',error));
}

function checkTypeBins(value,id){
  buttonDest = document.getElementById('varDest')
  boxDest = document.getElementById('stepDest')
  buttonAsim = document.getElementById('varAsim')
  boxAsim = document.getElementById('stepAsim')
  
  if(value == "intervals")
    if (id == 1){
      buttonDest.style = "display:inline";
      boxDest.style = "display:none";
    }
    else
    {
    buttonAsim.style = "display:inline";
    boxAsim.style = "display:none";
    }
    else
    if (id == 1)
    {
      buttonDest.style = "display:none"
      boxDest.style = "display:inline";
    }
    else
    {
      buttonAsim.style = "display:none"
      boxAsim.style = "display:inline";
    }
  
}

function getUrl(id){
  switch(id){
    case 1:
      var url = 'http://127.0.0.1:3000/destinations/'
      var radio = document.getElementById('typeDest1');
      var value = document.getElementById('stepDest').value;
      if (radio.checked){
        url = url + 'list';
      }
      else {
        url = url + value;
      }
      break;
    case 2:
      var url = 'http://127.0.0.1:3000/asimuts/'
      var radio = document.getElementById('typeAsim1');
      var value = document.getElementById('stepAsim').value;
      if (radio.checked){
        url = url + 'list';
      }
      else {
        url = url + value;
      }
      break;
    case 3:
      var url = 'http://127.0.0.1:3000/PercentDiag';
      break;
    }
    console.log(url)
  return url
}

function fetchData(Id) {
  var chart = Chart.getChart('myChart' + Id);
  var url = getUrl(Id)
  switch(Id){
    case 3:
      data_name = document.getElementById("typeData1").checked ? "destinations" : "asimuts"
      console.log(data_name)
      fetch(url,{
        method:'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({data_name : data_name, percent: document.getElementById("percent_num").value, num_bins:document.getElementById("number_bins").value })
      })
      .then(response => response.json())
      .then(data => {
          // Данные успешно получены, теперь можно отобразить график
          if(chart){
            chart.destroy();
          }
          drawChart(data,Id);
      })
      .catch(error => {
          console.error('Произошла ошибка при получении данных:', error);
      });
      break;
    case 1:
      fetch(url,{
      })
      .then(response => response.json())
      .then(data => {
          // Данные успешно получены, теперь можно отобразить график
          if(chart){
            chart.destroy();
          }
          drawChart(data,Id);
      })
      .catch(error => {
          console.error('Произошла ошибка при получении данных:', error);
      });
      break;
      case 2:
      fetch(url,{
      })
      .then(response => response.json())
      .then(data => {
          // Данные успешно получены, теперь можно отобразить график
          if(chart){
            chart.destroy();
          }
          drawChart(data,Id);
      })
      .catch(error => {
          console.error('Произошла ошибка при получении данных:', error);
      });
      break;
  }
}

function drawChart(data,Id) {
  var ctx = document.getElementById('myChart' + Id).getContext('2d');
  var label = '';
  switch(Id)
  {
    case 1:
      label = 'Удаления';
      break;
    case 2:
      label = 'Азимут';
      break;
    case 3:
      label = 'Удаления';
      break;
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


function RoseDiag(){
  data_response = fetch("http://127.0.0.1:3000/RoseDiag",
  {
    method:'POST',
    headers: {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify({stepDest: document.getElementById("RoseStepDest").value, stepAsim:document.getElementById("RoseStepAsim").value })
  })
  .then(response => response.json())
  .then(data => {
    console.log(data)
    const graph = document.getElementById('graph'); 
    graph.innerHTML = '';
    var layout = {
      title: "Роза-Диаграмма , 0 азимут - север, 1) Удаление, 2) Азимут",
      font: {size: 16},
      legend: {font: {size: 16}}, 
      polar: {
        barmode: "overlay",
        bargap: 0,
        radialaxis: {angle: 0, dtick: 300},
        angularaxis: {direction: "clockwise"}
      }
    }
    Plotly.newPlot("graph", data, layout)
  })
  .catch(error => console.error('Ошибка:', error))

}

function PercentDiag(){
  var chart = Chart.getChart('myChart3');
  data_response = fetch("http://127.0.0.1:3000/PercentDiag",
  {
    method:'POST',
    headers: {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify({data_name : data_name, percent: document.getElementById("percent_num").value, num_bins:document.getElementById("number_bins").value })
  })
  .then(response => response.json())
  .then(data => {
    console.log(data)
    if(chart){
      chart.destroy();
    }
    drawChart(data,Id,1);
  })
  .catch(error => console.error('Ошибка:', error))

}