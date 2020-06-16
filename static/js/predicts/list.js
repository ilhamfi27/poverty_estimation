const appUrl = "http://localhost:8000"

let predictionTable = null;
let datasetDetailTable = null;

let mymap = null;
let info = null;
let legend = null;
let geojson = null;

$(document).ready(function () {
  dataTableInit();
  predictionDelete();
  predictionEdit();
  predictionDetails();
});
/**
 * ===============================================
 * start of micro component init
 * ===============================================
 */

function dataTableInit() {
  predictionTable = $('#js-prediction-table').DataTable();
  predictionTableDetail = $('#js-prediction-detail').DataTable();
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

function predictionDelete() {
  $('#js-prediction-table tbody').on('click', '#js-delete-prediction-button', function () {
    const id = $(this).data("id");
    console.log(id);
    

    Swal.fire({
      title: 'You Will Delete This Prediction History',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
      if (result.value) {
        $.ajax({
          url: appUrl + `/api/v1/prediction/${id}`,
          method: 'DELETE',
          success: (res) => {
            Swal.fire(
              'Deleted!',
              'Your prediction has been deleted.',
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

function predictionEdit() {
  $('#js-prediction-table tbody').on('click', '#js-edit-prediction-button', function () {
    const id = $(this).data("id");

    $.ajax({
      url: appUrl + `/api/v1/prediction/${id}`,
      method: 'GET',
      success: function (res) {
        $("#edit-prediction-name").val(res.name);
        $("#js-edit-prediction-modal").modal("show");
      }
    });

    $("#js-edit-prediction-form").submit((e) => {
      e.preventDefault();
      let data = $("#js-edit-prediction-form").serialize();

      $.ajax({
        url: appUrl + `/api/v1/prediction/${id}`,
        method: 'PUT',
        data: data,
        success: (res) => {
          let temp = predictionTable.row($(this).parents('tr')).data();
          temp[1] = res.name

          predictionTable
            .row($(this).parents('tr'))
            .data(temp)
            .invalidate();

          $("#js-edit-prediction-modal").modal("hide");

          Swal.fire(
            'Updated!',
            'Your prediction has been Updated.',
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

function predictionDetails() {
  $('#js-prediction-table tbody').on('click', '#js-detail-prediction-button', function () {
    const id = $(this).data("id");
    
    $.ajax({
      url: appUrl + `/api/v1/prediction_result/${id}`,
      method: 'GET',
      async: false,
      success: (res) => {
        populateTable(res);
        $("#js-detail-prediction-modal").modal("show");
      }
    });
  });
}

function populateTable(data) {  
  predictionTableDetail.clear().draw();
  let number = 1;
  data.forEach(item => {
    predictionTableDetail.row.add([
      number,
      item.city,
      item.province,
      item.result.toFixed(3) + " %",
    ]).draw();
    number++;
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
