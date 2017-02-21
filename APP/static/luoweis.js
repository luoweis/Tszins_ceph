/**
 * Created by luoweis on 2017/1/19.
 */
//获取url地址
var web_server = 'http://192.168.1.10:8080';
function geturl(url) {
    $.ajax({
        url:url,
        type:'GET',
        success:function (res) {
            swal('获取到的URL地址','<div class="scroll-x" style="width:550px;height: 100px;">'+res+'</div>','success')
        },
        error:function(){
            alert('error');
        }
    })
}
//获取二维码
function getqrcode(url){
    $.ajax({
        url:url,
        type: 'GET',
        success:function (res) {
            swal('获取二维码','<div  style="width:200px;height: 200px;margin-left:180px;" id="showqrcode"><canvas width="200" height="200"></canvas></div>','success')
            $("#showqrcode").erweima({
                label: 'TszinS',
                text: res
            });
        },
        error:function () {
            alert('error');
        }
    });
}

function doDeleteKey(deleteUrl) {
    swal({
        title: '删除',
        text: "你确定删除么?",
        type: 'warning',   //感叹号图标
        showCancelButton: true,   //显示取消按钮
        confirmButtonColor: '#3085d6', //俩个按钮的颜色
        cancelButtonColor: '#d33',
        confirmButtonText: '确定', //俩个按钮的文本
        cancelButtonText: '取消',
        confirmButtonClass: 'btn btn-success',  //俩个按钮的类样式
        cancelButtonClass: 'btn btn-danger',
        timer:10000

    }).then(function() {//大部分，then是通用的回调函数
        //执行删除的url
        $.ajax({
            url:deleteUrl,
            type:'GET',
            success:function (res) {
                swal({
                        type: 'success',
                        title: '成功删除',
                        text: res + '已经被存储集群中删除'
                    }
                );
                setTimeout('reload()',2000);
            },
            error:function () {
                alert('error');
            }
        })
    }, function(dismiss) {
        // dismiss can be 'cancel', 'overlay',
        // 'close', and 'timer'
        if (dismiss === 'cancel') {
            swal(
                '取消',
                '文件未被删除 :)',
                'error'
            )
        }
    })
}
function deleteKey(deleteUrl){
    swal({
        title: '输入口令进行验证',  //标题
        input: 'password',                             //封装的email类型  列如qq@qq.com
        showCancelButton: true,
        confirmButtonText: 'Submit',
        showLoaderOnConfirm: true,
        allowOutsideClick: false
    }).then(function(email) {
        $.ajax({
            url:'/confirmEmail?email=' + email,
            type:'GET',
            success:function (res) {
                if (res == 'ok'){
                    doDeleteKey(deleteUrl);
                }else{
                    swal(
                        'Cancelled',
                        '口令验证失败',
                        'error'
                    )
                }
            }
        })
    })
}


function reload() {
    window.location.reload();
}

function playOnWeb(bucket,name,acl){
    $.ajax({
        url:'/play/'+bucket+'?key='+name+'&acl='+acl,
        type:'GET',
        success:function(url){
            var hh='<video id=""  controls preload="none" width="640" height="264" poster="../static/plugin/play/Tszins.png" data-setup="{}"><source src="'+url +'" type="video/mp4" /></video>'
            swal({
                allowOutsideClick: false,
                confirmButtonText:'关闭',
                title:'播放文件',
                width:'800',
                html:hh}).then(function () {
                reload();
            })
        }
    })
}
function playOnPhone(url){

    swal('获取二维码','<div  style="width:200px;height: 200px;margin-left:180px;" id="showqrcode1"><canvas width="200" height="200"></canvas></div>','success')
    res = $("#showqrcode1").erweima({
        label: 'TszinS',
        text: web_server+url
    });
}

