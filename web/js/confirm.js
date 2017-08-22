var MTC = MTC || {};
MTC.newElem = function(tagName, id, className){
    var elem = document.createElement(tagName);
    id && (elem.id = id);
    className && (elem.className = className);
    return elem;
};

MTC.addShade = function(){
    var bd = document.body;
    var shade = MTC.newElem("div", "shade");
    shade.style.width = bd.scrollWidth+"px";
    shade.style.height = bd.scrollHeight+"px";
    bd.appendChild(shade);
    return shade;
};
MTC.addCss = function(url) {
    var head = document.getElementsByTagName('head')[0];
    var link = document.createElement('link');
    link.href = url;
    link.rel = 'stylesheet';
    link.type = 'text/css';
    head.appendChild(link);
}
MTC.addJs = function(url) {
    var head = document.getElementsByTagName('head')[0];
    var script = document.createElement('script');
    script.src = url;
    script.type = 'text/javascript';
    head.appendChild(script);
}
MTC.confirm = function(msg, title, okCallback, cancelCallback, closeCallback){
    var shade = MTC.addShade();
    var bd = document.body;
    var alertBody = MTC.newElem("div", "alert-body");
    var alertTitle = MTC.newElem("div", "alert-title");
    var span = MTC.newElem("span");
    var titleText = document.createTextNode(title);
    span.appendChild(titleText);
    alertTitle.appendChild(span);
    var alertClose = MTC.newElem("a", "alert-close");
    alertTitle.appendChild(alertClose);
    alertBody.appendChild(alertTitle);
     
    var alertContentHolder = MTC.newElem("div", "alert-content-holder");
    var alertMsg = MTC.newElem("div", "alert-msg");
    var msg = document.createTextNode(msg);
    alertMsg.appendChild(msg);
    var okBtn = MTC.newElem("a", "alert-ok-btn", "alert-btn");
    var ok = document.createTextNode("Ok");
    okBtn.appendChild(ok);
    var cancelBtn = MTC.newElem("a", "alert-cancel-btn", "alert-btn");
    var cancel = document.createTextNode("Cancel");
    cancelBtn.appendChild(cancel);
    alertContentHolder.appendChild(alertMsg);
    alertContentHolder.appendChild(okBtn);
    alertContentHolder.appendChild(cancelBtn);    
    alertBody.appendChild(alertContentHolder);
    bd.appendChild(alertBody);
    
    var close = function(){
        bd.removeChild(shade);
        bd.removeChild(alertBody);
    };
    
    alertClose.onclick = function(){
        close();
        closeCallback && closeCallback();
    };
    
    okBtn.onclick = function(){
        close();
        okCallback && okCallback();
    };
    
    cancelBtn.onclick = function(){
        close();
        cancelCallback && cancelCallback();
    };
};

MTC.alert = function(msg, title, okCallback, closeCallback){
    var shade = MTC.addShade();
    var bd = document.body;
    var alertBody = MTC.newElem("div", "alert-body");
    var alertTitle = MTC.newElem("div", "alert-title");
    var span = MTC.newElem("span");
    var titleText = document.createTextNode(title);
    span.appendChild(titleText);
    alertTitle.appendChild(span);
    var alertClose = MTC.newElem("a", "alert-close");
    alertTitle.appendChild(alertClose);
    alertBody.appendChild(alertTitle);
     
    var alertContentHolder = MTC.newElem("div", "alert-content-holder");
    var alertMsg = MTC.newElem("div", "alert-msg");
    var msg = document.createTextNode(msg);
    alertMsg.appendChild(msg);
    var okBtn = MTC.newElem("a", "alert-ok-btn", "alert-btn");
    var ok = document.createTextNode("Ok");
    okBtn.appendChild(ok);
    okBtn.style.marginLeft = "-50px";
    alertContentHolder.appendChild(alertMsg);
    alertContentHolder.appendChild(okBtn);
    alertBody.appendChild(alertContentHolder);
    bd.appendChild(alertBody);
    
    var close = function(){
        bd.removeChild(shade);
        bd.removeChild(alertBody);
    };
    
    alertClose.onclick = function(){
        close();
        closeCallback && closeCallback();
    };
    
    okBtn.onclick = function(){
        close();
        okCallback && okCallback();
    };
};

