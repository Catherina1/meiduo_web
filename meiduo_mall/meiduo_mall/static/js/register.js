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
        uuid:'',
        image_code_url: '',
        send_flag: false, // 用来判断频繁发送短信

      //  v-show
        error_username: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code:false,


      // vue变量[[]]使用
        error_username_message:'',
        error_mobile_message:'',
        error_image_code_message:'',
        error_sms_code_message:'',

    },
    mounted(){
        this.image_generate();
    },
    methods:{
        image_generate(){
           this.uuid = generateUUID();
           this.image_code_url = "/image_codes/" + this.uuid + "/";
        },
        send_sms_code(){
            //为了避免重复点击发送短信
            if(this.send_flag == true){
                return;
            }
            this.send_flag = true;

            //检查图片校验码
            this.check_image_code();
            if(this.error_image_code == true || this.error_mobile == true){
                this.send_flag == false;
                return;
            }

            // 验证图形验证码后才能请求短信验证码
            let url = '/sms_codes/' +this.mobile + '/?image_code=' + this.image_code+'&uuid='+ this.uuid;
            axios.get(url,{responseType:'jason'})
                .then(response=>{
                    if(response.data.code == '0'){
                        let num = 60;
                        let t = setInterval(()=>{
                            if(num==1){
                                clearInterval(t);
                                this.error_sms_code_message='获取短信验证码';
                                this.send_flag= false;
                            }else {
                                num -=1;
                                this.error_sms_code_message = num + "s";
                            }
                        },1000,60);

                    }else {
                        if(response.data.code == '4001'){
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }else {
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                    }
                    this.image_generate();
                    this.sending_flag = false;
                })
                .catch(error => {
                    console.log(error.response);
                    this.sending_flag = false;
        })


        },
        //blur光标触发的时候，会执行以下方法
        check_username(){
            //前端js自己检验用户格式是否正确
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if(re.test(this.username)){
                this.error_username = false;
            }else{
                this.error_username_message = '用户名格式不对';
                this.error_username = true;
            }
            //使用axios.js来实现与数据库连接判断用户是否存在
            if (this.error_username == false){
                let url = '/username/' + this.username + '/count/';
                axios.get(url,{responseType:'json'})
                    .then(response=>{
                        //从后端访问返回到的response.data,判断用户名是否重复
                        if (response.data.count == 1){
                            this.error_username_message = '用户名已存在哦';
                            this.error_username = true;
                        }else {
                            this.error_username = false;
                        }
                    })
                    .catch(error=>{
                        console.log(error.response);
                    })
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
                this.error_mobile_message  = '手机号没输对';
                this.error_mobile = true;
            }
            if(this.error_mobile == false){
                let url = '/mobile/' + this.mobile + '/count/';
                axios.get(url,{responseType:'json'})
                    .then(response=>{
                        if(response.data.count == 1) {
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        }else {
                            this.error_mobile = false;
                        }
                    })
                    .catch(error=>{
                        console.log(error.response)
                    })
            }
        },
        check_allow(){
          if(!this.allow){
              this.error_allow = false;
          }else {
              this.error_allow = true;
          }
        },

        check_image_code(){
            if(this.image_code.length != 4){
                this.error_image_code_message = '请填写验证码哦';
                this.error_image_code = true;
            }else {
                this.error_image_code = false;
            }
        },
        check_sms_code(){
            if (this.sms_code.length != 6 ){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            }else {
                this.error_sms_code = false;
            }
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