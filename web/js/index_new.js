old_url = '';
function cklogin()
{
        var user_name = $("#username").val();
        var password = $("#password").val();
        if(user_name.length < 1 || password.length < 1){
                
                $("#shade").hide();
                alert("Account or password can not be null !");
                return false;
        }
        $.ajax({
                type: "post",
                url: "/php/login.php",
                async: true,
                data: {
                    UserName: user_name + "@marvell.com",
                    PassWord: password
                },
                beforeSend: function(XMLHttpRequest){
                    var bd = document.body;
                    $("#shade").css("width", bd.scrollWidth+"px");
                    $("#shade").css("height", bd.scrollHeight+"px");
                    $("#shade").show();
                },
                success: function(res, textStatus){
                    $("#shade").hide();
                    if(res.match("true")){        
                        setCookie('username', user_name, 7);
                        setCookie('password', password, 7);
			/******* qiujie ********/
                        //window.location.href = 'home1.html';
			
			var url =  getCookie("old_url");
			window.location.href = url
			/************/
                        $("#user").text(user_name + "@marvell.com");
                        return true;
                    }else{
                        alert("Account not exsit or password error !");
                        return false;
                    }     
                },
                error: function(){
                    alert("Query failed from Mysql database !");
                }
        });
        return true;
}
function getCookie(c_name)
{
                
if (document.cookie.length > 0)
{    
c_start=document.cookie.indexOf(c_name + "=")
if (c_start!=-1)
{        
c_start=c_start + c_name.length+1 ;
c_end=document.cookie.indexOf(";",c_start);
if (c_end==-1)
{
    c_end=document.cookie.length;
}
return unescape(document.cookie.substring(c_start,c_end));
} 
}
return ""
}

function setCookie(c_name,value,expiredays)
{
var exdate=new Date();
exdate.setDate(exdate.getDate()+expiredays)
document.cookie=c_name+ "=" +escape(value)+
((expiredays==null) ? "" : "; expires="+exdate.toGMTString())
}

function checkCookie()
{
    var username=getCookie('username');
    //var password=getCookie('password');
    if (username==null || username=="")
    {
        //open_login();
        if(window.location.href.indexOf("index.html") != -1){
                return;
        }else{
                //old_url = window.location.href	//qiujie
		setCookie("old_url", window.location.href, 1)
                window.location.href = "login1.html";
        }
    }
    else
    {
        var url_arr = window.location.href.split('/');
        if(url_arr[url_arr.length-1].match('index.html') || url_arr[url_arr.length-1] == '')
        {
            window.location.href = 'home1.html';
        }
        var user_tag = document.getElementById('user');
        user_tag.innerHTML = username + "@marvell.com";
    }
}
function deleteCookie()
{
    MTC.confirm('Are sure to log out ?', 'Log off', function(){
        setCookie('username','',-1);
        setCookie('password','',-1);
        window.location.href = 'index.html';
    });
}