MTC.showImage = function(src){
    var bd = document.body;
    var shade = MTC.addShade();    
    var imgBody =MTC.newElem("div", "img-body");
    var imgClose =MTC.newElem("a", "img-close");
    var imgBorder =MTC.newElem("div", "img-border");
    var img =MTC.newElem("img", "img-img");
    img.src = src;
    imgBody.appendChild(imgBorder);
    imgBody.appendChild(imgClose);
    imgBody.appendChild(img);    
    bd.appendChild(imgBody);
    
    var close = function(){
        bd.removeChild(shade);
        bd.removeChild(imgBody);
    };
    imgClose.onclick = function(){
        close();
    };
    shade.onclick = function(){
        close();
    };
};

MTC.select = function(options){
    var that = this,timer;
    var options = options || {"selector":"select"};
    this.onSelect = options.onSelect || function(){console.log("select");};
    this.$self = $("." + options.selector);
    this.$handler = this.$self.find(".select-tit").length && this.$self.find(".select-tit")  || this.$self.find(".selectHandler");
    this.$handlerName = this.$self.find(".select-tit").length && ".select-tit"  || ".selectHandler";
    this.$options = this.$self.find(".options");
    this.$option = this.$options.find(".option");
    this.$selected = this.$self.find(".selected");
    this.selectValue = this.$selected.attr("value");
    this.selectText = this.$selected.html();
    
    this.$self.on('mouseover',function(){
        clearTimeout(timer);
    }).on('mouseout',function(){
        if(that.$options.is(':visible')){
            timer = setTimeout(function(){
                that.$options.slideUp('fast');
                clearTimeout(timer);
            },300);
        }
    });
    this.$self.on('click',this.$handlerName,function(){
        that.$options.slideToggle('fast');
    });
    this.$self.on('click','.option',function(){
        $(this).addClass('current-selected').siblings().removeClass('current-selected');
        that.$selected.html($(this).html());
        that.$selected.attr("value",$(this)[0].getAttribute("value"));//attr bug?
        that.$options.slideUp('fast');
        that.$selected.trigger('change');
        that.onSelect();
    });
    this.value = function(){
        return that.selectValue;
    };
    this.option = function(){
        return that.selectedText;
    };
};

