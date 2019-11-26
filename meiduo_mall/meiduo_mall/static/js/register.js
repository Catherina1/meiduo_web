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
        image_code:'',
        sms_code:'',

      //  v-show
        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code:false,

    },
    methods:{
        //blur光标触发的时候，会执行以下方法
        check_username(){
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if(re.test(this.username)){
                this.error_username = false;
            }else{
                this.error_username = true;
            }
        },
        check_password(){
            let re = /^[0-9A-Za-z]{8,20}$/;
            if(re.test(this.password)){
                this.error_password = false;
            }else{
                this.error_password = true;
            }
        },
        check_password2(){
            if(this.password2 != this.password){
                this.error_password2 = true;
            }else{
                this.error_password2 = false;
            }
        },
        check_mobile(){
            let re = /^1[3-9]\d{9}$/;
            if(re.test(this.mobile)){
                this.error_mobile = false;
            }else {
                this.error_mobile = true;
            }
        },
        check_allow(){
          if(!this.allow){
              alert(this.allow)
              this.error_allow = false;
          }else {
              this.allow
              this.error_allow = true;
          }
        },
        check_sms_code(){

        },
        check_image_code(){

        },
        on_submit(){
            check_username();
            check_password();
            check_password2();
            check_mobile();
            check_allow();
            //这块是为了检测有哪些报错的地方，如有不合适的地方则需要停止表单的提交
            if(this.error_username==true | this.error_mobile==true | this.error_password==true | this.error_password2==true | this.error_allow==true){
                window.event.returnValue = false;
            }
        },
    }
});