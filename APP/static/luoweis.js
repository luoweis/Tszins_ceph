/**
 * Created by luoweis on 2017/1/19.
 */
//获取url地址
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
        title: '输入管理员的EMAIL验证',  //标题
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
                        '邮箱验证失败',
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
                showCloseButton: true,
                html:hh}).then(function () {
                reload();
            })
        }
    })
}
function playOnPhone(url){
    var server = 'http://192.168.1.10:8080'
    swal('获取二维码','<div  style="width:200px;height: 200px;margin-left:180px;" id="showqrcode1"><canvas width="200" height="200"></canvas></div>','success')
            $("#showqrcode1").erweima({
                label: 'TszinS',
                text: server+url
            });
}

//检查表单上传的文件是否有效
function filenameCheck(obj){
    filename = obj.value;
    $.ajax({
        url:'/filenameCheck?file=' + filename,
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