MTC.showFeedback = function(task_id, status){
    var bd = document.body;
    var shade = MTC.addShade();
    var contentHolder = MTC.newElem("div", "frameHolder");
    var title = MTC.newElem("div","alert-title");
    var titleText = MTC.newElem("em");
    if(task_id != undefined){
        titleText.innerHTML = "Task Management";
    }else{
        titleText.innerHTML = "Case Configuration";
    }
    title.appendChild(titleText);
    var close = MTC.newElem("a", "alert-close");
    title.appendChild(close);
    contentHolder.appendChild(title);
    
    var iframe = MTC.newElem("div", "frame");
    iframe.innerHTML = "<div class='content-frame'> \
                            <div id='case_id' style='display:none'></div> \
                            <table cellspacing='8' id='config_table'></table> \
                            <a class='btn'>Done</a> \
                        </div>";
    contentHolder.appendChild(iframe);
    contentHolder.style.display = "none";
    bd.appendChild(contentHolder);
    if(task_id != undefined){
        $.ajax({
            type: "post",
            url: "/php/read-db.php",
            async: false,
            data: {
                sql_cmd: "select * from case_cmd_pool where id=" + task_id    
            },
            beforeSend: function(XMLHttpRequest){
                $("#shade-bg").show();
            },
            success: function(data, textStatus){
                var json_arr = eval('(' + data + ')');
                var result = json_arr[0]["result"];
                if(result != null){
                    result = result.toLowerCase();
                }
                if(status != 'not run'){
                    var tmp = "";
                    if(status == 'running'){
                        $("#config_table").append("<tr><td class='item'>Result:</td><td> \
                                                    <div class='select select6' id='t-result'> \
                                                        <div class='select-tit clearfix'> \
                                                            <div class='selected' value='"+status+"'>"+status+"</div> \
                                                            <div class='selectHandler'><i class='caret'></i></div> \
                                                        </div> \
                                                        <ul class='options' style='margin-left:0px;'> \
                                                            <li class='option' value='running'>running</li> \
                                                            <li class='option' value='stopped'>stopped</li> \
                                                        </ul> \
                                                    </div> \
                                                  </td></tr>");
                    }else{
                        $("#config_table").append("<tr><td class='item'>Result:</td><td> \
                                                    <div class='select select6' id='t-result'> \
                                                        <div class='select-tit clearfix'> \
                                                            <div class='selected' value='"+result+"'>"+result+"</div> \
                                                            <div class='selectHandler'><i class='caret'></i></div> \
                                                        </div> \
                                                        <ul class='options' style='margin-left:0px;'> \
                                                            <li class='option' value='pass'>pass</li> \
                                                            <li class='option' value='failed'>failed</li> \
                                                            <li class='option' value='error'>error</li> \
                                                        </ul> \
                                                    </div> \
                                                  </td></tr>");
                    }
                    var select = new MTC.select({"selector":"select6"});
                    var sw_version = json_arr[0]["sw_version"];
                    $("#config_table").append("<tr><td class='item'>SW version:</td><td><input type='text' id='t-sw' value='"+sw_version+"'></input></td></tr>");
                    var comments = json_arr[0]["reserved"];
                    $("#config_table").append("<tr><td class='item'>Comments:</td><td><input type='text' id='t-comments' value='"+comments+"'></input></td></tr>");
                    var bugid = json_arr[0]["bugid"];
                    $("#config_table").append("<tr><td class='item'>Bug ID:</td><td><input type='text' id='t-bugid' value='"+bugid+"'></input></td></tr>");
                }else{
                    getCaseConfig("", "", "", task_id);
                }
                $("#shade-bg").hide();
            },
            complete: function(XMLHttpRequest, textStatus){
                //override
            },
            error: function(){
                $("#shade-bg").hide();
                alert("Query failed from Mysql database !");
            }
        });
    }
    $("#frame .btn").click(function(){
        if(window.location.href.indexOf("add-case")>-1 || status == 'not run'){
            var config_json = {};
            $("#frame .item").each(
                function(){
                    var option = $(this).attr("value");
                    var value = $(this).next().find("input").val();
                    var comments = $(this).next().find(".easyui-tooltip").attr("title");
                    if (value == undefined){
                        value = $(this).next().find("select").val();
                    }
                    //alert("'"+value+"'");
                    config_json[option] = value+" #"+comments;
                    //alert(option+":"+ value+" #"+comments);
                });
            case_config_json[$("#case_id").text()] = config_json;
            if(status == 'not run'){
                var config_json_task = {};
                config_json_task[task_id] = config_json;
                writeCaseConfig(config_json_task); 
            }
        }else{
            var sql_cmd = '';
            var tmp = $("#t-result").find('.selected').attr("value");
            var sw_version = $("#t-sw").val();
            var comments = $("#t-comments").val();
            var bugid = $("#t-bugid").val();
            //alert(bugid);
            if (tmp.indexOf(";") > -1){
                alert("Please remove ';' from status: "+tmp);return;
            }
            if (sw_version.indexOf(";") > -1){
                alert("Please remove ';' from sw_version: "+sw_version);return;
            }
            if (comments.indexOf(";") > -1){
                alert("Please remove ';' from comments: "+comments);return;
            }
            if (bugid.indexOf(";") > -1){
                alert("Please remove ';' from bugid: "+bugid);return;
            }


            if(status == 'running'){
                sql_cmd = "update case_cmd_pool set status='"+tmp+"',sw_version='"+sw_version+"',reserved='"+comments+"',bugid='"+bugid+"' where id=" + task_id;
            }else{
                sql_cmd = "update case_cmd_pool set result='"+tmp+"',sw_version='"+sw_version+"',reserved='"+comments+"',bugid='"+bugid+"' where id=" + task_id;
            }
            //alert(sql_cmd);
            $.ajax({
                type: "post",
                url: "/php/read-db.php",
                async: false,
                data: {
                    sql_cmd: sql_cmd  
                },
                beforeSend: function(XMLHttpRequest){
                    $("#shade-bg").show();
                },
                success: function(data, textStatus){
                    window.location.href = window.location.href; 
                    $("#shade-bg").hide();
                },
                complete: function(XMLHttpRequest, textStatus){
                    //override
                },
                error: function(){
                    $("#shade-bg").hide();
                    alert("Query failed from Mysql database !");
                }
            });
          /*  alert("edit task!##"+task_id);  */  
        }
        MTC.closeFeedback();
    });
    $("#alert-close").click(function(){
        MTC.closeFeedback();
    });
    $("#frameHolder").fadeIn(500);
};

