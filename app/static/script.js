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
for (x = 0; x < timestamps.length; x++) {
  console.log("fff");
  var unixTimestamp = timestamps[x].textContent;
  var milliseconds = unixTimestamp * 1000;
  var dateObject = new Date(milliseconds);
  const options = { weekday: 'short', month: 'short', day: 'numeric', hour: "numeric", minute: "numeric" };
  timestamps[x].textContent = dateObject.toLocaleDateString('en-US', options);
};
