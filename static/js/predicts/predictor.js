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

$(document).ready(function () {
  useMyOwnDataset();
  createNewModel();
  newModelOrExisting();
  formSubmit();
});

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
      processData:false,
      success: function (res) {
        console.log(res);
      },
      error: function(err){
        console.log(err);
      }
    });
  });

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
    } else {}
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
    success: function (res) {}
  });
}