MTC.Upgrade = function(msg, title){
    MTC.closeFeedback();
    var bd = document.body;
    var shade = MTC.addShade();
    var contentHolder = MTC.newElem("div", "frameHolder");
    var title = MTC.newElem("div","alert-title");
    var titleText = MTC.newElem("em");
    titleText.innerHTML = "Upgrade(fastboot)";
    title.appendChild(titleText);
    var close = MTC.newElem("a", "alert-close");
    title.appendChild(close);
    contentHolder.appendChild(title);

    var iframe = MTC.newElem("div", "frame");
    iframe.innerHTML = "<div class='content-frame'> \
                            <div id='case_id' style='display:none'></div> \
                            <table cellspacing='8' id='config_table' align='top'></table> \
                            </ul></div></tr> \
                            <a class='btn'>Upgrade</a> \
                        </div>";
    contentHolder.appendChild(iframe);
    //contentHolder.style.display = "none";
    bd.appendChild(contentHolder);
    $("#frame .btn").click(function(){
        var sbt_ver, client_id, dut_type,owner;
        if ($("#sbt_ver").find('.selected')) {
            sbt_ver = $("#sbt_ver").find('.selected').attr("value");
        }
        else {
            sbt_ver = $("#sbt_ver").val();
        }
        client_id = $("#client_id").val();
        dut_type = $("#dut_type").val();
        owner = getCookie('username');
        //alert(client_id);
        $.ajax({
            type: "post",
            url: "/php/add_case_cmd.php",
            async: false,
            data: {
                sbt_ver: sbt_ver,
                client_id: client_id,
                dut_type: dut_type,
                version: sbt_ver,
                owner: owner
            },
            beforeSend: function(XMLHttpRequest){
                $("#shade-bg").show();
            },
            success: function(data, textStatus){
                alert(data);
                MTC.closeFeedback();
                $("#shade-bg").hide();
                $("#frameHolder").fadeIn(500);
            },
            complete: function(XMLHttpRequest, textStatus){
                            //override
            },
            error: function(){
                $("#shade-bg").hide();
                alert("Query failed from Mysql database !");
            }
        });
    });
 
    $("#alert-close").click(function(){
        MTC.closeFeedback();
    });
    $("#frameHolder").fadeIn(500);

}

function notifier(){
    console.log("notifier");
}
function upload_all(project_name, case_name, case_abs_path, sql_cmd){
                        $.ajaxFileUpload({
                        url:'php/upload_all.php', //你处理上传文件的服务端
                        data:{'project_name': project_name,
                              'case_name': case_name,
                              'case_abs_path': case_abs_path,
                              'file_type': "upload_package",
                              'file_id':  ["config_path", "case_path"],
                              'sql_cmd': sql_cmd
                             },
                        secureuri:false,
                        fileElementId:['config_path', 'case_path'],//与页面处理代码中file相对应的ID值
                        dataType: 'text',//返回数据类型:text，xml，json，html,scritp,jsonp五种
                        success: function (data, status){
                            alert("upload case package finished.\r\n" + data);
                        },
                        error: function (data, status, e){
                            alert(e);
                        }
                    });
}