//发送邮件
function sendEmail(url) {
    $("#getcanvastomail").erweima({
        label: 'TszinS',
        text: web_server+url
    });
    var mycanvas = document.getElementById('canvascontent');
    //将canvas转化成图片
    var image = mycanvas.toDataURL("image/png");
    var html = "<html><head><style type='text/css'>body{text-align:center}</style><body><div id='tszins'><img src='"+image+"' alt='from tszins' /></div></head></body></html>";
    swal({
        title: '输入对方邮箱',  //标题
        input: 'email',        //封装的email类型  列如qq@qq.com
        showCancelButton: true,
        confirmButtonText: 'Submit',
        showLoaderOnConfirm: true,
        allowOutsideClick: false
    }).then(function(email) {
        $.ajax({
            url:'/sendEmail',
            type:'post',
            data: JSON.stringify({who:email,html:html}),
            contentType:'application/json',
            beforeSend:function (XMLHttpRequest) {
                swal({
                    title:'正在发送邮件',
                    imageUrl: '/static/images/loading.gif'
                })
            },
            success:function (res) {
                if (res == 'ok'){
                    swal(
                        '成功',
                        '发送'+email+'邮件成功',
                        'success'
                    )
                }
            },
            error:function () {
                swal(
                    '失败',
                    '发送'+email+'邮件失败',
                    'error'
                    )
            }
        })
    })
}
//检查表单上传的文件是否有效
function filenameCheck(obj){
    filename = obj.value;
    bucket = document.getElementById('keyName').getAttribute('mybucket');
    $.ajax({
        url:'/filenameCheck/'+bucket+'?file=' + filename,
        type:'GET',
        success:function (res) {
            if(res=='ok') {
                swal({
                    title: '文件已经存在',
                    showCancelButton: false,
                    confirmButtonText: '返回',
                    showLoaderOnConfirm: true,
                    allowOutsideClick: false
                });
                obj.value='';
            }

        }
    })
}

//增加bucket
function addBucket(){
    swal({
        title: '输入口令进行验证',  //标题
        input: 'password',                             //封装的email类型  列如qq@qq.com
        showCancelButton: true,
        confirmButtonText: 'Submit',
        showLoaderOnConfirm: true,
        allowOutsideClick: false
    }).then(function(email) {
        $.ajax({
            url:'/confirmEmail?email=' + email,
            type:'GET',
            success:function (res) {
                if (res == 'ok'){
                    swal({
                        title: '输入Bucket名字',  //标题
                        input: 'text',
                        showCancelButton: true,
                        confirmButtonText: 'Submit',
                        showLoaderOnConfirm: true,
                        allowOutsideClick: false
                    }).then(function (bucket) {
                        $.ajax({
                            url:'/addBucket?bucket=' + bucket,
                            type:'GET',
                            success:function(){
                                swal(
                                    '成功',
                                    '创建Bucket'+bucket+'成功',
                                    'success'
                                );
                                reload();
                            }
                        })
                    })
                }else{
                    swal(
                        'Cancelled',
                        '口令验证失败',
                        'error'
                    )
                }
            }
        })
    })
}
//删除bucket
function delBucket(Bucket){
    swal({
        title: '输入口令进行验证',  //标题
        input: 'password',                             //封装的email类型  列如qq@qq.com
        showCancelButton: true,
        confirmButtonText: 'Submit',
        showLoaderOnConfirm: true,
        allowOutsideClick: false
    }).then(function(email) {
        $.ajax({
            url:'/confirmEmail?email=' + email,
            type:'GET',
            success:function (res) {
                if (res == 'ok'){
                    $.ajax({
                        url:'/delBucket?bucket=' + Bucket,
                        type:'GET',
                        success:function () {
                            swal(
                                '成功',
                                '删除Bucket'+Bucket+'成功',
                                'success'
                            );
                            reload();
                        }
                    })
                }else{
                    swal(
                        'Cancelled',
                        '口令验证失败',
                        'error'
                    )
                }
            }
        })
    })
}
//upload submit
//异步提交方法
function uploadSubmit(bucket){
    var form = new FormData(document.getElementById("uploadForm"));//type object
    //var tag = form.get('tag');//获取表达中的name值
    //alert(tag);
    //for(x in form){
    //    alert(x);
    //}
    var fileName = form.get('file').name;//获取到form表单中file的文件名称
    var file = document.getElementById("keyName").files[0];
    if (file) {
          var fileSize = 0;
          if (file.size > 1024 * 1024)
            fileSize = (Math.round(file.size * 100 / (1024 * 1024)) / 100).toString() + 'MB';
          else
            fileSize = (Math.round(file.size * 100 / 1024) / 100).toString() + 'KB';
        }
    $.ajax({
        url:'/keyUpload/' + bucket,
        type: 'POST',
        data: form,
        processData:false,
        contentType:false,
        beforeSend:function () {
            swal({
                title: "开始上传",
                html: "<p>文件:"+fileName+"</p>"+"<p>大小:"+fileSize+"</p>",
                allowOutsideClick: false,
                showConfirmButton: false,
                showCancelButton: true,
                cancelButtonText: '取消',
                imageUrl: '/static/images/loading.gif'
            })
        },
        success:function (res) {
            if (res == 'ok'){
                swal({
                        title: '成功',
                        text: "上传"+fileName+"成功！",
                        type: 'success',
                        timer:2000
                    }
                );
                reload();
            }
        },
        error:function () {
            swal(
                '失败',
                '上传'+fileName+'失败',
                'error'
            )
        }
    })
}