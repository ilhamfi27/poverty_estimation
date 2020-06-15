const appUrl = "http://localhost:8000"

let datasetTable = null;
let datasetDetailTable = null;

$(document).ready(function () {
  formSubmit();
  dataTableInit();
  datasetDelete();
});
/**
 * ===============================================
 * start of micro component init
 * ===============================================
 */

function dataTableInit() {
  datasetTable = $('#js-dataset-table').DataTable();
  datasetDetailTable = $('#js-dataset-detail-table').DataTable();
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

function datasetDetail(id) {
  $.ajax({
    url: appUrl + `/api/v1/dataset/${id}`,
    method: 'GET',
    success: function (res) {
      console.log(res);
      datasetDetailTable.clear().draw();
      let number = 1;
      res.dataset_data.forEach(item => {
        datasetDetailTable.row.add([
          number,
          item.city,
          item.BPS_poverty_rate,
          item.sum_price_car,
          item.avg_price_car,
          item.std_price_car,
          item.sum_sold_car,
          item.avg_sold_car,
          item.std_sold_car,
          item.sum_viewer_car,
          item.avg_viewer_car,
          item.std_viewer_car,
          item.sum_buyer_car,
          item.avg_buyer_car,
          item.std_buyer_car,
          item.sum_price_motor,
          item.avg_price_motor,
          item.std_price_motor,
          item.sum_sold_motor,
          item.avg_sold_motor,
          item.std_sold_motor,
          item.sum_viewer_motor,
          item.avg_viewer_motor,
          item.std_viewer_motor,
          item.sum_buyer_motor,
          item.avg_buyer_motor,
          item.std_buyer_motor,
          item.sum_price_rumah_sell,
          item.avg_price_rumah_sell,
          item.std_price_rumah_sell,
          item.sum_sold_rumah_sell,
          item.avg_sold_rumah_sell,
          item.std_sold_rumah_sell,
          item.sum_viewer_rumah_sell,
          item.avg_viewer_rumah_sell,
          item.std_viewer_rumah_sell,
          item.sum_buyer_rumah_sell,
          item.avg_buyer_rumah_sell,
          item.std_buyer_rumah_sell,
          item.sum_price_rumah_rent,
          item.avg_price_rumah_rent,
          item.std_price_rumah_rent,
          item.sum_sold_rumah_rent,
          item.avg_sold_rumah_rent,
          item.std_sold_rumah_rent,
          item.sum_viewer_rumah_rent,
          item.avg_viewer_rumah_rent,
          item.std_viewer_rumah_rent,
          item.sum_buyer_rumah_rent,
          item.avg_buyer_rumah_rent,
          item.std_buyer_rumah_rent,
          item.sum_price_apt_sell,
          item.avg_price_apt_sell,
          item.std_price_apt_sell,
          item.sum_sold_apt_sell,
          item.avg_sold_apt_sell,
          item.std_sold_apt_sell,
          item.sum_viewer_apt_sell,
          item.avg_viewer_apt_sell,
          item.std_viewer_apt_sell,
          item.sum_buyer_apt_sell,
          item.avg_buyer_apt_sell,
          item.std_buyer_apt_sell,
          item.sum_price_apt_rent,
          item.avg_price_apt_rent,
          item.std_price_apt_rent,
          item.sum_sold_apt_rent,
          item.avg_sold_apt_rent,
          item.std_sold_apt_rent,
          item.sum_viewer_apt_rent,
          item.avg_viewer_apt_rent,
          item.std_viewer_apt_rent,
          item.sum_buyer_apt_rent,
          item.avg_buyer_apt_rent,
          item.std_buyer_apt_rent,
          item.sum_price_land_sell,
          item.avg_price_land_sell,
          item.std_price_land_sell,
          item.sum_sold_land_sell,
          item.avg_sold_land_sell,
          item.std_sold_land_sell,
          item.sum_viewer_land_sell,
          item.avg_viewer_land_sell,
          item.std_viewer_land_sell,
          item.sum_buyer_land_sell,
          item.avg_buyer_land_sell,
          item.std_buyer_land_sell,
          item.sum_price_land_rent,
          item.avg_price_land_rent,
          item.std_price_land_rent,
          item.sum_sold_land_rent,
          item.avg_sold_land_rent,
          item.std_sold_land_rent,
          item.sum_viewer_land_rent,
          item.avg_viewer_land_rent,
          item.std_viewer_land_rent,
          item.sum_buyer_land_rent,
          item.avg_buyer_land_rent,
          item.std_buyer_land_rent,
        ]).draw();
        number++;
      });
      $('#js-dataset-detail-modal').modal('show');
    },
    error: function (e) {
      console.log(e);
    }
  })
}

function datasetDelete() {
  $('#js-dataset-table tbody').on('click', '#js-delete-dataset-button', function () {
    const id = $(this).data("id");

    Swal.fire({
      title: 'You Will Delete This Dataset',
      text: "You won't be able to revert this!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
      if (result.value) {
        $.ajax({
          url: appUrl + `/api/v1/dataset/${id}`,
          method: 'DELETE',
          success: (res) => {
            Swal.fire(
              'Deleted!',
              'Your file has been deleted.',
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
 * start of dataset form submit process
 * 
 * 
 * 
 * ===============================================
 */
function formSubmit() {
  $("#js-new-dataset-form").submit(function (e) {
    e.preventDefault();
    $.ajax({
      url: `${appUrl}/api/v1/dataset_profile/`,
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
        if (err.status != 500) {
          showErrorModal(err.responseJSON.message);
        }
      }
    });
  });
}

function processAjaxResponse(res) {
  $('#js-new-dataset-form').each(function () {
    this.reset();
  });
  $('#js-add-dataset-modal').modal('hide');

  populateTable(res);

  Swal.fire(
    "Saved!",
    "Dataset Has Been Saved",
    "success"
  );
}

function populateTable(resData) {
  let lastData = datasetTable.row(':last').data();
  let number = lastData == undefined ? 1 : parseInt(lastData[0]) + 1
  datasetTable.row.add([
    number,
    resData.name,
    resData.valid_date,
    `<button type="button" class="btn btn-primary" id="js-show-dataset-button" data-toggle="modal"
    data-target="#js-dataset-detail-modal" data-id="${resData.id}"><i class="fas fa-eye"></i></button>
    <button type="button" class="btn btn-danger" id="js-delete-dataset-button" data-toggle="modal"
    data-target="#js-dataset-delete-modal" data-id="${resData.id}"><i class="fas fa-trash"></i></button>`
  ]).draw();
  var row = datasetTable.row(':last');
  row.attr("data-id", resData.id);
  row.attr("id", "js-dataset-row");
}
/**
 * ===============================================
 *
 *
 *
 * end of dataset form submit process
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
