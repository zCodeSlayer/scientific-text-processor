const graph = new graphology.Graph();

const sigmaInstance = new Sigma(graph, document.getElementById("container"), {
  renderEdgeLabels: true
});

document.getElementById('search-button').addEventListener('click', () => {
  const searchTerm = document.getElementById('node-search-input').value.toLowerCase();
  if (!searchTerm) return;

  let foundNode = graph.findNode((node, attributes) => {
      return attributes.label && attributes.label.toLowerCase() === searchTerm;
    });
  if (!foundNode) {
    alert('Node not found!');
    return;
  }

  let neighbors = graph.neighbors(foundNode);
  let edges = graph.edges(foundNode);

  let subGraph = new graphology.Graph();
  subGraph.addNode(foundNode, { ...graph.getNodeAttributes(foundNode) });
  neighbors.forEach(neighbor => subGraph.addNode(neighbor, { ...graph.getNodeAttributes(neighbor) }));
  edges.forEach(edge => subGraph.addEdge(graph.source(edge), graph.target(edge), { ...graph.getEdgeAttributes(edge) }));

  sigmaInstance.setGraph(subGraph);
  sigmaInstance.refresh();
});

const collapsibleWidget = document.getElementById('collapsible-widget');
const widgetList = document.getElementById('widget-list');

collapsibleWidget.addEventListener('click', () => {
  widgetList.classList.toggle('hidden');
  if (!widgetList.classList.contains('hidden')) {
    fetch('http://0.0.0.0:8000/scientific-catalogs/titles')
      .then(response => response.json())
      .then(data => {
        updateWidgetList(data.catalogsTitles);
      })
      .catch(error => console.error('Error fetching catalog titles:', error));
  }
});

function updateWidgetList(titles) {
  widgetList.innerHTML = '';
  titles.forEach(title => {
    const listItem = document.createElement('li');
    listItem.textContent = title;
    listItem.addEventListener('click', () => {
      fetch(`http://0.0.0.0:8000/scientific-catalog-graph/${title}`)
        .then(response => response.json())
        .then(data => {
          sigmaInstance.setGraph(graph);
          graph.clear();
          data.forEach(link => {
            if (!graph.hasNode(link.term_from.hash.toString())) {
              graph.addNode(link.term_from.hash.toString(), { 
                label: link.term_from.title,
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
              size: link.weight,
              color: "purple",
              label: `${link.weight}`
            });
          });
          sigmaInstance.refresh();
        })
        .catch(error => console.error('Error fetching catalog entry:', error));
    });
    widgetList.appendChild(listItem);
  });
}

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
  const file = fileInput.files[0];

  if (!textValue || !file) {
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

// Логика для нового виджета с select
const toggleSelectFormButton = document.getElementById('toggle-select-form-button');
const selectForm = document.getElementById('select-form');
const dropdownSelect = document.getElementById('dropdown-select');

if (toggleSelectFormButton && selectForm) {
  toggleSelectFormButton.addEventListener('click', () => {
    selectForm.classList.toggle('hidden');
    if (!selectForm.classList.contains('hidden')) {
      toggleSelectFormButton.classList.add('active');
      // Загружаем варианты для select
      fetch('http://0.0.0.0:8000/scientific-catalogs/titles')
        .then(response => response.json())
        .then(data => {
          if (dropdownSelect) {
            dropdownSelect.innerHTML = '';
            data.catalogsTitles.forEach(title => {
              const option = document.createElement('option');
              option.value = title;
              option.textContent = title;
              dropdownSelect.appendChild(option);
            });
          }
        })
        .catch(error => console.error('Ошибка при загрузке названий каталогов:', error));
    } else {
      toggleSelectFormButton.classList.remove('active');
    }
  });
} 

const analyzeTextButton = document.getElementById('analyze-text-button');
const fileInputSelect = document.getElementById('file-input-select');

const analyzeModal = document.getElementById('analyze-modal');
const closeAnalyzeModal = document.getElementById('close-analyze-modal');
const analyzeResultsTable = document.getElementById('analyze-results-table').querySelector('tbody');

if (closeAnalyzeModal && analyzeModal) {
  closeAnalyzeModal.addEventListener('click', () => {
    analyzeModal.style.display = 'none';
  });
}

if (analyzeTextButton && fileInputSelect && dropdownSelect) {
  analyzeTextButton.addEventListener('click', async () => {
    const catalogName = dropdownSelect.value;
    const file = fileInputSelect.files[0];
    if (!catalogName || !file) {
      alert('Пожалуйста, выберите каталог и файл для анализа.');
      return;
    }
    const formData = new FormData();
    formData.append('article_file', file);
    try {
      const response = await fetch(`http://0.0.0.0:8000/analyze-text/${encodeURIComponent(catalogName)}`, {
        method: 'POST',
        body: formData
      });
      if (response.ok) {
        const result = await response.json();
        // Показываем модальное окно с результатами
        if (result.terms_frequency && Array.isArray(result.terms_frequency)) {
          analyzeResultsTable.innerHTML = '';
          const total = result.terms_frequency.reduce((sum, [, freq]) => sum + freq, 0) || 1;
          result.terms_frequency.forEach(([term, freq]) => {
            const percent = ((freq / total) * 100).toFixed(2);
            const row = document.createElement('tr');
            row.innerHTML = `<td>${term}</td><td>${freq}</td><td>${percent}</td>`;
            analyzeResultsTable.appendChild(row);
          });
          analyzeModal.style.display = 'flex';
        } else {
          alert('Результат анализа: ' + JSON.stringify(result));
        }
      } else {
        const errorData = await response.json();
        let errorMsg = errorData.detail;
        if (!errorMsg) {
          errorMsg = JSON.stringify(errorData);
        }
        alert('Ошибка: ' + errorMsg);
      }
    } catch (error) {
      alert('Ошибка при отправке запроса: ' + error);
    }
  });
} 