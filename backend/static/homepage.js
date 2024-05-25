let is_ad_hoc = false;

function redirect() {
  document.getElementById("answer-box").innerHTML = "";
  console.log(document.getElementById("filter-text-val").value);
  const selectedMuscleGroups = [];
  const muscleGroupCheckboxes = document.querySelectorAll('.muscle-groups input[type="checkbox"]');
  muscleGroupCheckboxes.forEach(function (checkbox) {
    if (checkbox.checked) {
      selectedMuscleGroups.push(checkbox.id);
    }
  });

  const selectedEquipments = [];
  const equipmentCheckboxes = document.querySelectorAll('.equipment input[type="checkbox"]');
  equipmentCheckboxes.forEach(function (checkbox) {
    if (checkbox.checked) {
      selectedEquipments.push(checkbox.id);
    }
  });

  const title = (is_ad_hoc)
    ? document.getElementById("ad-hoc").value
    : document.getElementById("filter-text-val").value

  const route = is_ad_hoc ? "/create-recent-AH?" : '/create-recent-normal?';
  fetch(route + new URLSearchParams({
    title: title,
    muscleFilter: selectedMuscleGroups,
    equipmentFilter: selectedEquipments,
  }).toString())
    .then(response => response.json())
    .then(data => {
      window.location.href = '/results/';
    });
}

// Initialize Select2 on the filter-text-val element
$('#filter-text-val').select2({
  placeholder: "Select an Exercise",
});

$(document).ready(function () {
  $("#filter-text-val").select2({
    placeholder: "Select an Exercise",
  });

  $('#ad-hoc').hide();

  $("#search-method").change(function () {
    var $select2Container = $("#filter-text-val").next(".select2-container");
    var $adhocInput = $('#ad-hoc')
    if (this.checked) {
      $select2Container.hide();
      $adhocInput.show();
      is_ad_hoc = true;
    } else {
      $select2Container.show();
      $adhocInput.hide();
      is_ad_hoc = false;
    }
  });
});

function toggleFilter(button) {
  const filterDiv = button.parentElement.nextElementSibling;
  if (filterDiv.style.display === "none") {
    filterDiv.style.display = "flex";
  } else {
    filterDiv.style.display = "none";
  }
}

document.getElementById('toggle-muscle-groups').addEventListener('click', function () {
  this.classList.toggle('rotated');
});

document.getElementById('toggle-equipment').addEventListener('click', function () {
  this.classList.toggle('rotated');
});

function switchSearch() {
  const search_method = document.getElementById("search-method");
  const is_checked = search_method.getAttribute("checked");
}

// This function fetches the exercise titles and populates the dropdown
function fetchTitlesAndPopulateDropdown() {
  fetch("/get-titles")
    .then(response => response.json())
    .then(data => {
      const select = $('#filter-text-val');
      select.empty().append(new Option("", "", true, true)); // Empty option for placeholder
      data.titles.forEach(title => {
        select.append(new Option(title, title));
      });
    });
}

// This function is called when the dropdown selection changes
function dropdownChange() {
  const selectedTitle = document.getElementById("filter-text-val").value;
  console.log(selectedTitle);
  if (selectedTitle) {
    // Here you can call the same function you use to fetch and display the exercise info
    // For example, if you're using the text input's filter function:
    document.getElementById("filter-text-val").value = selectedTitle; // Update the text input to reflect the dropdown selection
  }
}

document.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    redirect()
  }
});

// Call the function to populate the dropdown when the page is loaded
document.addEventListener("DOMContentLoaded", fetchTitlesAndPopulateDropdown);

function sendFocus() {
  document.getElementById('filter-text-val').focus()
}

document.addEventListener('DOMContentLoaded', function () {
  const allCheckboxes = document.querySelectorAll('.filter-checkbox input[type="checkbox"]');
  allCheckboxes.forEach(function (checkbox) {
    checkbox.addEventListener('change', function () {
      filterText();
    });
  });
});

document.addEventListener('DOMContentLoaded', function () {
  function setupCheckboxGroup(checkboxesSelector, headerSelector) {
    var checkboxes = document.querySelectorAll(checkboxesSelector);
    var filterHeader = document.querySelector(headerSelector);

    function updateHeaderStyle() {
      var anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
      filterHeader.style.textDecoration = anyChecked ? 'underline' : 'none';
    }

    checkboxes.forEach(checkbox => {
      checkbox.addEventListener('change', updateHeaderStyle);
    });

    updateHeaderStyle();
  }

  setupCheckboxGroup('.muscle-groups .filter-checkbox input[type="checkbox"]', '.filter-header:has(#toggle-muscle-groups)');
  setupCheckboxGroup('.equipment .filter-checkbox input[type="checkbox"]', '.filter-header:has(#toggle-equipment)');
});