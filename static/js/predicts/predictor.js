const useMyOwnModel = $("#use-my-own-model");
const availableModel = $("#available-model");
const featureSelection = $("#feature-selection");
const regularizationInput = $("#regularization-input")
const epsilonInput = $("#epsilon-input");

const useDefaultModel = $("#use-default-model");

const useMyOwnDatasetCheckbox = $("#use-my-own-dataset");
const availableDatasetSelect = $("#available-dataset");
const newDatasetSourceFile = $("#new-dataset-source");

const chooseModel = $("choose-model");
const chooseDataset = $("choose-dataset");
const chooseTestingDataset = $("choose-testing-dataset");

const firstStep = $("#step-1");
const secondStep = $("#step-2");

const progressBtn = $("#multisteps-form__progress-btn");
const progressPanel = $("#multisteps-form__panel");

const datasetPredict = $("#dataset-predict");

const saveButton = $("#js-save-model-button");

const appUrl = "http://localhost:8000"

let modelSelected = false;
let ownDataset = false;
let ownModel = false;
let mymap = null;
let myDataTable = null;
let info = null;
let legend = null;
let geojson = null;

$(document).ready(function () {
  useMyOwnDataset();
  createNewModel();
  newModelOrExisting();
  getModelDetail();
  getDatasetDetail();
  formSubmit();
  dataTableInit();
  useTheDefaultModel();
  saveButton.hide();
  savingModel();

  mymap = L.map('poverty-mapping').setView([-7.166, 109.852], 7);
  mapLayer(mymap);
  choroplathInfoInit(mymap);
  choroplathLegend(mymap);
  mappingInit(mymap);
});

/**
 * ==============================================
 * 
 * 
 * 
 * start of choroplath JS
 * 
 * 
 * 
 * 
 * ==============================================
 */
function mapLayer(mymap) {
  // L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  //   attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  // }).addTo(mymap);

  L.tileLayer(
    'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
        '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      id: 'mapbox/light-v9',
      tileSize: 512,
      zoomOffset: -1
    }).addTo(mymap);
}

function mappingInit(mymap) {
  $.ajax({
    url: appUrl + "/datasets/geojson/",
    method: 'GET',
    success: function (res) {
      cloropathLayer(mymap, res.data);
    },
  })
}

// get color depending on population density value
function getColor(d) {
  return d > 1000 ? '#800026' :
    d > 18 ? '#BD0026' :
      d > 15 ? '#E31A1C' :
        d > 12 ? '#FC4E2A' :
          d > 9 ? '#FD8D3C' :
            d > 6 ? '#FEB24C' :
              d > 3 ? '#FED976' :
                '#FFEDA0';
}

function style(feature) {
  return {
    weight: 2,
    opacity: 1,
    color: 'white',
    dashArray: '3',
    fillOpacity: 0.7,
    fillColor: getColor(feature.properties.poverty_rate)
  };
}

function highlightFeature(e) {
  var layer = e.target;

  layer.setStyle({
    weight: 5,
    color: '#666',
    dashArray: '',
    fillOpacity: 0.7
  });

  if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    layer.bringToFront();
  }

  info.update(layer.feature.properties);
}

function resetHighlight(e) {
  geojson.resetStyle(e.target);
  info.update();
}

function zoomToFeature(e) {
  mymap.fitBounds(e.target.getBounds());
}

function onEachFeature(feature, layer) {
  layer.on({
    mouseover: highlightFeature,
    mouseout: resetHighlight,
    click: zoomToFeature
  });
}

function choroplathInfoInit(map) {
  // control that shows state info on hover
  info = L.control();

  info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info');
    this.update();
    return this._div;
  };

  info.update = function (props) {
    this._div.innerHTML = '<h4>Porverty Mapping</h4>' + (props ?
      '<b>' + props.region + ', ' + props.province + '</b><br />' + props.poverty_rate + '%' :
      'Hover over a state');
  };

  info.addTo(map);
}

