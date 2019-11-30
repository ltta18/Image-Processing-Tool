var img = new Image();
var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');
var fileName = '';
 
$("#inputGroupFile01").on("change", function(){
    var file = document.querySelector('#inputGroupFile01').files[0];
    var reader = new FileReader();
    if (file) {
        fileName = file.name;
        reader.readAsDataURL(file);
    }
    reader.addEventListener("load", function () {
        img = new Image();
        img.src = reader.result;
        img.onload = function () {
            canvas.width = img.width;
            canvas.height = img.height;
            canvas.src = img
            ctx.drawImage(img, 0, 0, img.width, img.height);
            $("#canvas").removeAttr("data-caman-id");
        }
    }, false);
});

$('#download-btn').on('click', function (e) {
    var fileExtension = fileName.slice(-4);
    if (fileExtension == '.jpg' || fileExtension == '.png') {
        var actualName = fileName.substring(0, fileName.length - 4);
    }
    download(canvas,"filter_" +actualName);
});

function download(canvas, filename) {
    var  e;
    var lnk = document.createElement('a');
     
    lnk.download = filename;
    lnk.href = canvas.toDataURL("image/jpeg", 0.8);
     
    if (document.createEvent) {
        e = document.createEvent("MouseEvents");
        e.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
        lnk.dispatchEvent(e);
    }
    else if (lnk.fireEvent) {
        lnk.fireEvent("onclick");
    }
}

// Import image
var inputGroupFile01 = document.getElementById('inputGroupFile01');
var URL = window.URL || window.webkitURL;
var uploadedImageType;
var uploadedImageName;
if (URL) {
  inputGroupFile01.onchange = function () {
    var files = this.files;
    var file;

    if (files && files.length) {
      file = files[0];

      if (/^image\/\w+/.test(file.type)) {
        uploadedImageType = file.type;
        uploadedImageName = file.name;

        if (uploadedImageURL) {
          URL.revokeObjectURL(uploadedImageURL);
        }
        image.src = uploadedImageURL = URL.createObjectURL(file);
            
      } else {
        window.alert('Please choose an image file.');
      }
    }
  };
} else {
  inputGroupFile01.disabled = true;
  inputGroupFile01.parentNode.className += ' disabled';
}