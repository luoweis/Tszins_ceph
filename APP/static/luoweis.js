/**
 * Created by luoweis on 2017/1/19.
 */
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
                setTimeout('reload()',5000);
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
                'Your imaginary file is safe :)',
                'error'
            )
        }
    })
}
function deleteKey(deleteUrl){
    swal({
        title: '输入管理员的EMAIL验证',  //标题
        input: 'email',                             //封装的email类型  列如qq@qq.com
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