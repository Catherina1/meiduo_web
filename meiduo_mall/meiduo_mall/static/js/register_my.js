let vm = new Vue({
    el: '#app',
    //修改Vue读取变量的写法，默认是{{}} 不能与django的jinja2模板语言起冲突
    delimiters:['[[',']]'],
    //data与前端的v-model双向数据传输
    data:{
      //  v-model
        username:'',
        password:'',
        password2:'',
        mobile:'',
        allow:'',

      //  v-show
        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code:false,

    },
    method:{
        check_username(){

        },
        check_password(){

        },
        check_password2(){

        },
        check_mobile(){

        },
        check_sms_code(){

        },
        on_submit(){

        },
    }
});