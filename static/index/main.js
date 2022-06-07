var num = 0;
var filename = num + ".jpg";
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
    deleteFile(no);

  });
});

async function SaveFile(file){
    let formData = new FormData();
    formData.append("file",file);
    await fetch('/uploader', {method: "POST", body: formData});
    alert("Files upload succesfuly");
}

async function deleteFile(no){
  let formData = new FormData();
  formData.append("file_no",no);
  await fetch('/remove', {method: "POST", body: formData});
  alert("Files deleted succesfuly");
}

function captureImage() {
  console.log("ilk aşama tamam");
  const imageUrl = "/capture_img";

  var picReader = new FileReader();
  picReader.onloadend = () => {
    const base64data = picReader.result;
    console.log(base64data);
  };

  (async () => {
    const response = await fetch(imageUrl);
    const imageBlob = await response.blob();
    filename = num + ".jpg";
    const myFile = new File([imageBlob], filename, {
      type: imageBlob.type,
  });
  
    picReader.readAsDataURL(imageBlob);
    SaveFile(myFile);
  })();

  var output = $(".preview-images-zone");
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

      output.append(html);
      num = num + 1;
    });
    $("#pro-image").val('');
 
}

function readImage() {
  if (window.File && window.FileList && window.FileReader) {
    var files = event.target.files; //FileList object
    
    var output = $(".preview-images-zone");

    for (let i = 0; i < files.length; i++) {
      var file = files[i];
      filename = num + ".jpg";
      var blob = file.slice(0, file.size, 'image/png'); 
      var newFile = new File([blob], filename, {type: 'image/png'});
      SaveFile(newFile);
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

        output.append(html);
        num = num + 1;
      });
      picReader.readAsDataURL(file);
    }

    $("#pro-image").val('');
  } else {
    console.log("Browser not support");
  }
}


