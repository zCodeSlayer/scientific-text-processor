// Create a graphology graph
const graph = new graphology.Graph();
graph.addNode("1", { label: "Node 1", x: 0, y: 0, size: 10, color: "blue" });
graph.addNode("2", { label: "Node 2", x: 1, y: 1, size: 20, color: "red" });
graph.addEdge("1", "2", { type: 'arrow', size: 5, color: "purple", label: "Edge from 1 to 2" });

// Instantiate sigma.js and render the graph
const sigmaInstance = new Sigma(graph, document.getElementById("container"), {
  renderEdgeLabels: true
});

document.getElementById('search-button').addEventListener('click', () => {
  const searchTerm = document.getElementById('node-search-input').value.toLowerCase();
  if (!searchTerm) return;

  let foundNode = null;
  // Ищем по ID, затем по label
  if (graph.hasNode(searchTerm)) {
      foundNode = graph.getNodeAttributes(searchTerm);
      // Важно: для goTo нужны исходные x, y, а не те, что sigma трансформирует для отображения.
      // Если sigmaInstance.getGraph() возвращает тот же объект graphology, то x, y должны быть доступны.
  } else {
      graph.forEachNode((node, attributes) => {
          if (attributes.label && attributes.label.toLowerCase() === searchTerm) {
              foundNode = attributes; 
              // Здесь мы также предполагаем, что attributes содержит x и y
          }
      });
  }

  if (foundNode && typeof foundNode.x === 'number' && typeof foundNode.y === 'number') {
    sigmaInstance.getCamera().animate(
      { x: foundNode.x, y: foundNode.y, ratio: 0.5 }, // ratio: 0.5 для приближения
      { duration: 500 } 
    );
    // Можно добавить логику для выделения вершины, например, изменив её цвет
    // graph.setNodeAttribute(foundNode.key || searchTerm, 'color', 'green'); // searchTerm если искали по ID, foundNode.key если он есть
    // sigmaInstance.refresh(); // Не забыть обновить, если меняем атрибуты
  } else {
    alert('Node not found!');
  }
});

// Collapsible widget functionality
const collapsibleWidget = document.getElementById('collapsible-widget');
const widgetList = document.getElementById('widget-list');

collapsibleWidget.addEventListener('click', () => {
  widgetList.classList.toggle('hidden');
  if (!widgetList.classList.contains('hidden')) {
    // Fetch data and update list when widget is opened
    fetch('http://0.0.0.0:8000/scientific-catalogs/titles')
      .then(response => response.json())
      .then(data => {
        updateWidgetList(data.catalogsTitles);
      })
      .catch(error => console.error('Error fetching catalog titles:', error));
  }
});

function updateWidgetList(titles) {
  // Clear existing list items
  widgetList.innerHTML = '';
  // Add new list items
  titles.forEach(title => {
    const listItem = document.createElement('li');
    listItem.textContent = title;
    listItem.addEventListener('click', () => {
      fetch(`http://0.0.0.0:8000/scientific-catalog-graph/${title}`)
        .then(response => response.json())
        .then(data => {
          // Очищаем предыдущий граф
          graph.clear();
          // Добавляем новые узлы и ребра
          data.forEach(link => {
            if (!graph.hasNode(link.term_from.hash.toString())) {
              graph.addNode(link.term_from.hash.toString(), { 
                label: link.term_from.title,
                // Для простоты разместим узлы случайным образом
                x: Math.random(), 
                y: Math.random(), 
                size: 10, 
                color: "blue" 
              });
            }
            if (!graph.hasNode(link.term_to.hash.toString())) {
              graph.addNode(link.term_to.hash.toString(), { 
                label: link.term_to.title,
                x: Math.random(), 
                y: Math.random(), 
                size: 10, 
                color: "red" 
              });
            }
            graph.addEdge(link.term_from.hash.toString(), link.term_to.hash.toString(), {
              type: 'arrow',
              size: link.weight, // Используем вес связи для размера ребра
              color: "purple",
              label: `Weight: ${link.weight.toFixed(2)}`
            });
          });
          sigmaInstance.refresh(); // Обновляем отображение графа
        })
        .catch(error => console.error('Error fetching catalog entry:', error));
    });
    widgetList.appendChild(listItem);
  });
}

// Input form functionality
const toggleFormButton = document.getElementById('toggle-form-button');
const inputForm = document.getElementById('input-form');

toggleFormButton.addEventListener('click', () => {
  inputForm.classList.toggle('hidden');
}); 

const generateGraphButton = document.getElementById('generate-graph-button');
const textInput = document.getElementById('text-input');
const fileInput = document.getElementById('file-input');

generateGraphButton.addEventListener('click', async () => {
  const textValue = textInput.value.trim();
  const file = fileInput.files[0]; // Получаем сам файл, а не только его имя

  if (!textValue || !file) { // Проверяем наличие файла, а не fileInput.value
    alert('Введите информацию о семантическом графе полностью');
    return; 
  }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`http://0.0.0.0:8000/generate-graph/${encodeURIComponent(textValue)}`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      alert('Граф успешно сгенерирован!');
      console.log('Ответ сервера:', result);
      // Тут можно добавить логику для обновления списка каталогов или отображения нового графа
      // Например, можно снова вызвать fetch для /scientific-catalogs/titles и обновить widgetList
      fetch('http://0.0.0.0:8000/scientific-catalogs/titles')
        .then(res => res.json())
        .then(data => {
          updateWidgetList(data.catalogsTitles);
        })
        .catch(error => console.error('Error fetching catalog titles after generation:', error));
    } else {
      const errorData = await response.json();
      alert(`Ошибка при генерации графа: ${errorData.detail || response.statusText}`);
      console.error('Ошибка от сервера:', errorData);
    }
  } catch (error) {
    alert('Произошла ошибка при отправке запроса.');
    console.error('Сетевая ошибка или ошибка выполнения запроса:', error);
  }
}); 