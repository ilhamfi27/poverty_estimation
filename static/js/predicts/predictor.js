const useMyOwnModel = $("#use-my-own-model");
const availableModel = $("#available-model");
const featureSelection = $("#feature-selection");
const regularizationInput = $("#regularization-input")
const epsilonInput = $("#epsilon-input");

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

let modelSelected = false;
let ownDataset = false;
let ownModel = false;
let mymap = null;
let myDataTable = null;

$(document).ready(function () {
  useMyOwnDataset();
  createNewModel();
  newModelOrExisting();
  formSubmit();
  dataTableInit();

  mymap = L.map('poverty-mapping').setView([-7.166, 109.852], 7);
  mapLayer(mymap);
});

function mapLayer(mymap) {
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mymap);
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

function dataTableInit() {
  myDataTable = $('#js-poverty-result').DataTable();
}

function formSubmit() {
  $("#predictor-form").submit(function (e) {
    e.preventDefault();
    const url = $(this).prop("action");

    $.ajax({
      url: url,
      method: 'POST',
      data: new FormData(this),
      dataType: 'json',
      contentType: false,
      cache: false,
      processData: false,
      success: function (res) {
        console.log(res);
        if (res.success) {
          $("#js-r2").text(res.r2);
          $("#js-rmse").text(res.rmse);
          $("#js-regularization").text(res.regularization);
          $("#js-epsilon").text(res.epsilon);
          $("#js-feature_num").text(res.feature_num);
          $("#js-result_chart").prop("src", `data:image/png;base64,${res.result_chart}`);

          $("#js-sorted_feature ol").remove();
          const list = document.createElement('ol');

          res.sorted_feature.forEach(item => {
            const listItem = document.createElement('li');

            listItem.innerHTML = `${item}`;
            list.appendChild(listItem);
          });

          $("#js-sorted_feature").append(list);
          populateTable(res.result_cities);
          setMarkers(res.result_cities, mymap);

          // scroll to form
          $('html, body').animate({
            scrollTop: $("#js-result-panels").offset().top
          }, 600);
        } else {
          console.log("ERROR");
        }
      },
      error: function (err) {
        console.log(err);
      }
    });
  });
}

function populateTable(data) {
  myDataTable.clear().draw();
  let number = 1;
  data.forEach(item => {
    myDataTable.row.add([
      number,
      item.city,
      item.province,
      item.poverty_rate,
    ]).draw();
    // item.number = number;
    number++;
  });
  // myDataTable.dataTable({
  //   "aaData": data,
  //   "columns": [
  //     { "data": "number" },
  //     { "data": "city" },
  //     { "data": "province" },
  //     { "data": "poverty_rate" }
  //   ]
  // });
}

function useMyOwnDataset() {
  useMyOwnDatasetCheckbox.click(function () {
    if ($(this).prop("checked") == true) {
      availableDatasetSelect.prop("disabled", true);
      newDatasetSourceFile.prop("disabled", false);
      ownDataset = true;
    } else if ($(this).prop("checked") == false) {
      availableDatasetSelect.prop("disabled", false);
      newDatasetSourceFile.prop("disabled", true);
      ownDataset = false;
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
    } else {
      availableModel.prop("disabled", false);
      featureSelection.prop("disabled", true);
      regularizationInput.prop("disabled", true);
      epsilonInput.prop("disabled", true);
      ownModel = false;
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
    console.log("HAHAHA");
    if (!availableModel.val() && !ownModel) {
      errorDetail = {
        "model": "Please choose existing model or create new machine learning model"
      };
      showErrorModal(errorDetail);
    } else { }
  });
}

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

function getPredictionId(id) {
  $.ajax({
    url: `/predicts/prediction_result/${id}/`,
    method: 'GET',
    success: function (res) { }
  });
}