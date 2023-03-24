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
}

/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function openNav() {
    document.getElementById("sidenav").style.width = "250px";
    var main = document.getElementsByTagName("main")[0];
    main.style.marginLeft = "250px";
    document.getElementById("overlay").style.display = "block"
  }
  
  function closeNav() {
    document.getElementById("sidenav").style.width = "0";
    var main = document.getElementsByTagName("main")[0];
    main.style.marginLeft= "0";
    document.getElementById("overlay").style.display = "none"
  }