MTC.AddCase = function(){
    MTC.closeFeedback();
    var bd = document.body;
    var shade = MTC.addShade();
    var contentHolder = MTC.newElem("div", "frameHolder");
    var title = MTC.newElem("div","alert-title");
    var titleText = MTC.newElem("em");
    titleText.innerHTML = "Customize Test Case";
    title.appendChild(titleText);
    var close = MTC.newElem("a", "alert-close");
    title.appendChild(close);
    contentHolder.appendChild(title);

    var iframe = MTC.newElem("div", "frame");
    iframe.innerHTML = "<div class='content-frame'> \
                            <div id='case_id' style='display:none'></div> \
                            <table cellspacing='8' id='config_table'></table> \
                            </ul></div></td></tr> \
                            <a class='btn'>Done</a> \
                        </div>";
    contentHolder.appendChild(iframe);
    contentHolder.style.display = "none";
    bd.appendChild(contentHolder);


 
    $("#frame .btn").click(function(){
        {
            var sql_cmd = '';
            
            var project_name = $("#project_name").find('.selected').attr("value");
            var case_type = $("#case_type").find('.selected').attr("value");
            var case_name;
            if ($("#case_name").find('.selected')) {
                case_name = $("#case_name").find('.selected').attr("value");
            }
            else {
                case_name = $("#case_name").val(); 
            }
            var case_path = $("#case_path").val();
	    var case_config = $("#case_config").val();
            var case_abs_path = $("#case_abs_path").val();
            var case_description = $("#case_description").val();
            case_description = case_description.replace(/(^\s*)|(\s*$)/g, ""); 
            var customize_type = $("#customize_type").find('.selected').attr("value");
            alert(customize_type);
            if (customize_type == "Extend Case") {
                var extend_project_name = $("#extend_project_name").find('.selected').attr("value");
                var extend_case_type = $("#extend_case_type").find('.selected').attr("value");
                var extend_case_name = $("#extend_case_name").val();
                
                alert("extend dut type:"+extend_project_name+"\r\nextend case type:"+extend_case_type+"\r\ncase name:"+extend_case_name);
                alert("dut type:"+project_name+"\r\ncase type:"+case_type+"\r\ncase name:"+case_name);
                if (extend_project_name == project_name && extend_case_name == case_name){
                    alert("extend case name and dut type should different with parent's");
                }
                else if (case_description == null || case_description.length == 0){
                    alert("case description should not be null; case description:'"+case_description+"'");
                }
                else {
                    sql_cmd = "insert into case_info (name, dut_type, description, case_type, path) values ('"+extend_case_name+"', '"+extend_project_name+"', '"+case_description+"', '"+extend_case_type+"', (select a.path from case_info as a where a.name='"+case_name+"' and a.dut_type='"+project_name+"'))";
                    alert(sql_cmd);
                    $.ajax({
                        type: "post",
                        url: "/php/write-db.php",
                        async: false,
                        data: {
                            sql_cmd: sql_cmd
                        },
                        beforeSend: function(XMLHttpRequest){
                            $("#shade-bg").show();
                        },
                        success: function(data, textStatus){
                            if (data.indexOf("Error") > 0 || data.indexOf("error") > 0){
                                alert("Query failed from Mysql: " + data);
                            }
                            else {
                            
                            }
                            window.location.href = window.location.href;
                            $("#shade-bg").hide();
                        },
                        complete: function(XMLHttpRequest, textStatus){
                            //override
                        },
                        error: function(){
                            $("#shade-bg").hide();
                            alert("Query failed from Mysql database !");
                        }
                    });
                    $.ajax({
                        type: "post",
                        url: "/php/extend_case.php",
                        async: false,
                        data: {
                            project_name: project_name,
                            case_name: case_name,
                            extend_project_name: extend_project_name,
                            extend_case_name: extend_case_name
                        },
                        beforeSend: function(XMLHttpRequest){
                            $("#shade-bg").show();
                        },
                        success: function(data, textStatus){
                            window.location.href = window.location.href;
                            $("#shade-bg").hide();
                        },
                        complete: function(XMLHttpRequest, textStatus){
                            //override
                        },
                        error: function(){
                            $("#shade-bg").hide();
                            alert("Query failed from Mysql database !");
                        }
                    });
                }
            }
            else if (customize_type == "Update Case") {
                    sql_cmd = "update case_info set description='"+case_description+"' where name='"+case_name+"' and dut_type='"+project_name+"'";
                    upload_all(project_name, case_name, case_abs_path, sql_cmd);
            }
            else if (customize_type == "Add New Case") {
                var upload_config = $("#config_path").val();
                upload_config = upload_config.replace(/(^\s*)|(\s*$)/g, "");
                var upload_package = $("#case_path").val();
                upload_package = upload_package.replace(/(^\s*)|(\s*$)/g, "");
                case_name = $("#case_name").val();
                if (upload_config == null || upload_config == ""){
                    alert("No config.py file upload");
                }
                else if (upload_package == null || upload_package == "") {
                    alert("No case package upload");
                }
                else {
                    case_abs_path = "TestCase/all/"+case_name+".tar.gz";
                    var sql_cmd = "insert case_info (name, path, dut_type, description, case_type) value ('"+case_name+"', '"+case_abs_path+"', '"+project_name+"', '"+case_description+"', '"+case_type+"')";
                    upload_all(project_name, case_name, case_abs_path, sql_cmd);
                }
            }
          /*  alert("edit task!##"+task_id);  */
        }
        MTC.closeFeedback();
	alert("close");		
    });
    $("#alert-close").click(function(){
        MTC.closeFeedback();
    });
    $("#frameHolder").fadeIn(500);
}    

MTC.closeFeedback = function(){    
    var bd = document.body;
    var shade = document.getElementById("shade");
    var frameHolder = document.getElementById("frameHolder");
    if (shade != null){
        bd.removeChild(shade);
    }
    if (frameHolder != null){
        bd.removeChild(frameHolder);
    }
};

