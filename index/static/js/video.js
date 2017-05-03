function PopupCenter(url, title, w, h) { 
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;
    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;
    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;
    var newWindow = window.open(url, title, 'menubar=no,status=no,titlebar=no,toolbar=no,scrollbars=no, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);
    if (window.focus) {
        newWindow.focus();
    }
}

function PopupCenterAudio(id,title) {
    var w = '300';
    var h = '35';
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;
    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;
    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;
    var newWindow = window.open('', title, 'menubar=no,status=no,titlebar=no,toolbar=no,scrollbars=no, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);
    newWindow.document.body.innerHTML = "<head><title>"+title+"</title></head><body><audio controls autoplay style=\"position: absolute; left: 0px; top: 0px; width: 300px;\"><source src=\""+id+"\"></audio></body>";
    if (window.focus) {
        newWindow.focus();
    }
}


$(document).ready(function(){
var active = 0;
  $('.play').click (function(e){
    var id = $(this).data('id');
    var type = $(this).data('type');
    var title = $(this).data('title');
    if(type=='video') {
        PopupCenter('https://drive.google.com/file/d/'+id+'/preview','Video Player','848','480');
    } 
    if(type=='audio') {
        PopupCenterAudio(id,title);
    }
        
    return false; 
  });
});

