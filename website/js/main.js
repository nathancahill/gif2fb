document.getElementById('gif').addEventListener('change', function(e) {
    mixpanel.track("Uploaded file");

    var file = this.files[0];
    var xhr = new XMLHttpRequest();
    xhr.file = file;

    xhr.addEventListener('progress', function(e) {
        var done = e.position || e.loaded, total = e.totalSize || e.total;
        console.log('xhr progress: ' + (Math.floor(done/total*1000)/10) + '%');
    }, false);

    if (xhr.upload) {
        xhr.upload.onprogress = function(e) {
            var done = e.position || e.loaded, total = e.totalSize || e.total;
            console.log('xhr.upload progress: ' + done + ' / ' + total + ' = ' + (Math.floor(done/total*1000)/10) + '%');
        };
    }

    xhr.onreadystatechange = function(e) {
        if (4 == this.readyState) {
            var id = xhr.responseText;

            $('.form-gif').hide();
            $('#display').attr('src', '/uploads/' + id).show();
            $('#generating').show();

            var c = 1;

            var g = setInterval(function() {
                c += 1;

                $('#generating').text('Generating video' + Array(c).join("."));

                if (c > 3) {
                    c = 0;
                }
            }, 300);

            var h = setInterval(function() {
                $.ajax({
                    'url': '/app/done',
                    'type': 'POST',
                    'data': {
                        'id': id
                    }
                }).done(function(data) {
                    if (data == 'done') {
                        mixpanel.track("Finished upload");

                        clearInterval(h);
                        clearInterval(g);

                        window.video_id = id;

                        $('#generating').text('Done! ');
                        $('<a href="#" />').text('Post to Facebook').appendTo('#generating').click(function() {
                            FB.login(function(){}, {scope: 'video_upload'});
                            return false;
                        });
                    } else if (data == 'error') {
                        mixpanel.track("Upload error");

                        clearInterval(h);
                        clearInterval(g);

                        $('#generating').text('Error!');
                    }
                });
            }, 1000);
        }
    };

    xhr.open('post', '/app/upload', true);
    xhr.send(file);
}, false);
