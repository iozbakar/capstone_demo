var selDiv = "";
var storedFiles = [];
var num = 4;

$(document).ready(function () {
  document
    .getElementById("pro-image")
    .addEventListener("change", readImage, false);

  document
    .getElementById("capture-image")
    .addEventListener("click", captureImage);
  
  $(".preview-images-zone").sortable();

  $(document).on("click", ".image-cancel", function () {
    let no = $(this).data("no");
    $(".preview-image.preview-show-" + no).remove();
  });
});


function readImage() {
    if (window.File && window.FileList && window.FileReader) {
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
       storedFiles[i] +
       '"></div>' +
       '<div class="tools-edit-image"><a href="javascript:void(0)" data-no="' +
       num +
       '" class="btn btn-light btn-edit-image">delete</a></div>' +
       "</div>";
   }

    
      var files = event.target.files; //FileList object
      var output = $(".preview-images-zone");
  
      for (let i = 0; i < files.length; i++) {
        var file = files[i];
        if (!file.type.match("image")) continue;
  
        var picReader = new FileReader();
  
        picReader.addEventListener("load", function (event) {
          var picFile = event.target;
          var html =
            '<div class="preview-image preview-show-' +
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
  
          storedFiles.push(picFile.result)  
          output.append(html);
          num = num + 1;
        });
        

        picReader.readAsDataURL(file);

       // $("#pro-image").val.append(img)
        //$("#pro-image").val('pro-image[]');
       // $("#pro-image").val(storedFiles);
      }
      $("#pro-image").val(storedFiles);
      console.log(storedFiles);
    } else {
      console.log("Browser not support");
    }
  }
  




