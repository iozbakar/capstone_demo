var selDiv = "";
var storedFiles = []; //store the object of the all files
var num = 4;


document.addEventListener("DOMContentLoaded", init, false); 

function init() {
   //To add the change listener on over file element
   document.querySelector('#pro-image').addEventListener('change', handleFileSelect, false);
   //allocate division where you want to print file name
   selDiv = document.querySelector("#filelist"); //sonra değiştirilicek
}

//function to handle the file select listenere
function handleFileSelect(e) {
   //to check that even single file is selected or not
   if(!e.target.files) return;      

   //for clear the value of the selDiv
   selDiv.innerHTML = "";

   //get the array of file object in files variable
   var picFile = e.target;
   var files = e.target.files;
   var filesArr = Array.prototype.slice.call(files);

   //print if any file is selected previosly 
   for(var i=0;i<storedFiles.length;i++)
   {
       selDiv.innerHTML += '<div class="preview-image preview-show-' +
       num +
       '">' +
       '<div class="image-cancel" data-no="' +
       num +
       '">x</div>' +
       '<div class="image-zone"><img id="pro-img-' +
       num +
       '" src="' +
       picFile.result +
       '"></div>' +
       '<div class="tools-edit-image"><a href="javascript:void(0)" data-no="' +
       num +
       '" class="btn btn-light btn-edit-image">delete</a></div>' +
       "</div>";
   }
   filesArr.forEach(function(f) {
       //add new selected files into the array list
       storedFiles.push(f);
       //print new selected files into the given division
       selDiv.innerHTML += '<div class="preview-image preview-show-' +
       num +
       '">' +
       '<div class="image-cancel" data-no="' +
       num +
       '">x</div>' +
       '<div class="image-zone"><img id="pro-img-' +
       num +
       '" src="' +
       f.name +
       '"></div>' +
       '<div class="tools-edit-image"><a href="javascript:void(0)" data-no="' +
       num +
       '" class="btn btn-light btn-edit-image">delete</a></div>' +
       "</div>";

       num = num + 1;
   });

   //store the array of file in our element this is send to other page by form submit
   $("#pro-image").val(storedFiles);
}