function cloropathLayer(map, mapping) {
  geojson = L.geoJson(mapping, {
    style: style,
    onEachFeature: onEachFeature
  }).addTo(map);

  map.attributionControl.addAttribution(
    'Population data &copy; <a href="http://census.gov/">US Census Bureau</a>');
}

function choroplathLegend(map) {
  legend = L.control({
    position: 'bottomright'
  });

  legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
      grades = [0, 3, 6, 9, 12, 15, 18],
      labels = [],
      from, to;

    for (var i = 0; i < grades.length; i++) {
      from = grades[i];
      to = grades[i + 1];

      labels.push(
        '<i style="background:' + getColor(from + 1) + '"></i> ' +
        from + (to ? '&ndash;' + to : '+'));
    }

    div.innerHTML = labels.join('<br>');
    return div;
  };

  legend.addTo(map);
}

function setMarkers(response, mymap) {
  response.forEach(res => {
    let myMarker = L.marker([res.latitude, res.longitude]);
    let icon = myMarker.options.icon;
    icon.options.iconSize = [12, 20];
    icon.options.iconAnchor = [6, 20];
    icon.options.popupAnchor = [1, -34]
    icon.options.tooltipAnchor = [16, -28]
    icon.options.shadowSize = [20, 20]

    myMarker.setIcon(icon);
    myMarker.addTo(mymap);


    let content = `
        <p>${res.city}, ${res.province}</p>
        <p>Poverty Rate (%): ${res.poverty_rate}</p>
        `;

    myMarker.bindPopup(content);

    myMarker.on('mouseover', function (e) {
    });
    myMarker.on('mouseout', function (e) {
    });
  });
}
/**
 * ==============================================
 * 
 * 
 * 
 * end of choroplath JS
 * 
 * 
 * 
 * 
 * ==============================================
 */


/**
 * ===============================================
 * start of micro component init
 * ===============================================
 */

function dataTableInit() {
  myDataTable = $('#js-poverty-result').DataTable();
}

/**
 * ===============================================
 * end of micro component init
 * ===============================================
 */

/**
 * ===============================================
 * 
 * 
 * 
 * start of predict form submit process
 * 
 * 
 * 
 * ===============================================
 */
function formSubmit() {
  $("#predictor-form").submit(function (e) {
    e.preventDefault();
    const url = $(this).prop("action");

    $.ajax({
      url: `${appUrl}/api/v1/predict/`,
      method: 'POST',
      data: new FormData(this),
      dataType: 'json',
      contentType: false,
      cache: false,
      processData: false,
      success: function (res) {
        processAjaxResponse(res);
      },
      error: function (err) {
        if (err.status != 500){
          showErrorModal(err.responseJSON.message);
        }
      }
    });
  });
}

function processAjaxResponse(res) {
  if (!res.best_model) {
    $("#js-r2").text(res.accuracy_value.toFixed(3));
    $("#js-rmse").text(res.error_value.toFixed(3));
    $("#js-regularization").text(res.regularization);
    $("#js-epsilon").text(res.epsilon);
    $("#js-feature_num").text(res.feature_num);

    $("#js-sorted_feature ol").remove();
    const list = document.createElement('ol');

    res.sorted_feature.forEach(item => {
      const listItem = document.createElement('li');

      listItem.innerHTML = `${item}`;
      list.appendChild(listItem);
    });

    $("#js-sorted_feature").append(list);

  } else {
    $("#js-r2").text("");
    $("#js-rmse").text("");
    $("#js-regularization").text("");
    $("#js-epsilon").text("");
    $("#js-feature_num").text("");

    $("#js-sorted_feature ol").remove();
  }
  populateTable(res.result_cities);
  populateChartResponse(res);
  scrollPageAfterForm();

  cloropathLayer(mymap, res.region_geojson);

  if (!res.best_model && res.new_model && res.success) {
    saveButton.show();
    storeImportantData(res);
  }
}

