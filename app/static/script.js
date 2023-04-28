var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.maxHeight){
        content.style.maxHeight = null;
        } else {
        content.style.maxHeight = content.scrollHeight + "px";
        } 
    });
};

/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function openNav() {
  document.getElementById("sidenav").style.width = "250px";
  document.getElementById("overlay").style.display = "block"
};
  
function closeNav() {
  document.getElementById("sidenav").style.width = "0";
  document.getElementById("overlay").style.display = "none"
};

function editAccount() {
  var x = document.getElementsByClassName("account-info-edit");
  for (var i = 0; i < x.length; i++) {
    x[i].classList.toggle("invisible");
  };
    
  var y = document.getElementsByClassName("account-info");
  for (var z = 0; z < y.length; z++) {
    y[z].classList.toggle("invisible");
  }
  document.getElementById("change-btn").classList.toggle("invisible");
  document.getElementById("cancel-btn").classList.toggle("invisible");
  document.getElementById("account-submit-btn").classList.toggle("invisible");
};

function editPassword() {
  var x = document.getElementsByClassName("account-info-edit-pw");
  for (var i = 0; i < x.length; i++) {
    x[i].classList.toggle("invisible");
  };
    
  var y = document.getElementsByClassName("account-info-pw");
  for (var z = 0; z < y.length; z++) {
    y[z].classList.toggle("invisible");
  }
  document.getElementById("change-btn-pw").classList.toggle("invisible");
  document.getElementById("cancel-btn-pw").classList.toggle("invisible");
  document.getElementById("account-submit-btn-pw").classList.toggle("invisible");
};


var timestamps = document.getElementsByClassName("timestamp");
var x;
const today = new Date();

for (x = 0; x < timestamps.length; x++) {
  var unixTimestamp = timestamps[x].textContent;
  var milliseconds = unixTimestamp * 1000;
  var dateObject = new Date(milliseconds);

  if (dateObject.getDate() == today.getDate()) {
    timestamps[x].textContent = "Today, " + dateObject.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'});
  } else if (dateObject.getDate() == (today.getDate() + 1)) {
    timestamps[x].textContent = "Tomorrow, " + dateObject.toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit'});
  } else {
    const options = { weekday: 'short', month: 'short', day: 'numeric', hour: "numeric", minute: "numeric" };
    timestamps[x].textContent = dateObject.toLocaleDateString('en-GB', options);
  }
};

var modal = document.getElementById("delete-modal");

// Get the button that opens the modal
var btn = document.getElementById("account-delete-btn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close-modal");

if (btn) {
  btn.onclick = function() {
    modal.style.display = "block";
  };
}

for (let index = 0; index < span.length; index++) {
  span[index].onclick = function() {
    modal.style.display = "none";
  }
};

window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// try {
//   var aircraftSearch = document.getElementById("aircraft-search");
//   var radios = document.forms["aircraft_form"].elements["search_option"];

//   for(var i = 0; i < radios.length; i++) {
//     radios[i].onclick = function() {
//       if (this.value == 1) {
//         aircraftSearch.type = 'text'
//       } else {
//         aircraftSearch.type = 'number'
//       }
//     }
//   };
// }
// catch {}

async function addAircraft(btn, aircraft, airport) {
  var loading = document.getElementsByClassName("loading");
  var loadBtn = document.getElementsByClassName("reload-btn");
  for (let index = 0; index < loading.length; index++) {
    loading[index].style.display = "block";
  }
  await fetch("/save-aircraft/" + aircraft + "/" + airport, {
    method: "POST",
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then(response => {
    if (response.status === 200) {
      btn.style.backgroundColor = "rgb(0, 202, 34)";
      btn.innerHTML = "Added <i class='fa fa-solid fa-check'></i>";
      btn.onclick = null;
      for (let index = 0; index < loadBtn.length; index++) {
        loadBtn[index].style.display = "block";
        
      }
    }
    for (let index = 0; index < loading.length; index++) {
      loading[index].style.display = "none";
    }
  })
  .catch(error => {
    for (let index = 0; index < loading.length; index++) {
      loading[index].style.display = "none";
    }
  });
}

if(window.location.hash) {
  var airport = document.getElementById(window.location.hash.toString().replace("#", ""));
  var coll = airport.getElementsByClassName("collapsible")[0];

  if (!coll.classList.contains("active")) {
    coll.classList.toggle("active"); 
  }
  var content = coll.nextElementSibling;
  if (!content.style.maxHeight){
    content.style.maxHeight = content.scrollHeight + "px"
  }
};


function changeSearchType(selectInput) {
  var searchInput = selectInput.nextElementSibling;
  if (selectInput.value == 1) {
    searchInput.style.display = "block";
    searchInput.type = 'text';
    searchInput.placeholder = "Search Aircraft (e.g. 'A320', 'Boeing')"
  } else if (selectInput.value == 2) {
    searchInput.style.display = "block";
    searchInput.type = 'number';
    searchInput.placeholder = "Search by engine count"
    searchInput.min = '0';
    searchInput.max = '12';
  }
}

var aircraftForms = document.getElementsByClassName("aircraft-search-form");
for (var i=0; i<aircraftForms.length; i++) {
  var pills = aircraftForms[i].querySelectorAll('input[name=filter]');
  for (var x=0; x<pills.length; x++) {
    pills[x].formId = "aircraft-search-form-" + (i+1).toString();
    pills[x].addEventListener('click', submitForm, false);
  }
};

function submitForm(evt) {
  document.getElementById((evt.currentTarget.formId).toString()).submit();
}