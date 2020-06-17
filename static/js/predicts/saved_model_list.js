const appUrl = "http://localhost:8000"

let modelTable = null;
let datasetDetailTable = null;

$(document).ready(function () {
  formSubmit();
  dataTableInit();
  modelDelete();
  modelEdit();
  modelDetails();
});
/**
 * ===============================================
 * start of micro component init
 * ===============================================
 */

function dataTableInit() {
  modelTable = $('#js-model-table').DataTable();
}

/**
 * ===============================================
 * end of micro component init
 * ===============================================
 */
/**
 * ===============================================
 * start of direct action
 * ===============================================
 */

function modelDelete() {
  $('#js-model-table tbody').on('click', '#js-delete-model-button', function () {
    const id = $(this).data("id");

    Swal.fire({
      title: 'You Will Delete This Model',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
      if (result.value) {
        $.ajax({
          url: appUrl + `/api/v1/ml_model/${id}`,
          method: 'DELETE',
          success: (res) => {
            Swal.fire(
              'Deleted!',
              'Your model has been deleted.',
              'success'
            );
            $(this).closest("tr").remove();
          },
          error: (err) => {
            Swal.fire(
              "Ooops!",
              "There's Something Wrong!",
              "error"
            );
          }
        });
      }
    });
  });
}

function modelEdit() {
  $('#js-model-table tbody').on('click', '#js-edit-model-button', function () {
    const id = $(this).data("id");

    $.ajax({
      url: appUrl + `/api/v1/ml_model/${id}`,
      method: 'GET',
      success: function (res) {
        $("#edit-model-name").val(res.name);
        $("#js-edit-model-modal").modal("show");
      }
    });

    $("#js-edit-model-form").submit((e) => {
      e.preventDefault();
      let data = $("#js-edit-model-form").serialize();

      $.ajax({
        url: appUrl + `/api/v1/ml_model/${id}`,
        method: 'PUT',
        data: data,
        success: (res) => {
          let temp = modelTable.row($(this).parents('tr')).data();
          temp[1] = res.name

          modelTable
            .row($(this).parents('tr'))
            .data(temp)
            .invalidate();

          $("#js-edit-model-modal").modal("hide");

          Swal.fire(
            'Updated!',
            'Your model has been Updated.',
            'success'
          );
        },
        error: (err) => {
          Swal.fire(
            "Ooops!",
            "There's Something Wrong!",
            "error"
          );
        }
      });
    });
  });
}

function modelDetails() {
  $('#js-model-table tbody').on('click', '#js-detail-model-button', function () {
    const id = $(this).data("id");
    console.log(id);
    
    $.ajax({
      url: appUrl + `/api/v1/ml_model/${id}`,
      method: 'GET',
      async: false,
      success: (res) => {
        $("#js-model-name").text(res.name);
        $("#js-r2").text(res.accuracy_value);
        $("#js-rmse").text(res.error_value);
        $("#js-regularization").text(res.regularization);
        $("#js-epsilon").text(res.epsilon);
        $("#js-feature_num").text(res.feature_num);
        $("#js-detail-model-modal").modal("show");
      }
    });
  });
}

/**
 * ===============================================
 * end of direct action
 * ===============================================
 */
/**
 * ===============================================
 * 
 * 
 * 
 * start of model form submit process
 * 
 * 
 * 
 * ===============================================
 */
function formSubmit() {
}

function processAjaxResponse(res) {
}

function populateTable(resData) {
}
/**
 * ===============================================
 *
 *
 *
 * end of model form submit process
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
 * start of swal fires
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