function populateChartResponse(res) {
  if (res.new_model && !res.best_model) {
    $("#js-chart-box").css({ 'display': 'block', });
    $("#js-result_chart").prop("src", `data:image/png;base64,${res.result_chart}`);
  } else {
    $("#js-chart-box").css({ 'display': 'none', });
  }
}

function scrollPageAfterForm() {
  // scroll to form
  $('html, body').animate({
    scrollTop: $("#js-result-panels").offset().top
  }, 600);
}

function populateTable(data) {
  myDataTable.clear().draw();
  let number = 1;
  data.forEach(item => {
    myDataTable.row.add([
      number,
      item.city,
      item.province,
      item.poverty_rate + " %",
    ]).draw();
    number++;
  });
}

function storeImportantData(res) {
  delete res.result_chart;
  delete res.sorted_feature;
  delete res.region_geojson;
  delete res.result_cities;
  delete res.new_model;

  sessionStorage.setItem('prediction_data', JSON.stringify(res));
}
/**
 * ===============================================
 * 
 * 
 * 
 * end of predict form submit process
 * 
 * 
 * 
 * ===============================================
 */

/**
 * ===============================================
 * 
 * 
 * 
 * start of saving model process
 * 
 * 
 * 
 * ===============================================
 */

function savingModel() {
  $("#new-model-name-form").submit(function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    let formObject = {};

    formData.forEach((value, key) => {
      formObject[key] = value
    });

    const data = JSON.parse(JSON.stringify(formObject));
    const sessionInformation = JSON.parse(sessionStorage.getItem("prediction_data"));

    const predictInformation = {
      ...data,
      ...sessionInformation,
    };

    $.ajax({
      url: `${appUrl}/api/v1/ml_model/`,
      method: 'POST',
      data: predictInformation,
      success: function (res) {
        respondToSavedModel(res);
      },
      error: function (err) {
        if (err.status != 500){
          showErrorModal(err.responseJSON.message);
        }
      }
    });
  });
}

function respondToSavedModel(res) {
  availableModel.append(`<option value="${res.id}">${res.name} - ${res.accuracy_value}</option>`);

  sessionStorage.removeItem("prediction_data")
  saveButton.hide();

  $('#js-save-model-modal').modal('hide');

  Swal.fire(
    "Saved!",
    "Model Has Been Saved",
    "success"
  );
  
}

/**
 * ===============================================
 * 
 * 
 * 
 * end of saving model process
 * 
 * 
 * 
 * ===============================================
 */

/**
 * ===============================================
 * 
 * 
 * 
 * start of check boxes responses
 * 
 * 
 * 
 * ===============================================
 */
function useTheDefaultModel() {
  useDefaultModel.click(function () {
    if ($(this).prop("checked") == true) {
      useMyOwnModel.prop("disabled", true);
      availableModel.prop("disabled", true);
      featureSelection.prop("disabled", true);
      regularizationInput.prop("disabled", true);
      epsilonInput.prop("disabled", true);
      // =========================================
    } else if ($(this).prop("checked") == false) {
      useMyOwnModel.prop("disabled", false);
      availableModel.prop("disabled", useMyOwnModel.prop("checked"));
      featureSelection.prop("disabled", !useMyOwnModel.prop("checked"));
      regularizationInput.prop("disabled", !useMyOwnModel.prop("checked"));
      epsilonInput.prop("disabled", !useMyOwnModel.prop("checked"));
    }
  });
}

function useMyOwnDataset() {
  useMyOwnDatasetCheckbox.click(function () {
    if ($(this).prop("checked") == true) {
      availableDatasetSelect.prop("disabled", true);
      newDatasetSourceFile.prop("disabled", false);
      ownDataset = true;
      $("#js-div-dataset-detail").css({ "display": "none" });
    } else if ($(this).prop("checked") == false) {
      availableDatasetSelect.prop("disabled", false);
      newDatasetSourceFile.prop("disabled", true);
      ownDataset = false;
      $("#js-div-dataset-detail").css({ "display": "block" });
    }
  });
}

