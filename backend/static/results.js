console.log("hello")
let is_ad_hoc = false;

window.onload = function pageLoad() {

  fetch("/get-recent")
    .then((response) => response.json())
    .then((data) => {
      data.forEach((row) => {
        let tempDiv = document.createElement("div");
        tempDiv.innerHTML = answerBoxTemplate(
          row.Title,
          row.Desc,
          row.Sim,
          row.Muscles,
          row.Equipment
        );
        document.getElementById("answer-box").appendChild(tempDiv);
      });
      updateProgressBars();
    });

  fetch("/get-recent-info").then((response => response.json()))
    .then((data) => {
      var $select2Container = $("#filter-text-val").next(".select2-container");
      var $adhocInput = $('#ad-hoc')
      if (data.was_AH) {
        $select2Container.hide();
        $adhocInput.show();
        is_ad_hoc = true;
        document.getElementById("ad-hoc").value = data.title;
        document.getElementById("search-method").checked = true;
      }
      else {
        $select2Container.show();
        $adhocInput.hide();
        is_ad_hoc = false;
        $('#filter-text-val').val(data.title).change();
      };

      document.querySelectorAll('.muscle-groups .filter-checkbox input[type="checkbox"]').forEach((checkbox) => {
        if ((data.muscle_groups).includes(checkbox.id)) {
          checkbox.checked = true;
        }
      });

      document.querySelectorAll('.equipment .filter-checkbox input[type="checkbox"]').forEach((checkbox) => {
        if ((data.equipments).includes(checkbox.id)) {
          checkbox.checked = true;
        }
      });
    });
};

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
  const filterDiv = button.parentElement.nextElementSibling
  if (filterDiv.style.display === "none") {
    filterDiv.style.display = "block";
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

function showMore(button) {
  var descDiv = button.previousElementSibling;
  if (descDiv.style.height === "155px") {
    descDiv.style.height = "auto";
    descDiv.style.overflow = "visible";
    button.textContent = ". . .";
  } else {
    descDiv.style.height = "155px";
    descDiv.style.overflow = "hidden";
    button.textContent = ". . .";
  }
}

function switchSearch() {
  const search_method = document.getElementById("search-method");
  const is_checked = search_method.getAttribute("checked");
}

// This function fetches the exercise titles and populates the dropdown
function fetchTitlesAndPopulateDropdown() {
  fetch("/get-titles")
    .then((response) => response.json())
    .then((data) => {
      const select = $("#filter-text-val");
      select.empty().append(new Option("", "", true, true));
      data.titles.forEach((title) => {
        select.append(new Option(title, title));
      });
    });
}

// This function is called when the dropdown selection changes
function dropdownChange() {
  const selectedTitle = document.getElementById("filter-text-val").value;
  console.log(selectedTitle);
  if (selectedTitle) {
    document.getElementById("filter-text-val").value = selectedTitle;
  }
}

document.addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    filterText()
  }
});

// Call the function to populate the dropdown when the page is loaded
document.addEventListener(
  "DOMContentLoaded",
  fetchTitlesAndPopulateDropdown
);

function answerBoxTemplate(title, titleDesc, sim, muscles, exercises) {
  const muscleElements = muscles.slice(0, 5).map(muscle => `<p>${muscle}</p>`).join('');
  const exerciseElements = exercises.map(exercise => `<p>${exercise}</p>`).join('');
  const similarity = sim * 100;
  return `
    <div class='answer-container'>
        <label class="episode-title">${title}</label>
        <div class='answer-box'>
            <div class="episode-container">
                <div class="description-container">
                    <div class="episode-desc" style="overflow:hidden; height:155px;">${titleDesc}</div>
                    <button id="more-button" onclick="showMore(this)">. . .</button>    
                </div>
                <img src= "../static/images/exercises/${title.replace(/ /g, "_")}.gif" alt="Image of ${title}">
            </div>
            <div class = "muscle-group">
                <div class="line"></div>
                ${muscleElements}
                <div class="line"></div>
            </div>
            <div class = "exercise-info">
                <div class = "similarity-info">
                    <p class='episode-sim'>Similarity Score</p>
                    <div class="progress">
                        <div class="progress-done" data-done="${similarity}">
                            ${Math.floor(similarity)}%
                        </div>
                    </div>
                </div>
                <div class = "equipment-info">
                    <p class='episode-sim'>Equipment</p>
                    <div class = "equipment-group">
                        ${exerciseElements}
                    </div>
                </div>
            </div>
        </div>
    </div>`;
}

function updateProgressBars() {
  const progressBars = document.querySelectorAll('.progress-done');
  console.log("hello");
  progressBars.forEach(element => {
    console.log(element.getAttribute('data-done'));
    element.style.width = element.getAttribute('data-done') + '%';
    element.style.opacity = 1;
  });
}

function sendFocus() {
  document.getElementById("filter-text-val").focus();
}

function filterText() {
  document.getElementById("answer-box").innerHTML = "";
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

  const response =
    !(is_ad_hoc)
      ? fetch(
        "/normal_search?" +
        new URLSearchParams({
          title: document.getElementById("filter-text-val").value,
          muscleFilter: selectedMuscleGroups,
          equipmentFilter: selectedEquipments,
        }).toString()
      )
      : fetch(
        "/AH_search?" +
        new URLSearchParams({
          title: document.getElementById("ad-hoc").value,
          muscleFilter: selectedMuscleGroups,
          equipmentFilter: selectedEquipments,
        }).toString()
      )

  response
    .then((response) => response.json())
    .then((data) => {
      data.forEach((row) => {
        let tempDiv = document.createElement("div");
        tempDiv.innerHTML = answerBoxTemplate(
          row.Title,
          row.Desc,
          row.Sim,
          row.Muscles,
          row.Equipment
        );
        document.getElementById("answer-box").appendChild(tempDiv);
      });
      updateProgressBars();
    });
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
