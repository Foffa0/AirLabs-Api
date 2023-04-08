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

/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function openNav() {
  document.getElementById("sidenav").style.width = "250px";
  document.getElementById("overlay").style.display = "block"
};
  
function closeNav() {
  document.getElementById("sidenav").style.width = "0";
  document.getElementById("overlay").style.display = "none"
};