function createNewModel() {
  useMyOwnModel.click(function () {
    if ($(this).prop("checked") == true) {
      availableModel.prop("disabled", true);
      featureSelection.prop("disabled", false);
      regularizationInput.prop("disabled", false);
      epsilonInput.prop("disabled", false);
      ownModel = true;
      $("#js-div-model-detail").css({ "display": "none" });
    } else {
      availableModel.prop("disabled", false);
      featureSelection.prop("disabled", true);
      regularizationInput.prop("disabled", true);
      epsilonInput.prop("disabled", true);
      ownModel = false;
      $("#js-div-model-detail").css({ "display": "block" });
    }
  });
}

function newModelOrExisting() {
  availableModel.on("change", function () {
    if (availableModel.val() != "") {
      // TODO
    }
  });
}

function modelValidCheck() {
  firstStep.click(function () {
    if (!availableModel.val() && !ownModel) {
      errorDetail = {
        "model": "Please choose existing model or create new machine learning model"
      };
      showErrorModal(errorDetail);
    } else { }
  });
}
/**
 * ===============================================
 * 
 * 
 * 
 * end of check boxes responses
 * 
 * 
 * 
 * ===============================================
 */

/**
 * ===============================================
 * 
 * 
 * 
 * start of getter
 * 
 * 
 * 
 * ===============================================
 */

function getModelDetail() {
  availableModel.change(function (e) {
    const modelId = $(this).val();
    if (modelId != "" || modelId != null || modelId != undefined) {
      $.ajax({
        url: appUrl + `/api/v1/ml_model/${modelId}`,
        method: 'GET',
        success: function (res) {
          const response = res;

          $("#js-div-model-detail").css({ "display": "block" });
          $("#js-model-fs-used").text(response.feature_selection);
          $("#js-model-r2-value").text(response.accuracy_value);
          $("#js-model-rmse-value").text(response.error_value);
          $("#js-model-total-features-used").text(response.feature_num);
        },
        error: function (e) {
          console.log(e);
        }
      });
    }
    panelHeightChanged();
  });
}

function getDatasetDetail() {
  availableDatasetSelect.change(function (e) {
    const datasetId = $(this).val();
    if (datasetId != "" || datasetId != null || datasetId != undefined) {
      $.ajax({
        url: appUrl + `/api/v1/dataset_profile/${datasetId}`,
        method: 'GET',
        success: function (res) {
          const response = res;

          $("#js-div-dataset-detail").css({ "display": "block" });
          $("#js-dataset-total-rows").text(response.total_row);
          $("#js-dataset-valid-date").text(response.valid_date);
        },
        error: function (e) {
          console.log(e);
        }
      })
    }
  });
}

function getPredictionId(id) {
  $.ajax({
    url: `/predicts/prediction_result/${id}/`,
    method: 'GET',
    success: function (res) { }
  });
}

/**
 * ===============================================
 * 
 * 
 * 
 * end of getter
 * 
 * 
 * 
 * ===============================================
 */

function showErrorModal(errorData) {
  const list = document.createElement('ul');

  for (let [key, value] of Object.entries(errorData)) {
    const listItem = document.createElement('li');

    listItem.innerHTML = `${value}`;
    list.appendChild(listItem);
  }

  Swal.fire(
    "Ooops!",
    list,
    "error"
  );
}

/**
 * ===============================================
 * 
 * 
 * 
 * end of swal fires
 * 
 * 
 * 
 * ===============================================
 */

/**
 * ===============================================
 * miscellaneous functions
 * ===============================================
 */
function panelHeightChanged() {
  /**
   * TODO
   * fix height change bug
   */
  const activePanel = getActivePanel();
  const activePanelHeight = activePanel.offsetHeight;
  const modeldetailHeight = $("#js-div-model-detail").height();
  console.log(activePanelHeight + modeldetailHeight);

  $("#js-form-container").css({ "height": (activePanelHeight + modeldetailHeight) + "px" })
}