var dut_cnt_json = {};
function getOnlineNumber(){
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select client_id,dut_type,status from conn_info where mac_addr is not null and status != 'invalid'"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json = eval('(' + data + ')');
            for(var i=0;i<json.length;i++){
                var dut_type = json[i]["dut_type"];
                var status = json[i]["status"];
                if(status != "offline" && status != "dead"){
                    if(dut_cnt_json[dut_type] == undefined){
                        dut_cnt_json[dut_type] = 1;
                    }else{
                        dut_cnt_json[dut_type]++;  
                    }
                }
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
function getDutType(){
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from dut_type where name != 'gtvv4_4k' and name != 'gtvv4_cedar' and name != 'gtvv4_bg2' and name != 'gtv_bat' and name != 'jellybean' and name != 'ics' and name != 'gtvv4_willow' and name != 'bg2q4k' and name != 'LinuxRDK' "
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json = eval('(' + data + ')');
            getOnlineNumber();
            var rows = [];
            for(var i=0;i<json.length;i++){
                var dut_type = json[i]["name"];
                var dut_des = json[i]["description"];
                var dut_num_html = "";
                var dut_num = dut_cnt_json[dut_type];
                if(dut_num == undefined){dut_num_html="0"}
                if(dut_num > 0){
                    dut_num_html = "<a target='_blank' style='color:#5ab530;font-weight:bold' href='device-info.html?pname=dev-list'>"+dut_num+"</a>";
                }
                rows.push({
                    dut_type: dut_type,
                    dut_des: dut_des,
                    dut_num: dut_num_html
                });
            }
            $('#dut_type_create').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', rows);
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
function getSelectedDutType(){
    var dut_list = $('#dut_type_create').datagrid("getChecked");
    if(dut_list.length < 1){
        MTC.alert("Please at least select one DUT type !", "DUT error");
        return false;
    }else if(dut_list.length > 1){
        MTC.alert("Please select no more than one DUT type !", "DUT error");
        return false;
    }else if(dut_list[0]['dut_num']==0){
        MTC.alert("Please select DUT with at least one available device !", "DUT error");
        return false;
        //return true;
    }else{
        return true;
    }
}
function getCaseInfo() {
    var cons = "";
    var p_val = $('#dut_type_create').datagrid("getChecked")[0]['dut_type'];
    if(p_val != "Any"){
        cons = " where dut_type=" + "'" + p_val + "'";
    }
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from case_info" + cons
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json = eval('(' + data + ')');
            var json_fixed = getCaseData(json);
            $('#case-info').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', json_fixed);
            if (json_fixed.length != 0 && $('#case-info').datagrid('getRows').length == 0){
                $('#case-info').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', json_fixed);
            }
            //$('#case-info').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', json_fixed);
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
function getCaseInfo_extend(dut_type) {
    var cons = "";
    if (dut_type == "Any"){
        var p_val = "Any";
    }
    else {
        var p_val = dut_type;
    }
    if(p_val != "Any"){
        cons = " where dut_type=" + "'" + p_val + "'";
    }
    else{
        cons = " where dut_type != 'gtvv4_4k' and dut_type != 'gtvv4_cedar' and dut_type != 'gtvv4_bg2' and dut_type != 'gtv_bat' and dut_type != 'jellybean' and dut_type != 'ics' and dut_type != 'gtvv4_willow'";
    }
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from case_info" + cons
        },
        beforeSend: function(XMLHttpRequest){
            //$("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json = eval('(' + data + ')');
            json_result= getCaseData_extend(json);
            //$("#shade-bg").hide();
        },
        complete: function(XMLHttpRequest, textStatus){
            //override
        },
        error: function(){
            //$("#shade-bg").hide();
            alert("Query failed from Mysql database !");
        }
    });
}

function getCaseData(json_array){
    if($("#case_classify").find("tr").length<1){
        var type_list = new Array();
        var tr = $("<tr></tr>");
        tr.append("<td rowspan=2>Classification:&nbsp;&nbsp;</td>");
        if (json_array.length > 0){
            tr.append("<td><input type='checkbox' id='case_type_all' value='all' checked='checked'></input></td><td><span>select all</span></td>");
        }

        for(var i=0;i<json_array.length;i++){
            var case_type = json_array[i]["case_type"];
            if($.inArray(case_type, type_list)>-1){continue}
            tr.append("<td><input name='case_type' type='checkbox' id='case_type_"+i+"' value='"+case_type+"' checked='checked'></input></td><td><span>"+case_type+"</span></td>");
            type_list.push(case_type);
        }
        $("#case_classify").append(tr);
        $("#case_classify input").bind({
            click: function() {
                if ($(this).attr('id') == 'case_type_all'){
                    /*
                    if($(this).attr("checked")){
                        $("#case_classify input[name='case_type']").each(function(){
                            alert('disable' + $(this).attr('id') + ' ' + $(this).attr("value") + ' ' + $(this).prop("checked"));
                            $(this).prop("checked",false);
                            alert($(this).attr('id') + ' ' + $(this).attr("value") + ' ' + $(this).prop("checked"));
                        });
                    }
                    else{
                        $("#case_classify input[name='case_type']").each(function(){
                            //alert("enable " + $(this).attr("value"));
                            alert('enable' + $(this).attr('id') + ' ' + $(this).attr("value") + ' ' + $(this).prop("checked"));
                            $(this).prop("checked",true);
                            alert($(this).attr('id') + ' ' + $(this).attr("value") + ' ' + $(this).prop("checked"));
                        });
                    }
                    */
                }
                {
                    if($(this).attr("checked")){
                        $(this).attr("checked",false);
                    }else{
                        $(this).attr("checked",true);
                    }
                }
                if ($(this).attr('id') == 'case_type_all'){
                    $("#case_classify input[name='case_type']").prop("checked",this.checked).attr("checked", this.checked);
                }

                getCaseInfo();
            } 	
        });
        /*
        $('#case_classify input').iCheck({
	    checkboxClass: 'icheckbox_square-blue',
	    radioClass: 'iradio_square-blue',
	    increaseArea: '20%'
	});
        */
    }
    var case_type_list = new Array();
    $("#case_classify input[type='checkbox']:checked").each(function(){
        //alert($(this).val());
	case_type_list.push($(this).val());	
    });
    var rows = [];
    for(var i=0; i<json_array.length; i++){
        var case_id = json_array[i]["id"];
        var case_name = json_array[i]["name"];
        var dut_type = json_array[i]["dut_type"];
        var case_des = json_array[i]["description"];
        var case_type = json_array[i]["case_type"];
        if($.inArray(case_type, case_type_list)==-1){continue}
        var case_time = "&nbsp;&nbsp;60000";
        var document_url = "http://debutrac.marvell.com/trac/SQA/wiki/"+case_name;
        rows.push({
            case_id: case_id,
            case_name: case_name,
            dut_type: dut_type,
            case_type: case_type,
            description: case_des,
            round_time: case_time,
            document_url: document_url 
        });
    }
    return rows;
}
function getCaseData_extend(json_array){
    var rows = [];
    for(var i=0; i<json_array.length; i++){
        var case_id = json_array[i]["id"];
        var case_name = json_array[i]["name"];
        var dut_type = json_array[i]["dut_type"];
        var case_des = json_array[i]["description"];
        var case_type = json_array[i]["case_type"];
        var case_time = "&nbsp;&nbsp;60000";
        rows.push({
            case_id: case_id,
            case_name: case_name,
            dut_type: dut_type,
            case_type: case_type,
            description: case_des,
            round_time: case_time,
        });
    }
    return rows;
}

function getSelectedCase(){
    var case_list = $('#case-info').datagrid("getChecked");
    if(case_list.length < 1){
        MTC.alert("Please at least select one task into test pool !", "No task");
        return false;
    }
    return true;
}
function getSelectedDevice(){
    var device_list = $('#online-device-info').datagrid("getChecked");
    if(device_list.length < 1){
        MTC.alert("Please select one device for your task !", "No device");
        return false;
    }
    return true;
}
function pagerFilter(data){
    if (typeof data.length == 'number' && typeof data.splice == 'function'){    // is array
        data = {
            total: data.length,
            rows: data
        }
    }
    var dg = $(this);
    var opts = dg.datagrid('options');
    var pager = dg.datagrid('getPager');
    pager.pagination({
        onSelectPage:function(pageNum, pageSize){
            opts.pageNumber = pageNum;
            opts.pageSize = pageSize;
            pager.pagination('refresh',{
                pageNumber:pageNum,
                pageSize:pageSize
            });
            dg.datagrid('loadData',data);
        }
    });
    if (!data.originalRows){
        data.originalRows = (data.rows);
    }
    var start = (opts.pageNumber-1)*parseInt(opts.pageSize);
    var end = start + parseInt(opts.pageSize);
    data.rows = (data.originalRows.slice(start, end));
    return data;
}
        
var editIndex = undefined;
function endEditing(){
    if (editIndex == undefined){return true}
    if ($('#case-info').datagrid('validateRow', editIndex)){
        $('#case-info').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field){
    if (endEditing() && (field == "total_rounds" || field == "round_time")){
        $('#case-info').datagrid('selectRow', index)
                .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}
function getOnlineDeviceInfo() {
    var cons = "";
    var p_val = $('#dut_type_create').datagrid("getChecked")[0]['dut_type'];
    if(p_val != "Any"){
        cons = " where status != 'offline' and status != 'dead' and status != 'invalid' and mac_addr is not null and dut_type=" + "'" + p_val + "'";
    }else{
        cons = " where status != 'offline' and status != 'dead' and status != 'invalid' and mac_addr is not null";
    }
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from conn_info" + cons
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json = eval('(' + data + ')');
            var json_fixed = getOnlineDeviceData(json);
            $('#online-device-info').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', json_fixed);
            //$('#online-device-info').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', json_fixed);
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
function getOnlineDeviceData(json_array){
    //$("#online-device-info tbody").empty();
    var owner_list = new Array();
    $("#device_classify input[type='checkbox']:checked").each(function(){
	owner_list.push($(this).attr("id"));	
    });
    var curr_user = getCookie('username');
    var rows = [];
    for(var i=0; i<json_array.length; i++){
        var device_id = json_array[i]["client_id"];
        var device_ip = json_array[i]["client_ip"];
        var dut_type = json_array[i]["dut_type"];
        var sw_info = json_array[i]["sw_version"];
        if(sw_info != null){
            sw_info = sw_info.replace(/0x20/gi, " ");
        }
        var owner = json_array[i]["owner"];
        if($.inArray("my-devices", owner_list)==-1){
            if(owner == curr_user){continue}
        }
        if($.inArray("others-devices", owner_list)==-1){
            if(owner != curr_user){continue}
        }
        var owner_info = "<a href='mailto:"+owner+"@marvell.com'>"+owner+"</a>";
        var start_time = json_array[i]["start_time"];
        var status = json_array[i]["status"];
        if(status=="idle"){
            status = "<span style='color:#5ab530'>"+status+"</span>"
        }else if(status=="busy"){
            status = "<span style='color:red'>"+status+"</span>"
        }
        rows.push({
            device_id: device_id,
            device_ip: device_ip,
            dut_type: dut_type,
            sw_info: sw_info,
            owner_info: owner_info,
            start_time: start_time,
            status: status
        });
    }
    return rows;
}
var case_config_json = {};
function submitTask(){
    var curr_user = getCookie('username');
    var case_list = $('#case-info').datagrid("getChecked");
    var device_list = $('#online-device-info').datagrid("getChecked");
    var client_id_arr = new Array();
    for(var j=0;j<device_list.length;j++){
        var client_id = device_list[j]["device_id"];
        client_id_arr.push(client_id);
    }
    var val_list = new Array();
    var config_list = new Array();
    for(var i=0;i<case_list.length;i++){
        var case_owner = curr_user;
        var case_id = case_list[i]["case_id"];
        var case_config = case_config_json[case_id];
        config_list.push(case_config);
        var dut_type = case_list[i]["dut_type"];
        var client_id = client_id_arr.join(";");
        var now = new Date();
        var create_time = now.getFullYear() + '-' + (now.getMonth()+1) + '-' + now.getDate() + ' ' +now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds();
        var case_time = parseInt(case_list[i]["round_time"]);
        var deadline = new Date(now.getTime() + 604800*1000);
        var deadline_str = deadline.getFullYear() + '-' + (deadline.getMonth()+1) + '-' + deadline.getDate() + ' ' + deadline.getHours() + ':' + deadline.getMinutes() + ':' + deadline.getSeconds();
        var status = "not run";
        val_list.push("('"+case_owner+"'"+","+case_id+","+"'"+dut_type+"'"+","+"'"+client_id+"'"+","+"'"+create_time+"'"+","+"'"+deadline_str+"'"+","+"'"+status+"')");
    }
    var val_str = val_list.join(",");
    var insert_task_len = config_list.length;
    $.ajax({
        type: "post",
        url: "/php/write-db.php",
        async: false,
        data: {
            sql_cmd: "insert into case_cmd_pool(cmd_owner,case_id,dut_type,client_id,create_time,deadline,status) values" + val_str
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var first_task_id = parseInt(data);
            var task_config_json = {};
            for(var i=0;i<insert_task_len;i++){
                var task_id = first_task_id + i;
                var case_config = config_list[i];
                task_config_json[task_id] = case_config;
            }
            writeCaseConfig(task_config_json);
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
function getCaseConfig(case_id, dut_type, case_name, task_id){
    var curr_user = getCookie('username');
    $.ajax({
        type: "post",
        url: "/php/read-file.php?case_owner=" + curr_user,
        async: false,
        data: {
            dut_type: dut_type.toUpperCase(),
            case_name: case_name,
            task_id: task_id
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            if(data=="false"){return;}
            if(window.location.href.indexOf("add-case") != -1){
                MTC.showFeedback(undefined, undefined);
            }
            $("#case_id").text(case_id);
            var comment_re = new RegExp("^\\s{0,}#{1,}" , "i");
            var enum_re = new RegExp("(.*)enum:([^;]*)(.*)" , "i");
            var int_res = new RegExp("(.*)int:([^;]*)(.*)", "i");
            var config_re = new RegExp("(\\s{0,})(\\S*)(\\s{0,})=(\\s{0,})([^#]*)(.*)", "i");
            var config_add_re = new RegExp("([^#]*)", "i");
            var data_arr = data.split("\n");
            $("#config_table").empty();
            focused = false;
            var src_json = {};
            for(var i=0;i<data_arr.length;i++){
                var comment_matcher = data_arr[i].match(comment_re);
                var config_matcher = data_arr[i].match(config_re);
                var config_add_matcher = data_arr[i].match(config_add_re);
                var enum_matcher = data_arr[i].match(enum_re);
                var int_matcher = data_arr[i].match(int_res);
                if(comment_matcher != null){
                    continue;
                }else if(config_matcher != null){
                    var option = config_matcher[2];
                    var value = config_matcher[5];
                    var value_cons = config_matcher[6];
                    if(value_cons.indexOf("#")>-1){
                        value_cons = value_cons.substring(1, value_cons.length);
                    }
                    var fg_disable = false;
                    if (value_cons.indexOf("Could not be edit") > -1){
                        fg_disable = true;
                    }
                    var enum_type = "";
                    if (value_cons.indexOf("enum") > -1){
                        if (enum_matcher == null) {alert("invalid enum: "+value_cons);}
                        var enum_str = enum_matcher[2];
                        $("#config_table").append(get_select(option, value, value_cons, enum_str.split(","), fg_disable, false));
                    }
                    else if (value_cons.indexOf("boolean") > -1){
                        $("#config_table").append(get_select(option, value, value_cons,["False", "True"], fg_disable, false));
                    }
                    else if (0){//value_cons.indexOf("int") > -1){
                        alert("12");
                        if (int_matcher == null){alert("invalid int: "+value_cons);}
                        var int_str = int_matcher[2];
                        $("#config_table").append(get_input_int(option, value, value_cons, int_str.split(",")[0], int_str.split(",")[1], fg_disable, false));
                    }
                    else{ 
                    if(option != "__all__"){
                        //alert(value_cons);
                        $("#config_table").append(get_input_text(option, value, value_cons, fg_disable, false));
                        if(!focused){
                            //$("#config_table").append("<tr><td class='item' value='"+option+"'>"+option+":</td><td><input title='"+value_cons+"' type='text' "+disabled_str+" value='"+value+"'></input></td></tr>");
                            focused = true;
                        }else{
                            //$("#config_table").append("<tr><td class='item' value='"+option+"'>"+option+":</td><td><input title='"+value_cons+"' type='text' "+disabled_str+" value='"+value+"'></input></td></tr>");
                        }
                    }else{
                        //$("#config_table").append("<tr style='display:none'><td class='item' value='"+option+"'>"+option+":</td><td><input type='text'"+disabled_str+"value='"+value+"' title='unknown'></input></td></tr>");
                        $("#config_table").append(get_input_text(option, value, value_cons, fg_disable, true));
                    }
                    }
                }else if(config_add_matcher != null){
                    if(data_arr[i].match(/.+/gi)){
                        var td_el = $("#config_table td[value='__all__']").next();
                        var input_el = td_el.find("input");
                        input_el.val(input_el.val() + data_arr[i]);
                    }
                }
                
            }
            var config_json = {};
            $("#frame .item").each(
                function(){
                    var option = $(this).attr("value");
                    var value = $(this).next().find("input").val();
                    var comments = $(this).next().find(".easyui-tooltip").attr("title");
                    if (value == undefined){
                        value = $(this).next().find("select").val();
                    }

                    config_json[option] = value+" #"+comments;
                    //alert(option+":"+value+"#"+comments);
                });
            case_config_json[$("#case_id").text()] = config_json;

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
function writeCaseConfig(task_config_json){
    var curr_user = getCookie('username');
    var dut_type = $('#dut_type_create').datagrid("getChecked")[0]["dut_type"];
    $.ajax({
        type: "post",
        url: "/php/write-file.php?case_owner=" + curr_user + "&dut_type=" + dut_type,
        async: false,
        data: task_config_json,
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
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
function getResultHtmlFile(task_id){
    htmlobj = $.ajax({url:"/php/chk_file.php?task_id="+task_id, async:false});
    var res = htmlobj.responseText;
    if(res.indexOf("true")>-1){
        return true;
    }
    return false;
}
function getResultHtmlFold(task_id){
    htmlobj = $.ajax({url:"/php/chk_fold.php?task_id="+task_id, async:false});
    var res = htmlobj.responseText;
    if(res.indexOf("true")>-1){
        return true;
    }
    return false;
}

var is_reload = true;

function get_cell_in_table(cell_value, max_length, center){
    var td_start = "<td>";
    if (center != undefined && center == true){
        td_start = "<td style='text-align:center'>";
    }

    if (max_length == undefined || max_length <= 0 || cell_value == null || cell_value.length <= max_length){
        return td_start + cell_value + "</td>";
    }
    var cell_value_short = cell_value.substring(0, max_length-1) + " ...";
    return td_start + "<span name='tooltip' title='" + cell_value + "'>" + cell_value_short + "</span></td>";

}
function gettaskid_str(task_id){
    return get_cell_in_table(task_id);
}
function getstatus_str(status_str){
    return get_cell_in_table(status_str);
}
function getcasename_str(case_name){
    return get_cell_in_table(case_name, 25);
}
function gettaskowner_str(task_owner){
    return get_cell_in_table(task_owner);
}
function getduttype_str(dut_type){
    return get_cell_in_table(dut_type, 8);
}
function getclientname_str(pcname, pcip){
    if (pcname == 'unknown') {return "<td>" + pcip + "</td>";}
    return "<td>" + "<span name='tooltip' title='" + pcip + "'>" + pcname + "</span></td>";
}
function getswver_str(sw_version){
    return get_cell_in_table(sw_version, 10);
}
function getstarttime_str(start_time){
    return get_cell_in_table(start_time, 25);
}
function getreport_str(report){
    return get_cell_in_table(report, 0, true);
}
function getresult_str(result){
    return get_cell_in_table(result, 0, true);
}
function getcomments_str(comments){
    return get_cell_in_table(comments, 0, true);
}
function getaction_str(action){
    return get_cell_in_table(action, 0, true);
}
function getTaskData_All(json_array, start_idx, end_idx){
    $.getScript('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js',function(e){
        var server_ip = "10.37.132.95";
        if (remote_ip_info.country == "中国") {server_ip="10.37.132.95";} 
        else {server_ip="10.37.142.99";}
    

    if (start_idx == undefined || end_idx == undefined){
        startidx = 0;
        endidx = 10;
    }else{
        startidx = start_idx;
        endidx = end_idx;
    }
    $("#task-list tbody").empty();
    var curr_user = getCookie('username');
    var cnt = 0;
    var max_sw_length = 173;
    var max_case_length = 173;
    var status_arr = new Array();
    var case_arr = new Array();
    var version_arr = new Array();
    var result_arr = new Array();
    var dut_arr = new Array();
    for(var i=0; i<json_array.length; i++){
        if (i < startidx || i > endidx) {cnt++;continue;}
        var task_id = json_array[i]["id"];
        var client_ip = json_array[i]["client_ip"];
        var client_pcname = json_array[i]["client_pcname"];
        var status = json_array[i]["status"];
        if($.inArray(status, status_arr)==-1 && is_reload){
            $("#select_status .options").append("<li class='option' value='"+status+"'>"+status+"</li>");
            status_arr.push(status);
        }
        
        var status_html = "";
        //var taskid_html = "<span style='color:darkorange'>"+task_id+"</span>";
        if(status=="finished"){
            status_html = "<span style='color:#5ab530'>"+status+"</span>";
        }else if(status=="running"){
            status_html = "<span style='color:darkorange'>"+status+"</span>";
        }else if(status=="not run"){
            status_html = "<span style='color:#009ACD'>"+status+"</span>";
        }else if(status=="stopped"){
            status_html = "<span style='color:chocolate'>"+status+"</span>"; 
        }else if(status=="canceled"){
            status_html = "<span style='color:chocolate'>"+status+"</span>"; 
        }
        
        var result = json_array[i]["result"];
        if(result != null){
            result = result.toLowerCase();
        }
        if($.inArray(result, result_arr)==-1 && is_reload){
            $("#select_result .options").append("<li class='option' value='"+result+"'>"+result+"</li>");
            result_arr.push(result);
        }
        result_html = "";
        
        switch (result){
        case "pass":
            result_str = result;
            result_html_style = "color:#5ab530";
            break;
        case "canceled":
            result_str = result;
            result_html_style = "color:darkmagenta";
            break;
        case "failed":
        case "error":
        case "stopped":
            result_str = result;
            result_html_style = "color:red";
            break;
        case null:
        case "null":
            result_str = "----";
            result_html_style = "color:cornflowerblue";
            break;
        default:
            alert("invalid result "+result);
            break;
        }
        
        if(getResultHtmlFile(task_id)){
            result_html = "<a style='"+result_html_style+"' href='Log/"+task_id+"/result.html' target='_blank'>"+result_str+"</a>";
        }
        else if(getResultHtmlFold(task_id)){
            result_html = "<a style='"+result_html_style+"' href='Log/"+task_id+"/result/result.html' target='_blank'>"+result_str+"</a>";
        }
        else{
            result_html = "<span style='"+result_html_style+"' >"+result_str+"</span>";
        }
        
        var case_name_bak = "";
        var case_name = json_array[i]["name"];
        if(case_name.length>25){
            case_name_bak = case_name.substring(0,25)+" ...";
        }else{
            case_name_bak = case_name;
        }
        if($.inArray(case_name, case_arr)==-1 && is_reload){
            $("#select_case .options").append("<li class='option' value='"+case_name+"'>"+case_name+"</li>");
            case_arr.push(case_name);
            if((case_name.length*8) > max_case_length){
                max_case_length = case_name.length*8;
            }
            $("#select_case .options").css("width",max_case_length+10+"px");
            $("#select_case .option").css("width",max_case_length+"px");
        }
        var task_owner = json_array[i]["cmd_owner"];
        var task_owner_html = "<a href='mailto:"+task_owner+"@marvell.com'>"+task_owner+"</a>";        
        var dut_type = json_array[i]["dut_type"];
        var dut_type_short = "";
        if(dut_type.length>10){
            dut_type_short = dut_type.substring(0,7)+" ...";
        }else{
            dut_type_short = dut_type;
        }
        
        if($.inArray(dut_type, dut_arr)==-1 && is_reload){
            $("#select_dut_type .options").append("<li class='option' value='"+dut_type+"'>"+dut_type+"</li>");
            dut_arr.push(dut_type);
        }
        var sw_version_bak = "";
        var sw_version = json_array[i]["sw_version"].replace(/0x20/gi, " ");
        if($.inArray(sw_version, version_arr)==-1 && is_reload){
            $("#select_version .options").append("<li class='option' value='"+sw_version+"'>"+sw_version+"</li>");
            version_arr.push(sw_version);
            if((sw_version.length*8) > max_sw_length){
                max_sw_length = sw_version.length*8;
            }
            $("#select_version .options").css("width",max_sw_length+10+"px");
            $("#select_version .option").css("width",max_sw_length+"px");
        }
        if(sw_version.length>10){
            sw_version_bak = sw_version.substring(0,10)+" ...";
        }else{
            sw_version_bak = sw_version;
        }
        var create_time = json_array[i]["create_time"];
        var start_time = json_array[i]["start_time"];
        if(start_time == null){
            start_time = "----";
        }
        if(status == 'finished'){
            var test_report = "<a target='_blank' href='ftp://sqa:123456@"+server_ip+"/CaseDispatcher_v2.0/server/Log/"+task_id+"'>Download</a>";
            if((navigator.userAgent.indexOf('MSIE') >= 0) && (navigator.userAgent.indexOf('Opera') < 0)){
                test_report = "<a target='_blank' href='ftp://sqa:123456@"+server_ip+"/home/sqa/CaseDispatcher_v2.0/server/Log/"+task_id+"'>Download</a>";  
            }
        }else{
            test_report = "<a>----</a>";
        }
        var comments = json_array[i]["reserved"];
        var comments_a = "----";
        if(comments != null && comments != 'null'){
            comments_a = "detail";
        }
        var action = "----";
        if(task_owner == curr_user){
            action = "<a id='duplicate' class='k-button' href='javascript:duplicateTask("+task_id+")'><span class='k-icon k-dup'></span></a> \
                      <a id='edit' class='k-button' href='javascript:MTC.showFeedback("+task_id+", \""+status+"\")'><span class='k-icon k-edit'></span></a> \
                      <a id='delete' class='k-button' href='javascript:deleteTask("+task_id+")'><span class='k-icon k-del'></span></a>"
        }
        
        if(window.location.href.indexOf("sbt")>-1 ){
            if(task_owner == "sbt"){
                $("#task-list tbody").append("<tr><td>"+task_id+"</td><td>"+status_html+"</td><td><span name='case_tooltip' title='"+case_name+"'>"+case_name_bak+"</span></td><td>"+task_owner_html+"</td><td><span name='sw_tooltip' title='"+dut_type+"'>"+dut_type_short+"</span></td><td>"+client_ip+"</td><td><span name='sw_tooltip' title='"+sw_version+"'>"+sw_version_bak+"</span></td><td>"+start_time+"</td><td style='text-align:center'>"+test_report+"</td><td style='text-align:center'>"+result_html+"</td><td style='text-align:center'><a name='comment' title='"+comments+"'>"+comments_a+"</a></td><td style='text-align:center'>"+action+"</td></tr>");
                cnt++;
            }
        }else{
            if(task_owner != "sbt"){
                //$("#task-list tbody").append("<tr><td>"+task_id+"</td><td>"+status_html+"</td><td><span name='case_tooltip' title='"+case_name+"'>"+case_name_bak+"</span></td><td>"+task_owner_html+"</td><td><span name='sw_tooltip' title='"+dut_type+"'>"+dut_type_short+"</span></td><td>"+client_ip+"</td><td><span name='sw_tooltip' title='"+sw_version+"'>"+sw_version_bak+"</span></td><td>"+start_time+"</td><td style='text-align:center'>"+test_report+"</td><td style='text-align:center'>"+result_html+"</td><td style='text-align:center'><a name='comment' title='"+comments+"'>"+comments_a+"</a></td><td style='text-align:center'>"+action+"</td></tr>");
                var append_str = "<tr>";
                append_str += gettaskid_str(task_id);
                append_str += getstatus_str(status_html);
                append_str += getcasename_str(case_name);
                append_str += gettaskowner_str(task_owner_html);
                append_str += getduttype_str(dut_type);
                append_str += getclientname_str(client_pcname, client_ip);
                append_str += getswver_str(sw_version);
                append_str += getstarttime_str(start_time);
                append_str += getreport_str(test_report);
                append_str += getresult_str(result_html);
                append_str += getcomments_str("<a name='comment' title='"+comments+"'>"+comments_a+"</a>");
                append_str += getaction_str(action);
                append_str += "</tr>";

                $("#task-list tbody").append(append_str);
            }

                cnt++;
        }
        
    }
    if (start_idx != undefined || end_idx != undefined){return;}
    $(".totalnum").text(cnt);
    init();
    $( "a[name='comment'][title != 'null']" ).tooltip({
        show: null,
        tooltipClass: "tooltip-ui",
        position: {
            my: "left top",
            at: "left bottom"
        },
        open: function( event, ui ) {
            ui.tooltip.animate({ top: ui.tooltip.position().top + 10 }, "fast" );
        }
    });
    $("span[name='sw_tooltip']").tooltip({
        show: null,
        tooltipClass: "tooltip-sw",
        position: {
            my: "left top",
            at: "left bottom"
        },
        open: function( event, ui ) {
            ui.tooltip.animate({ top: ui.tooltip.position().top + 10 }, "fast" );
        }
    });
    $("span[name='case_tooltip']").tooltip({
        show: null,
        tooltipClass: "tooltip-sw",
        position: {
            my: "left top",
            at: "left bottom"
        },
        open: function( event, ui ) {
            ui.tooltip.animate({ top: ui.tooltip.position().top + 10 }, "fast" );
        }
    });
    is_reload = false;
    });
}



function cancelTask(task_id){
    MTC.confirm("Task will be stopped after canceled, are you sure ?", "Cancel task", function(){
        $.ajax({
            type: "post",
            url: "/php/write-db.php",
            async: false,
            data: {
                sql_cmd: "update case_cmd_pool set result='canceled' where id=" + task_id // Add user query constraint
            },
            beforeSend: function(XMLHttpRequest){
                $("#shade-bg").show();
                
            },
            success: function(data, textStatus){
                $("#shade-bg").hide();
                window.location.href = window.location.href; 
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
}
function deleteTask(task_id){
    MTC.confirm("Task recording will be lost after deleted, are you sure ?", "Delete task", function(){
        $.ajax({
            type: "post",
            url: "/php/write-db.php",
            async: false,
            data: {
                sql_cmd: "delete from case_cmd_pool where id=" + task_id
            },
            beforeSend: function(XMLHttpRequest){
                $("#shade-bg").show();
            },
            success: function(data, textStatus){
                $("#shade-bg").hide();
                window.location.href = window.location.href;
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
}
function duplicateConfigFile(src_id, des_id){
    $.ajax({
        type: "post",
        url: "/php/duplicate_config.php",
        async: false,
        data: {
            src_id: src_id,
            des_id: des_id
        },
        beforeSend: function(XMLHttpRequest){
            //override
        },
        success: function(data, textStatus){
            //override
        },
        complete: function(XMLHttpRequest, textStatus){
            //override
        },
        error: function(){
            alert("Query failed from Mysql database !");
        }
    });
}
function duplicateTask(task_id){
    var now = new Date();
    var create_time = now.getFullYear() + '-' + (now.getMonth()+1) + '-' + now.getDate() + ' ' +now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds();
    var deadline = new Date(now.getTime() + 604800*1000);
    var deadline_str = deadline.getFullYear() + '-' + (deadline.getMonth()+1) + '-' + deadline.getDate() + ' ' + deadline.getHours() + ':' + deadline.getMinutes() + ':' + deadline.getSeconds();
    MTC.confirm("Duplicate a new task ?", "Duplicate task", function(){
        $.ajax({
            type: "post",
            url: "/php/write-db.php",
            async: false,
            data: {
                sql_cmd: "insert into case_cmd_pool(cmd_owner,case_id,dut_type,client_id,create_time,deadline,status) select cmd_owner,case_id,dut_type,client_id,'"+create_time+"','"+deadline_str+"','not run' from case_cmd_pool where id=" + task_id
            },
            beforeSend: function(XMLHttpRequest){
                $("#shade-bg").show();
            },
            success: function(data, textStatus){
                $("#shade-bg").hide();
                duplicateConfigFile(task_id, data);
                window.location.href = window.location.href;
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
}

function init(){
    var table_id = "";
    var item_num = 1;
    if(window.location.href.indexOf("all-task")>-1 || window.location.href.indexOf("my-task")>-1 || window.location.href.indexOf("sbt-task")>-1){
        table_id = "task-list";
        item_num = 11;
    }else if(window.location.href.indexOf("dev-list")>-1){
        table_id = "device_info_list";
        item_num = 13;
    }else if(window.location.href.indexOf("test-result")>-1){
        table_id = "pie_task_list";
        item_num = 10;
    }else if(window.location.href.indexOf("home-overview")>-1){
        table_id = "case_list";
        item_num = 10;
    }else if(window.location.href.indexOf("CI-result")>-1){
        table_id = "task-list";
        item_num = 11;
    }


    $("#"+table_id+" tbody tr").each(function(i,dom){   
        if(i>(item_num-1)){
            $(dom).hide()
        }
    });
    var total_page = Math.ceil(+$(".totalnum").text()/item_num);
    $(".page").remove();
    for(var i=1;i<=5;i++){
        if(i > total_page){
            break;
        }
        if(i==1){
            $("#page-num").append("<span name='1' class='page active'>"+i+"</span>");
        }else{
            $("#page-num").append("<span name='"+i+"' class='page'>"+i+"</span>");
        }
    }
    
    $(".left").click(function(){
        if($(".page.active").text() == "1"){
            return;
        }
        if(total_page>5 && parseInt($(".page[name='5']").text())>5){
            $(".page").each(function(i,dom){
                if($(".page.active").attr("name") == "1"){
                    $(dom).text(String(parseInt($(dom).text())-1))
                }
            });
        }
        $(".page").each(function(i,dom){
            if($(dom).text() == String(parseInt($(".page.active").text())-1)){
                $(".page.active").removeClass("active");
                $(dom).addClass("active");
                return false;
            }
        });
        var pn = parseInt($(".page.active").text());
        $("#"+table_id+" tbody tr").each(function(i,dom){   
            if(i<pn*item_num && i>=pn*item_num-item_num){
                $(dom).show();
            }else{
                $(dom).hide();
            }
        });
        //alert('page left click ' + pn);
        if (table_id == "task-list"){   
            getTaskData_All(json_result, (pn-1)*item_num, pn*item_num-1);
        }
        
    });
    
    $(".right").click(function(){
        if($(".page.active").text() == String(total_page)){
            return;
        }
        if(total_page>5 && parseInt($(".page[name='1']").text())>=1){
            $(".page").each(function(i,dom){
                if($(".page.active").attr("name") == "5"){
                    $(dom).text(String(parseInt($(dom).text())+1))
                }
            });
        }
        $(".page").each(function(i,dom){
            if($(dom).text() == String(parseInt($(".page.active").text())+1)){
                $(".page.active").removeClass("active");
                $(dom).addClass("active");
                return false;
            }
            });
            var pn = parseInt($(".page.active").text());
            $("#"+table_id+" tbody tr").each(function(i,dom){   
                if(i<pn*item_num && i>=pn*item_num-item_num){
                    $(dom).show();
                }else{
                    $(dom).hide();
                }
            });
        //alert('page right click ' + pn);
        if (table_id == "task-list"){
            getTaskData_All(json_result, (pn-1)*item_num, pn*item_num-1);
        }
        });
    
    $(".page").click(function(){
        var pn = parseInt($(this).text());
        $(".page.active").removeClass("active");
        $(this).addClass("active");
        $("#"+table_id+" tbody tr").each(function(i,dom){   
            if(i<pn*item_num && i>=pn*item_num-item_num){
                $(dom).show();
            }else{
                $(dom).hide();
            }
        });
        //alert('page click ' + pn);
        if (table_id == "task-list"){
            getTaskData_All(json_result, (pn-1)*item_num, pn*item_num-1);
        }

    });
    
    $(".jump").click(function(){
        var pn = parseInt($(".page_no input").val());
        if(pn){
            if( pn < 1){
                    pn = 1;
            }else if( pn > total_page){
                    pn = total_page;
            }
            if(pn>5){
                $(".page[name='1']").text(parseInt(pn)-4);
                $(".page[name='2']").text(parseInt(pn)-3);
                $(".page[name='3']").text(parseInt(pn)-2);
                $(".page[name='4']").text(parseInt(pn)-1);
                $(".page[name='5']").text(parseInt(pn));
            }else{
                for(var i=1;i<=5;i++){
                    $(".page[name='"+i+"']").text(String(i));
                }   
            }
            $(".page.active").removeClass("active");
            $(".page").each(function(i,dom){
                if($(dom).text() == pn){
                    $(dom).addClass("active");
                }
            });
            $(".page").each(function(i,dom){
                if($(dom).text() == pn){
                    $(dom).addClass("active");
                }
            });
            $("#"+table_id+" tbody tr").each(function(i,dom){   
            if(i<pn*item_num && i>=pn*item_num-item_num){
                $(dom).show();
            }else{
                $(dom).hide();
            }
        });
        }
      //alert('page jump ' + pn);
      if (table_id == "task-list"){
            getTaskData_All(json_result, (pn-1)*item_num, pn*item_num-1);
      }

    });
}
function getDeviceList() {
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "(select * from conn_info where status != 'invalid' and start_time > '2015-12-31' order by id desc) order by status"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json = eval('(' + data + ')');
            var rows = getDeviceData(json);
            var rows_des = new Array();
            var rows_dup = new Array();
            for(var i=0;i<rows.length;i++){
                /*
                var device_ip = rows[i]["device_ip"];
                var status = rows[i]["status"];
                if($.inArray(device_ip, rows_dup)==-1){
                    rows_des.push(rows[i]);
                    rows_dup.push(device_ip);
                }
                */
                var mac_addr = rows[i]["mac_addr"];
                if (mac_addr == "NULL" || mac_addr == "unknown" || mac_addr == null){continue;}
                if($.inArray(mac_addr, rows_dup)==-1){
                    rows_des.push(rows[i]);
                    rows_dup.push(mac_addr);
                }

            }
            $('#device_info_list').datagrid({striped:$(this).is(':checked'), loadFilter:pagerFilter, selectOnCheck:$(this).is(':checked'), singleSelect:(this.value==0)}).datagrid('loadData', rows_des);
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

function indexof(arr, value){
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] == value) {
            return i;
        }
    }
    return -1;
}


function GetSelectStr(name, id, values, value, select_id){
    if (name == undefined || id== undefined || values == undefined || value == undefined || id == undefined){
        alert("Create Select failed! invalid input parameter.\r\nname:"+name+"\r\nid:"+id+"\r\nvalues:"+values+"\r\nvalue:"+value+"\r\nselect_id:"+select_id);
    }

    if (indexof(values, value) == -1){
        value = values[0];
    }
    //values.reverse();
    select_str = "<tr><td class='item' >"+name+":</td>";
    select_str += "<td><div class='select select"+select_id+"' id='"+id+"' >";
    select_str += "<div class='selected' value='"+value+"'>"+value+"</div>";
    select_str += "<div class='selectHandler'><i class='caret'></i></div><ul class='options' style='margin-left:0px;'>";
    for (var i = 0; i <values.length; i++){
         select_str += "<li class='option' value='"+values[i]+"'>"+values[i]+"</li>";
    }
    select_str += "</ul></div></td></tr>";
    return select_str;
}


function indexof(arr, value){
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] == value) {
            return i;
        }
    }
    return -1;
}

function GetSelectStr(name, id, values, value, select_id){
    if (name == undefined || id== undefined || values == undefined || value == undefined || id == undefined){
        alert("Create Select failed! invalid input parameter.\r\nname:"+name+"\r\nid:"+id+"\r\nvalues:"+values+"\r\nvalue:"+value+"\r\nselect_id:"+select_id);
    }

    if (indexof(values, value) == -1){
        value = values[0];
    }
    //values.reverse();
    select_str = "<tr><td class='item' >"+name+":</td>";
    select_str += "<td><div class='select select"+select_id+"' id='"+id+"' >";
    select_str += "<div class='selected' value='"+value+"'>"+value+"</div>";
    select_str += "<div class='selectHandler'><i class='caret'></i></div><ul class='options' style='margin-left:0px;'>";
    for (var i = 0; i <values.length; i++){
         select_str += "<li class='option' value='"+values[i]+"'>"+values[i]+"</li>";
    }
    select_str += "</ul></div></td></tr>";
    return select_str;
}

function addVersionlist(name, name_id, names_arr, name_default){
    var versions = GetSelectStr(name, name_id, names_arr, name_default, 6);
    $("#config_table").append(versions);
    new MTC.select({"selector":"select6"});

}
function AddClientID(client_id){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >Client ID:</td><td><input disabled='disabled' type='text' id='client_id' value='"+client_id+"'></input></td></tr>");
}
function AddDutType(dut_type){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >DUT type:</td><td><input disabled='disabled' type='text' id='dut_type' value='"+dut_type+"'></input></td></tr>");
}


function Upgrade(client_id, dut_type){
    $.ajax({
        type: "post",
          url: "/php/read-dir_new2.php",
          async: false,
          data: {
              src_path: "/mnt/external/Image_from_SBT"    
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){      
            json_result = eval('(' + data + ')');
            var names_arr = new Array();
            for(var i=0;i<json_result.length;i++){
                names_arr.push(json_result[i]);
            }
            names_arr.sort();
            names_arr.reverse();
            MTC.Upgrade();
            addVersionlist("SBT version", "sbt_ver", names_arr, "undefined");
            AddClientID(client_id);
            AddDutType(dut_type);
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
function Patch(client_id, dut_type){
    alert(client_id);alert(dut_type);
}
function getDeviceData(json_array){
    var rows = new Array();
    for(var i=0; i<json_array.length; i++){
        var client_id = json_array[i]["client_id"];
        var device_ip = json_array[i]["client_ip"];
        var owner = json_array[i]["owner"];
        var owner_info = "<a href='mailto:"+owner+"@marvell.com'>"+owner+"</a>";
        var dut_type = json_array[i]["dut_type"];
        var sw_version = json_array[i]["sw_version"];
        if(sw_version != null){
            sw_version = sw_version.replace(/0x20/gi, " ");
        }
        sw_version = '<a href="javascript:void(0)" onclick="Upgrade('+client_id+", '"+dut_type+"'"+')">'+sw_version+'</a>';
        var start_time = json_array[i]["start_time"];
        var status = json_array[i]["status"];
        var mac_addr = json_array[i]["mac_addr"];
        var status_html = "";
        if(status=="idle"){
            status_html = "<span style='color:#5ab530;font-weight:bold'>idle</span>";
        }else if(status=="busy"){
            status_html = "<span style='color:red;font-weight:bold'>busy</span>";
        }else if(status=="offline"){
            status_html = "<span style='color:dodgerblue;font-weight:bold'>offline</span>";
        }else{
            status_html = "<span style='font-weight:bold'>dead</span>";
        }
        var action = "<a id='upgrade' class='k-button' href='javascript:Upgrade("+client_id+', "'+dut_type+'"' + ")'><span class='k-icon k-upgrade'></span></a>";
        action += "<a id='patch' class='k-button' href='javascript:Patch("+client_id+', "'+dut_type+'"' + ")'><span class='k-icon k-patch'></span></a>";
        rows.push({
            conn_id: client_id,
            mac_addr: mac_addr,
            device_ip: device_ip,
            owner: owner_info,
            dut_type: dut_type,
            sw_version: sw_version,
            start_time: start_time,
            action: action, 
            status: status_html
        });
    }
    return rows;
}
function genPassrateLineChart(container_id, chart_title, x_categories, seriese_json_data, json_data) {
     $('#'+container_id).highcharts({
        credits: {
                enabled: true,
                href: "http://www.marvell.com",
                text: "Marvell.com"
            },
        chart: {
            type: "line",
            options3d: {
                enabled: true,
                depth: 50
            },
            animation: Highcharts.svg
        },
        title: {
            text: chart_title,
            style: {
                fontWeight: 'bold',
                color: 'royalblue'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        yAxis:{
            title: {
                text: 'Pass rate (%)',
                style: {
                        fontWeight: 'bold'
                    }
                },
            labels: {
              format:"{value} %"                  
            },
            max: 100,
            min: 0
        },
        xAxis: {
            categories: x_categories
        },
        series: [],
        plotOptions: {
            line: {
                connectNulls: true
            },
            column: {
                depth: 50
            },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() {
                            //alert(this.category);
			    getDesResult("","",this.series.name,this.category);
			    $( "#detail_dialog" ).dialog("open");
                            /*var fail_num = total_json_passrate[this.series.name][this.category]['fail_num'];
                            var pass_num = total_json_passrate[this.series.name][this.category]['total_num'] - fail_num;
                            gen_pie_passrate("Components of " + this.category + ' ' + this.series.name, [['Pass',pass_num],['Fail',fail_num]]);
                            $( "#pie_diag1" ).dialog( "open" );  */
                        }
                    }
                }
            }
        },
        tooltip: {
	    valueSuffix: ' %'
	}
    });
    var chart = $('#'+container_id).highcharts();
    for(var case_key in seriese_json_data){
        chart.addSeries({
            name: case_key,
            data: seriese_json_data[case_key][1]
        });
    }
}

function genTrend(mysql_cmd, container_id, chart_title, y_des, point_des, x_categories, seriese_json_data, max_bugnum) {
     $('#'+container_id).highcharts({
        credits: {
                enabled: true,
                href: "http://www.marvell.com",
                text: "Marvell.com"
            },
        chart: {
            //type: "line",
            type: "spline",
            options3d: {
                enabled: true,
                depth: 50
            },
            animation: Highcharts.svg
        },
        title: {
            text: chart_title,
            style: {
                fontWeight: 'bold',
                color: 'royalblue'
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        yAxis:{
            title: {
                text: y_des,
                style: {
                        fontWeight: 'bold'
                    }
                },
            labels: {
              format:"{value}"
            },
            max: max_bugnum,
            min: 0
        },

        xAxis: {
            //categories: x_categories
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            }
        },
        series: [],
        plotOptions: {
            line: {
                connectNulls: true
            },
            column: {
                depth: 50
            },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() {
                            getDetail(mysql_cmd, this.category);
                            $( "#casedetail_dialog" ).dialog("open");
                        }
                    }
                }
            }
        },
        tooltip: {
            valueSuffix: point_des,
        }
    });
    var chart = $('#'+container_id).highcharts();
    for(var case_key in seriese_json_data){
        chart.addSeries({
            name: case_key,
            data: seriese_json_data[case_key]
        });
    }
}



function genPieChart(container_id, chart_title, data, series_name){
    var data_labels;
    if(window.location.href.indexOf("home-overview")>-1){
	data_labels = {enabled: false};
    }else{
	data_labels = {
			enabled: true,
			format: "<b>{point.name}</b><br>"+series_name+": {point.y}",
			connectorColor: '#000000',
			color: '#000000'
		    };
    }
    $('#'+container_id).highcharts({
        credits: {
                enabled: true,
                href: "http://www.marvell.com",
                text: "Marvell.com"
            },
        chart: {
            type: 'pie',
            options3d: {
                enabled: true,
                alpha: 45,
                beta: 0
            }
        }, 
        title: {
            text: chart_title,
            margin: -45,
            y: 25,
            style: {
                fontWeight: 'bold',
                color: 'royalblue',
                fontSize: "20px"
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },
        series: [{
            name: series_name,
            data: data
        }],
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                depth: 35,
                dataLabels: data_labels,
                pointPlacement: 'between',
                showInLegend: true
            },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() {
                            if(window.location.href.indexOf("test-result")>-1){
                                if(window.location.href.indexOf("overview")>-1){
                                getDesResult(this.name.toLowerCase(),"","","");
                                }else if(window.location.href.indexOf("case-dist")>-1){
                                    getDesResult("",this.name,"","");
                                }
                                $( "#detail_dialog" ).dialog("open");
                            }else if(window.location.href.indexOf("home-overview")>-1){
                                //
                            }
                        }
                    }
                }
            }
        }
    });
}

function genCaseDetail(p_case_type, p_dut_type){
    var x_list = new Array(), y_list = new Array(), data = new Array();
    var json_fixed = json_result;
    var case_name, case_type, dut_type, create_time, description, status_des;

    var case_dist_json = {};
    var duttype_dist_json = {};
    var casetype_dist_json = {};
    for(var i=0;i<json_fixed.length;i++){
        case_type = json_fixed[i]["case_type"];
        dut_type = json_fixed[i]["dut_type"];
        case_name = json_fixed[i]["case_name"];
        
        if (duttype_dist_json[dut_type] ==  undefined){
            duttype_dist_json[dut_type] = 1;
        }

        if (p_case_type != case_type){
            continue;
        }
        if(case_dist_json[case_name] == undefined){
            case_dist_json[case_name] = {};
        }
        if (case_dist_json[case_name][dut_type] == undefined){
            case_dist_json[case_name][dut_type] = 1;
        }

    }

    x = 0;
    for (var case_name in case_dist_json){
       x_list.push(case_name);
       y = 0;
       for (var dut_type in duttype_dist_json){
           if (case_dist_json[case_name][dut_type] == undefined){
               data.push([x, y, 0]);
           }
           else{
               data.push([x, y, 1]);
           }
           y += 1;
       }
       x += 1;
    }
    for (var dut_type in duttype_dist_json){
        y_list.push(dut_type);
    }


   
    genMapChart("result-chart", p_case_type + " coverage in " + p_dut_type, x_list, y_list, data, "", "http://debutrac.marvell.com/trac/SQA/wiki/");
}

function genMapChart(container_id, chart_title, x_list, y_list, data, series_name, cellclick_returnval){
    var data_labels = {
                enabled: true,
                color: 'black',
                style: {
                    textShadow: 'none',
                    HcTextStroke: null
                }
            };
    $('#'+container_id).highcharts({
        credits: {
                enabled: true,
                href: "http://www.marvell.com",
                text: "Marvell.com"
            },

        chart: {
            type: 'heatmap',
            marginTop: 40,
            marginBottom: 40
        },


        title: {
            text: chart_title
        },

        xAxis: {
            categories: x_list
        },

        yAxis: {
            categories: y_list,
            title: null
        },

        colorAxis: {
            min: 0,
            minColor: '#FFFFFF',
            maxColor: Highcharts.getOptions().colors[0]
        },

        legend: {
            align: 'right',
            layout: 'vertical',
            margin: 0,
            verticalAlign: 'top',
            y: 25,
            symbolHeight: 420
        },

        tooltip: {
            formatter: function () {
                return '<b>' + this.series.xAxis.categories[this.point.x] + '</b> implemented <br><b>' +
                    this.point.value + '</b> cases on <br><b>' + this.series.yAxis.categories[this.point.y] + '</b>';
            }

        },

        series: [{
            name: series_name,
            borderWidth: 1,
            data: data,
            dataLabels: data_labels,

            point: {
                    events: {
                        click: function(e) {
                                if (cellclick_returnval == undefined){
                                    window.location.replace("case-coverage.html?pname=detail&case_type="+this.series.xAxis.categories[e.point.x]+"&dut_type="+this.series.yAxis.categories[e.point.y]);
                                }
                                else{
                                    href = cellclick_returnval + this.series.xAxis.categories[e.point.x];                              }
                                    window.open(href,'newCaseDocument',"fullscreen=1");
                            }
                        }
                    }


        }]
    });

}
function getDesResult(des_result,des_case_type,desc_case_name,des_date_range){
    var json_fixed = getFixedResultData(json_result)[0];
    $("#pie_task_list tbody").empty();
    var cnt = 0;
    for(var i=0;i<json_fixed.length;i++){
        var case_name = json_fixed[i]["name"];
	if(desc_case_name!="" && case_name != desc_case_name){continue;}
        var case_type = json_fixed[i]["case_type"];
        if(des_case_type!="" && case_type != des_case_type){continue;}
        var dut_type = json_fixed[i]["dut_type"];
        var sw_version = json_fixed[i]["sw_version"];
        if(sw_version.length>50){
            sw_version = sw_version.substring(0,50) + " ...";
        }
        var owner = json_fixed[i]["cmd_owner"];
        var start_time = json_fixed[i]["start_time"];
        var end_time = json_fixed[i]["end_time"];
	if(start_time.indexOf(des_date_range)==-1){continue;}
        var result = json_fixed[i]["result"];
        if(result != null){
            result = result.toLowerCase();
        }
        if(des_result!="" && result != des_result){continue;}
        $("#pie_task_list tbody").append("<tr><td>"+case_name+"</td><td>"+dut_type+"</td><td>"+sw_version+"</td><td>"+owner+"</td><td>"+start_time+"</td><td>"+end_time+"</td><td>"+result+"</td></tr>");
        cnt ++;
    }
    $(".totalnum").text(cnt);
    init();
}
function getDetail(mysql_cmd, day){
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: mysql_cmd
            //sql_cmd: "select * from case_info where dut_type != 'gtvv4_4k' and dut_type != 'gtvv4_cedar' and dut_type != 'gtvv4_bg2' and dut_type != 'gtv_bat' and dut_type != 'jellybean' and dut_type != 'ics' and dut_type != 'gtvv4_willow' and dut_type != 'bg2q4k' and dut_type != 'LinuxRDK'"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            json_result = eval('(' + data + ')');
            var casedetail_array = new Array();
            var caseid_array = new Array();
            var json_tmp;
            if (json_result.length == 0){
                alert("no case find in case_info ");
                return;
            }
            
            $("#case_list thead").empty();
            var head_str = "<tr>";
            var body_str = "";
            for (var key_name in json_result[0]){
                head_str += "<td>" + key_name + "</td>";
            }
            head_str += "</tr>";
            $("#case_list thead").append(head_str);
            
            $("#case_list tbody").empty();
            for(var i=0;i<json_result.length;i++){
                var date_tmp = json_result[i]['create_time'];
                json_tmp = json_result[i];
                if(date_tmp == null || date_tmp.indexOf('-') == -1){
                    continue;
                }
                var sDate = date_tmp.split(' ')[0].split('-');
                var TimeMS = new Date(sDate[0], sDate[1]-1, sDate[2]).getTime();
                var case_id = json_result[i]["id"];
                if(case_id == null || case_id == 'null' || $.inArray(case_id, caseid_array) != -1){
                    continue;
                }
                //alert(day);
                if (TimeMS == day){
                    casedetail_array.push(json_result);
                    caseid_array.push(case_id);
                    body_str = "<tr>";
                    for (var key_name in json_tmp)
                    {
                        body_str += "<td>";
                        if (json_tmp[key_name] != null && json_tmp[key_name].length > 16){
                            body_str += "<span name='sw_tooltip' title='"+json_tmp[key_name]+"'>"+json_tmp[key_name].substring(0,19)+" ..."+"</span>";
                        }
                        else {
                            body_str += json_tmp[key_name];
                        }
                        body_str += "</td>";
                    }
                    body_str += "</tr>";
                    $("#case_list tbody").append(body_str);
                }
            }
            $(".totalnum").text(casedetail_array.length);
            init();
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
function getTrendDetail(){
    var cnt = 0;
    $("#pie_task_list tbody").empty();
    $(".totalnum").text(cnt);
    init();
}

var json_result;
function getResultInfo(start_idx, end_idx){
    var constraint;
    if(arguments.length==0){
        constraint = "";
    }else{
        constraint = arguments[0];
    }
    if(window.location.href.indexOf("my")>-1){
        constraint += " and a.cmd_owner='"+getCookie('username')+"'";
    }
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
//            sql_cmd: "select distinct case_cmd_pool.id,conn_info.client_ip,case_id,name,case_type,cmd_owner,case_cmd_pool.dut_type,case_cmd_pool.sw_version,case_cmd_pool.create_time,case_cmd_pool.start_time,case_cmd_pool.end_time,case_cmd_pool.status,result,bugid,case_cmd_pool.reserved \
//                    from case_cmd_pool,case_info,conn_info \
//                    where case_cmd_pool.case_id=case_info.id and case_cmd_pool.exc_client_id=conn_info.client_id" + constraint + " group by case_cmd_pool.id order by id desc"
              sql_cmd: "select a.id, c.client_ip, a.case_id, b.name, b.case_type, a.cmd_owner, a.dut_type, a.sw_version, a.create_time, a.start_time, a.end_time, a.status, a.result, a.bugid, a.reserved, c.client_pcname from case_cmd_pool as a, case_info as b, (select * from (select * from conn_info order by id desc) cc group by cc.client_id) c where a.case_id=b.id and a.exc_client_id=c.client_id" + constraint + " order by a.id desc"

        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            json_result = eval('(' + data + ')');
            if(window.location.href.indexOf("task-management")>-1){
                getTaskData_All(json_result, start_idx, end_idx);
            }else if(window.location.href.indexOf("test-result")>-1){
                addDutTypeList();
                addMutipleCaseList();
                addSWInfoList();
            }else{
               //do pass
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

function getResultInfo_fromCI(CI_id){
    constraint = "and a.group_id='"+CI_id+"'";

    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
              sql_cmd: "select a.id, c.client_ip, a.case_id, b.name, b.case_type, a.cmd_owner, a.dut_type, a.sw_version, a.create_time, a.start_time, a.end_time, a.status, a.result, a.bugid, a.reserved, c.client_pcname from case_cmd_pool as a, case_info as b, (select * from (select * from conn_info order by id desc) cc group by cc.client_id) c where a.case_id=b.id and a.exc_client_id=c.client_id " + constraint + " order by a.id desc"

        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            json_result = eval('(' + data + ')');
            getTaskData_All(json_result);
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


function addDutTypeList(){
    for(var i=0; i<json_result.length; i++){
        var dut_type = json_result[i]["dut_type"];
        if($("#select_dut_type").find("option[value='"+dut_type+"']").length == 0){
            $("#select_dut_type").append("<option selected='selected' value='"+dut_type+"'>&nbsp;&nbsp;"+dut_type+"</option>");
        }
    }
    $("#select_dut_type").multiselect({selectedText:"DUT type",classes: "myClass",height:"auto",show:"fade",hide:"fade"});
}
function addSWInfoList(){
    for(var i=0;i<json_result.length;i++){
        var sw_version = json_result[i]["sw_version"];
        if($("#select_sw_version").find("option[value='"+sw_version+"']").length == 0){
            $("#select_sw_version").append("<option selected='selected' value='"+sw_version+"'>&nbsp;&nbsp;"+sw_version+"</option>");
        }
    }
    $("#select_sw_version").multiselect({selectedText:"SW version",classes: "myClass",height:"auto",show:"fade",hide:"fade"});
}
function addMutipleCaseList(){
    for(var i=0;i<json_result.length;i++){
        var case_name = json_result[i]["name"];
        if($("#select_case").find("option[value='"+case_name+"']").length == 0){
            $("#select_case").append("<option selected='selected' value='"+case_name+"'>&nbsp;&nbsp;"+case_name+"</option>");
        }
    }
    $("#select_case").multiselect({selectedText:"Mutiple case",classes: "myClass",height:"auto",show:"fade",hide:"fade"});
}

function getConstraint(){   
    var dut_type_cons = new Array();
    var date_cons = new Array();
    var sw_info_cons = new Array();
    var case_cons = new Array();
    //get dut_type constraint
    $("#select_dut_type").multiselect("getChecked").each(function(){
        dut_type_cons.push($(this).val());
    });
    //get day constraint
    var start_day = $("#from").val();
    var end_day = $("#to").val();
    var max_day_tmp = end_day.split("-");
    var min_day_tmp = start_day.split("-");
    var max_day = new Date(max_day_tmp[0], max_day_tmp[1]-1, max_day_tmp[2]);
    var min_day = new Date(min_day_tmp[0], min_day_tmp[1]-1, min_day_tmp[2]);
    date_cons.push(min_day);
    date_cons.push(max_day);
    //get sw_info constraint
    $("#select_sw_version").multiselect("getChecked").each(function(){
        sw_info_cons.push($(this).val());
    });
    //get mutiple_case constraint
    $("#select_case").multiselect("getChecked").each(function(){
        case_cons.push($(this).val());
    });
    return [dut_type_cons, date_cons, sw_info_cons, case_cons];
}
function getFixedResultData(json_data){
    var json_fixed = new Array();
    var cons = getConstraint();
    for(var i=0;i<json_data.length;i++){
        var status = json_data[i]["status"];
        if(status != "finished"){continue}
        var case_name = json_data[i]["name"];
        var cmd_owner = json_data[i]["cmd_owner"];
        var dut_type = json_data[i]["dut_type"];
        var sw_version = json_data[i]["sw_version"];
        var start_time = json_data[i]["start_time"];
        var sDate = start_time.split(' ')[0].split("-");
        var start_time_fixed = new Date(sDate[0], sDate[1]-1, sDate[2]);
        var end_time = json_data[i]["end_time"];
        var result = json_data[i]["result"];
        var bugid = json_data[i]["bugid"];
        if($.inArray(dut_type, cons[0])>-1 && (start_time_fixed>=cons[1][0] && start_time_fixed<=cons[1][1]) && $.inArray(sw_version, cons[2])>-1 && $.inArray(case_name, cons[3])>-1){
            json_fixed.push(json_data[i]);
        }
    }
    return [json_fixed, cons];
}
function getOverTrendData(start_day, end_day){
    var json_fixed;
    var chart_title = "Test Result Distribution On Projects";
    if(window.location.href.indexOf("test-result")>-1){
        json_fixed = getFixedResultData(json_result)[0];
    }else if(window.location.href.indexOf("home-overview")>-1){
        json_fixed = json_result;
        chart_title = "Test Result from " + start_day + " to " + end_day;
    }
    var pass_num = 0;
    var fail_num = 0;
    var error_num = 0;
    for(var i=0;i<json_fixed.length;i++){
        var test_status = json_fixed[i]["status"];
        var test_result = json_fixed[i]["result"];
        if(test_result != null){
            test_result = test_result.toLowerCase();
        }
        if(test_status != "finished"){continue}
        if(test_result == 'pass'){
            pass_num++;
        }else if(test_result == 'error'){
            error_num++;
        }else if(test_result == 'failed'){
            fail_num++;
        }
    }
    if((pass_num+error_num+fail_num) == 0){return};
    var des_id = "";
    if(window.location.href.indexOf("test-result")>-1){
        des_id = "result-chart";
    }else if(window.location.href.indexOf("home-overview")>-1){
        des_id = "result_summary";
    }
    if(fail_num != 0){
        genPieChart(des_id, chart_title, [{name:"Pass",y:pass_num,color:"rgb(144, 237, 125)"},{name:"Failed",y:fail_num,color:"rgb(247, 163, 92)"}], "Total num");
    }else{
        genPieChart(des_id, chart_title, [{name:"Pass",y:pass_num,color:"rgb(144, 237, 125)"},{name:"Failed",y:fail_num,color:"rgb(247, 163, 92)"},{name:"Error",y:error_num,color:"rgb(92, 92, 97)"}], "Total num");
    }
}
function getCaseDistData(){
    var json_fixed = getFixedResultData(json_result)[0];
    var case_dist_json = {};
    for(var i=0;i<json_fixed.length;i++){
        var test_status = json_fixed[i]["status"];
        if(test_status != "finished"){continue}
        var result = json_fixed[i]["result"];
        if(result != null){
            result = result.toLowerCase();
        }
        var case_type = json_fixed[i]["case_type"];
        if(case_dist_json[case_type] == undefined){
            case_dist_json[case_type] = 1;
        }else{
            case_dist_json[case_type]++;
        }
    }
    var data = new Array();
    for(var key in case_dist_json){
        data.push([key, case_dist_json[key]]);
    }
    genPieChart("result-chart", "Case Cover Rate On Projects", data, "Total run");
    
}
function getCaseDistData_extend(){
    
    var json_fixed = json_result;
    var case_dist_json = {};
    var duttype_dist_json = {};
    var casetype_dist_json = {};
    for(var i=0;i<json_fixed.length;i++){
        var case_type = json_fixed[i]["case_type"];
        var dut_type = json_fixed[i]["dut_type"];
        var case_name = json_fixed[i]["case_name"];
        if(case_dist_json[case_type] == undefined){
            case_dist_json[case_type] = {};
        }
        if (case_dist_json[case_type][dut_type] == undefined){
            case_dist_json[case_type][dut_type] = 1;
        }
        else{
            case_dist_json[case_type][dut_type] += 1;
        }

        if (duttype_dist_json[dut_type] ==  undefined){
            duttype_dist_json[dut_type] = 1;
        }
        if (casetype_dist_json[case_type] ==  undefined){
            casetype_dist_json[case_type] = 1;
        }
        else{
            casetype_dist_json[case_type] += 1;
        }

    }
    var data = new Array();
    var x_list = new Array();
    var y_list = new Array();
    var x=0, y=0, case_cnt=0;
    //x_list = ["xa", "xb", "xc"];
    //y_list = ["ya", "yb", "yc", "yd"];
    //data = [[0, 0, 1], [0, 1, 3], [0, 2, 12], [0, 3, 22], [1, 0, 1], [1, 1, 3], [1, 2, 12], [1, 3, 22], [2, 0, 1], [2, 1, 3], [2, 2, 12], [2, 3, 22]];
    
    for (var case_type in case_dist_json){
       x_list.push(case_type);
       y = 0;
       for (var dut_type in duttype_dist_json){
           if (case_dist_json[case_type][dut_type] == undefined){
               data.push([x, y, 0]);
           }
           else{
               var tmp = case_dist_json[case_type][dut_type];
               //tmp = (tmp*10/3).toFixed(2);
               data.push([x, y, tmp]);
               case_cnt += tmp;
           }
           y += 1;
       }
       x += 1;
    }
    for (var dut_type in duttype_dist_json){
        y_list.push(dut_type);
    }

    //genPieChart("result-chart", "Case Cover Rate On Projects", data, "Total run");
    genMapChart("result-chart", case_cnt + " cases coverage in " + y_list.length +  " projects", x_list, y_list, data, "");

}

function getQualityData(){
    var cons_json_fixed = getFixedResultData(json_result);
    var start_date = cons_json_fixed[1][1][0];
    var end_date = cons_json_fixed[1][1][1];
    var json_fixed = cons_json_fixed[0];
    var categories_arr = new Array();
    for(var day=start_date;day<=end_date;day=new Date(day.setDate(day.getDate() + 1))){
        categories_arr.push(stamp_format(day, "YY-MM-dd"));
    }
    var series_json_data = new Array();
    //step1: init totally passrate json 
    var passrate_json = {};
    for(var i=0;i<json_fixed.length;i++){
        var test_status = json_fixed[i]["status"];
        var case_name = json_fixed[i]["name"];
        var test_result = json_fixed[i]["result"];
        if(test_result != null){
            test_result = test_result.toLowerCase();
        }
        if(test_status != "finished" || test_result == "error"){continue}
        var date_json = {};
        for(var j=0;j<categories_arr.length;j++){
            var cnt_json = {};
            cnt_json['pass_num'] = 0;
            cnt_json['fail_num'] = 0;
            var str_day = categories_arr[j];
            date_json[str_day] = cnt_json;
        }
        passrate_json[case_name] = date_json;
    }
    //step2: fill totally passrate json data
    for (var i=0;i<json_fixed.length;i++) {
        var test_status = json_fixed[i]["status"];
        var case_name = json_fixed[i]["name"];
        var test_result = json_fixed[i]["result"];
        if(test_result != null){
            test_result = test_result.toLowerCase();
        }
        if(test_status != "finished" || test_result == "error"){continue}
        var start_day = json_fixed[i]["start_time"].split(' ')[0];
        for (var time_key in passrate_json[case_name]) {
            if(start_day == time_key){
                if(test_result == "pass"){
                    passrate_json[case_name][start_day]['pass_num']++;
                }else{
                    passrate_json[case_name][start_day]['fail_num']++;
                }
            }
        }
    }
    //step3: convert passrate json to highcharts series data
    var series_json = {}    
    for(var case_key in passrate_json){
        var a_arix = new Array();
        var pass_arr = new Array();
        for(var time_key in passrate_json[case_key]){
            a_arix.push(time_key);
            var pass_num = passrate_json[case_key][time_key]['pass_num'];
            var fail_num = passrate_json[case_key][time_key]['fail_num'];
            if(pass_num> 0 || fail_num> 0){
                var pass_rate = pass_num/(pass_num+fail_num);
                pass_arr.push(number_format(pass_rate*100,3));
            }
            else{
                pass_arr.push(null);
            }
        }    
        series_json[case_key] = [a_arix,pass_arr];
    }
    //step4: generate passrate line chart
    genPassrateLineChart("result-chart", "Case Passrate Trend On Projects", categories_arr, series_json, passrate_json);
}


function getBugTrend() {
    var mysql_cmd =  "select a.id, b.name, b.case_type, a.cmd_owner, a.dut_type, a.sw_version, a.create_time, a.start_time, a.result, a.bugid, a.reserved from case_cmd_pool as a, case_info as b, (select * from (select * from conn_info order by id desc) cc group by cc.client_id) c where a.case_id=b.id and a.exc_client_id=c.client_id and a.bugid != 0 order by a.id desc";
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: mysql_cmd
            //sql_cmd: "select a.id, c.client_ip, a.case_id, b.name, b.case_type, a.cmd_owner, a.dut_type, a.sw_version, a.create_time, a.start_time, a.end_time, a.status, a.result, a.bugid, a.reserved from case_cmd_pool as a, case_info as b, (select * from (select * from conn_info order by id desc) cc group by cc.client_id) c where a.case_id=b.id and a.exc_client_id=c.client_id order by a.id desc"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            json_result = eval('(' + data + ')');
            var now = new Date();
            var end_date = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
            var start_date = new Date().setTime(end_date - 2678400000);
 
            
            var categories_date = new Array();
            var bugid_array = new Array();
            for(var day=start_date;day<=end_date;day+=86400000){
                categories_date.push(stamp_format(day, "YY-MM-dd"));
            }
            var bugs_created_start = 0;
            for(var i=0;i<json_result.length;i++){
                var date_tmp = json_result[i]['start_time'];
                if(date_tmp == null || date_tmp.indexOf('-') == -1){
                    continue;
                }
                var bug_id = json_result[i]["bugid"];
                //if (bug_id == "7927"){alert(date_tmp)};
                if(bug_id == null || bug_id == 'null' || bug_id == '0'){
                    continue;
                }

                var sDate = date_tmp.split(' ')[0].split("-");
                var date_fixed_tmp = new Date(sDate[0], sDate[1]-1, sDate[2]);
                if (date_fixed_tmp.getTime() < start_date ){
                    if ($.inArray(bug_id, bugid_array) != -1){ continue;}
                    bugs_created_start += 1;
                    bugid_array.push(bug_id);
                    //if (bug_id == "7927"){alert(bug_id);}
                }
            }
            
            //alert(bugid_array.sort());
            var series_createbug_data = new Array();
            var bugs_created_last = -1;
            for(var day=start_date;day<=end_date;day+=86400000){
                for(var i=0;i<json_result.length;i++){
                    var date_tmp = json_result[i]['start_time'];
                    if(date_tmp == null || date_tmp.indexOf('-') == -1){
                        continue;
                    }

                    var sDate = date_tmp.split(' ')[0].split("-");
                    var date_fixed_tmp = new Date(sDate[0], sDate[1]-1, sDate[2]);
                    if (date_fixed_tmp.getTime() < start_date ){
                        continue;
                    }

                    var bug_id = json_result[i]["bugid"];
                    if(bug_id == null || bug_id == 'null' || bug_id == '0' || $.inArray(bug_id, bugid_array) != -1){
                        continue;
                    }
                    if (date_fixed_tmp.getTime() == day ){
                        bugs_created_start += 1;
                        bugid_array.push(bug_id);
                    }
                }
                if (bugs_created_last != bugs_created_start){
                    series_createbug_data.push([day, bugs_created_start]);
                    bugs_created_last = bugs_created_start;
                }
            }
            var series_json = {};
            mysql_cmd =  "select a.id, b.name, b.case_type, a.cmd_owner, a.dut_type, a.sw_version, a.create_time, a.result, a.bugid, a.reserved from case_cmd_pool as a, case_info as b, (select * from (select * from conn_info order by id desc) cc group by cc.client_id) c where a.case_id=b.id and a.exc_client_id=c.client_id and a.bugid != 0 order by a.id desc";
            series_json['created'] = series_createbug_data;
            genTrend(mysql_cmd, "bug_trend", "Issues: 30 Day Summary", "Bug Num", " bugs", categories_date, series_json, bugs_created_start);
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

function getCaseTrend() {
    var mysql_cmd =  "select * from case_info where dut_type != 'gtvv4_4k' and dut_type != 'gtvv4_cedar' and dut_type != 'gtvv4_bg2' and dut_type != 'gtv_bat' and dut_type != 'jellybean' and dut_type != 'ics' and dut_type != 'gtvv4_willow' and dut_type != 'bg2q4k' and dut_type != 'LinuxRDK'";
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: mysql_cmd
            //sql_cmd: "select id, name, path, dut_type, description, reserved, create_time, case_type from case_info where dut_type != 'gtvv4_4k' and dut_type != 'gtvv4_cedar' and dut_type != 'gtvv4_bg2' and dut_type != 'gtv_bat' and dut_type != 'jellybean' and dut_type != 'ics' and dut_type != 'gtvv4_willow' and dut_type != 'bg2q4k' and dut_type != 'LinuxRDK'"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            json_result = eval('(' + data + ')');
            var now = new Date();
            var end_date = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
            var start_date = new Date().setTime(end_date - 2678400000);


            var categories_date = new Array();
            var caseid_array = new Array();
            for(var day=start_date;day<=end_date;day+=86400000){
                categories_date.push(stamp_format(day, "YY-MM-dd"));
            }
            var cases_created_start = 0;
            for(var i=0;i<json_result.length;i++){
                var date_tmp = json_result[i]['create_time'];
                if(date_tmp == null || date_tmp.indexOf('-') == -1){
                    continue;
                }
                var case_id = json_result[i]["id"];
                if(case_id == null || case_id == 'null'){
                    continue;
                }

                var sDate = date_tmp.split(' ')[0].split("-");
                var date_fixed_tmp = new Date(sDate[0], sDate[1]-1, sDate[2]);
                if (date_fixed_tmp.getTime() < start_date ){
                    if ($.inArray(case_id, caseid_array) != -1){ continue;}
                    cases_created_start += 1;
                    caseid_array.push(case_id);
                }
            }
            var series_createcase_data = new Array();
            var cases_created_last = -1;
            for(var day=start_date;day<=end_date;day+=86400000){
                for(var i=0;i<json_result.length;i++){
                    var date_tmp = json_result[i]['create_time'];
                    if(date_tmp == null || date_tmp.indexOf('-') == -1){
                        continue;
                    }

                    var sDate = date_tmp.split(' ')[0].split("-");
                    var date_fixed_tmp = new Date(sDate[0], sDate[1]-1, sDate[2]);
                    if (date_fixed_tmp.getTime() < start_date ){
                        continue;
                    }
                    var case_id = json_result[i]["id"];
                  
                    if(case_id == null || case_id == 'null' || $.inArray(case_id, caseid_array) != -1){
                        continue;
                    }
                    if (date_fixed_tmp.getTime() == day){
                        cases_created_start += 1;
                        caseid_array.push(case_id);
                    }
                }
                if (cases_created_start != cases_created_last){
                    series_createcase_data.push([day, cases_created_start]);
                    cases_created_last = cases_created_start;
                }
            }
            var series_json = {};
            series_json['online'] = series_createcase_data;
            genTrend(mysql_cmd, "case_trend", "Cases: 30 Day Summary", "Case Num", " cases", categories_date, series_json, cases_created_start);
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



function getOnlineDeviceDistribution(){
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from conn_info where status != 'offline' and status != 'invalid' and status != 'dead'"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json_arr = eval('(' + data + ')');
            var type_json = {};
            var owner_json = {};
            for(var i=0;i<json_arr.length;i++){
                var dut_type = json_arr[i]["dut_type"];
                var owner = json_arr[i]["owner"];
                if(type_json[dut_type] == undefined){
                    type_json[dut_type] = 1;
                }else{
                    type_json[dut_type]++;
                }
                if(owner_json[owner] == undefined){
                    owner_json[owner] = 1;
                }else{
                    owner_json[owner]++;
                }
            }
            var json_arr = new Array();
            for(var key_type in type_json){
                json_arr.push([key_type, type_json[key_type]]);
            }
            var json_arr1 = new Array();
            for(var key_owner in owner_json){
                json_arr1.push([key_owner, owner_json[key_owner]]);
            }
            genPieChart("device_type_dis", "Online Test Device Distribution", json_arr, "Total num");
            genPieChart("device_owner_dis", "Online Test Device Owner Distribution", json_arr1, "Total devices");
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
function getOnlineCaseTypeDis(){
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from case_info where dut_type != 'gtvv4_4k' and dut_type != 'gtvv4_cedar' and dut_type != 'gtvv4_bg2' and dut_type != 'gtv_bat' and dut_type != 'jellybean' and dut_type != 'ics' and dut_type != 'gtvv4_willow'"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json_arr = eval('(' + data + ')');
            var type_json = {};
            for(var i=0;i<json_arr.length;i++){
                var dut_type = json_arr[i]["dut_type"];
                if(type_json[dut_type] == undefined){
                    type_json[dut_type] = 1;
                }else{
                    type_json[dut_type]++;
                } 
            }
            var json_arr = new Array();
            for(var key_type in type_json){
                json_arr.push([key_type, type_json[key_type]]);
            }
            genPieChart("case_type_dis", "Online Test Case Distribution", json_arr, "Total cases");
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
function getOnlineDeviceDis(){
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select * from conn_info where status != 'dead' and status != 'invalid'"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json_arr = eval('(' + data + ')');
            var online_num = 0;
            var offline_num = 0;
            var offline_arr = new Array();
            for(var i=0;i<json_arr.length;i++){
                var client_id = json_arr[i]["client_id"];
                var status = json_arr[i]["status"];
                if(status == "offline"){
                    if($.inArray(client_id, offline_arr)==-1){
                        offline_num ++;
                        offline_arr.push(client_id);
                    }
                }else{
                    online_num ++;
                    if($.inArray(client_id, offline_arr) != -1){offline_num--;}
                    offline_arr.splice($.inArray(client_id,offline_arr),1);
                }
            }
            //alert(offline_arr);
            genPieChart("online_device_dist", "Online & Offline Test Device Distribution", [["Online",online_num],["Offline",offline_num]], "Total num");
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
function getWorkloadData() {
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select exc_client_id,start_time,end_time from case_cmd_pool where end_time is not null"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json_workload = eval('(' + data + ')');
	    getSystemWorkload(json_workload);
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
function getFixedWorkloadJson(json_workload, chart_title, x_axis, data_arr_online, data_arr_offline) {
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select client_id,mac_addr from conn_info"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            var json_arr = eval('(' + data + ')');
	    var json_workload_fixed = {}
	    for(var i=0;i<json_arr.length;i++){
		var client_id = json_arr[i]["client_id"];
		var mac_addr = json_arr[i]["mac_addr"];
		if(json_workload[client_id] != undefined){
		    json_workload_fixed[mac_addr] = json_workload[client_id];
		}    
	    }
	    gen_chart_workload(json_workload_fixed, chart_title, x_axis, data_arr_online, data_arr_offline);
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
function gen_chart_workload(total_json_workload, chart_title, x_xAxis, online_data, offline_data) {
    var stack_type = "absolute";
    if (stack_type == "percent") {
        var label_format = "%"
        for(var i=0;i<offline_data.length;i++){
                
                offline_data[i] = number_format((offline_data[i] / (online_data[i]+offline_data[i]))*100,3);
                online_data[i] = 100 - offline_data[i];       
        }
    } else {
        var label_format = "hour"
    }
    $('#result-chart').highcharts({
        credits: {
                enabled: true,
                href: "http://www.marvell.com",
                text: "Marvell.com"
                },
        chart: {
            type: "column",
            options3d: {
                enabled: true,
                depth: 50
            }
        },
        title: {
            text: 'Workload of ' + chart_title,
            style: {
                        fontWeight: 'bold',
                        color: 'royalblue'
                }
        },
        xAxis: {
            categories: x_xAxis
        },
        yAxis: {
            title: {
                text: "Workload ("+label_format+")",
                style:{
                    "fontWeight": "bold"
                }
            },
            labels: {
		format:"{value} "+label_format  
            }
        },
        tooltip: {
		valueSuffix: ' '+label_format
	    },
        plotOptions: {
            column: {
                stacking: stack_type,
                depth: 50
            },
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() {
			    //if($('#pc_list option:selected').text() == "All"){
			        var data_array = new Array();
			        for (var key in total_json_workload) {
			            var total_time = total_json_workload[key][this.category];
			            if (total_time > 0) {
			                if (this.series.name == 'busy') {
			                    data_array.push([key, number_format(total_time,3)]);
			                } else if (this.series.name == 'idle') {
			                    total_time = 24 - total_time;
			                    data_array.push([key, number_format(total_time,3)]);
			                }
			            }
			        }
			        gen_pie_workload(this.series.name + " devices of " + this.category , data_array);
			        $( "#pie_diag" ).dialog( "open" );
			    //}
                        }
                    }
                }
            }
        },
        series: [{
            name: 'idle',
            color: 'gray',
            data: offline_data,
            stack: 0
        },
        {
            name: 'busy',
            color: 'green',
            data: online_data,
            stack: 0
        }]
      
    });
}
function gen_pie_workload(title, data) {
    $('#sub_pie_diag').highcharts({
        credits: {
                enabled: true,
                href: "http://www.marvell.com",
                text: "Marvell.com"
            },
        chart: {
            type: 'pie',
            options3d: {
                enabled: true,
                alpha: 45,
                beta: 0
            }
        }, 
        title: {
            text: title,
            style: {
                color: 'royalblue',
                "fontWeight": "bold"
            }
        },
        series: [{
            name: title.split(' ')[title.split(' ').length-1],
            data: data
        }],
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                depth: 35,
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b><br>'+title.split(' ')[0]+':{point.y} hour',
					connectorColor: '#000000',
					color: '#000000'
                }
            },
			series:{
				point:{
					events:{	
						click:function(){
						    //alert('ss');
							  //window.open("show_devices.html?parm="+this.name);
						}
					}
				}
			}
        },
        tooltip: {
	     valueSuffix: ' hour'
	}
    });
}

function getSystemWorkload(json_workload) {
    var total_json_workload = {};
    var date_start = $('#from').val();
    var date_end = $('#to').val();
    var _day_start = new Date(date_start).getTime();
    var _day_end = new Date(date_end).getTime();
    var res_arr = json_workload;

    for (var i = 0; i < res_arr.length; i++) {
        var delta_json = {};
        var client_name = res_arr[i]["exc_client_id"];
        for (var day = _day_start; day <= _day_end; day += 86400000) {
            var str_day = stamp_format(day, "YY-MM-dd");
            delta_json[str_day] = 0;
        }
        if (client_name.length > 0) {
            total_json_workload[client_name] = delta_json;
        }
    }
    for (var i = 0; i < res_arr.length; i++) {
            var client_name = res_arr[i]["exc_client_id"];
            var start_time = res_arr[i]["start_time"];
            var end_time = res_arr[i]["end_time"];
            var c_starttime = start_time.replace(/-/gi, '/').split(' ')[0].split('/');
            var c_endtime = end_time.replace(/-/gi, '/').split(' ')[0].split('/');
            var delta_time = (new Date(c_endtime[1] + '/' + c_endtime[2] + '/' + c_endtime[0] + ' ' + end_time.replace(/-/gi, '/').split(' ')[1]).getTime() - new Date(c_starttime[1] + '/' + c_starttime[2] + '/' + c_starttime[0] + ' ' + start_time.replace(/-/gi, '/').split(' ')[1]).getTime()) / 1000 / 3600;
	    for (var time_key in total_json_workload[client_name]) {
                if (start_time.split(' ')[0] == time_key) {
		    if(delta_time > (24 - total_json_workload[client_name][time_key])){
			delta_time = 24 - total_json_workload[client_name][time_key];
		    }
                    total_json_workload[client_name][time_key] += delta_time;
            }
        }
    }

    var x_axis = new Array();
    var data_arr_online = new Array();
    var data_arr_offline = new Array();
    
    for (var day = _day_start; day <= _day_end; day += 86400000) {
        var data_online = 0;
        var data_offline = 0;
        var key_date = stamp_format(day, 'YY-MM-dd');
        var pc_key = "All";
        if (pc_key == "All") {
            var chart_title = "All platforms";
            for (var key in total_json_workload) {		
		var on_time = total_json_workload[key][key_date];
		if (on_time > 24) {
			on_time = 24;
		}
		var off_time = 24 - on_time;
		if (on_time > 0) {
			data_online += on_time;
			data_offline += off_time;
		}
	    }
        }else {	
            var chart_title = pc_key;
            var on_time = total_json_workload[pc_key][key_date];
            if (on_time > 24) {
                on_time = 24;
            }
            var off_time = 24 - on_time;
            if (on_time > 0) {
                data_online += on_time;
                data_offline += off_time;
            }
        }
        x_axis.push(key_date);
        if(data_online == 0){if(pc_key == "All"){data_offline=120;}else{data_offline=24;}}
        data_arr_online.push(number_format(data_online,3));
        data_arr_offline.push(number_format(data_offline,3));
    }
    getFixedWorkloadJson(total_json_workload, chart_title, x_axis, data_arr_online, data_arr_offline);
}

//timstamp format func
function stamp_format(timestamp, format) {
    var year = new Date(timestamp).getFullYear();
    var month = new Date(timestamp).getMonth() + 1;
    if (month < 10) {
        month = "0" + month;
    }
    var day = new Date(timestamp).getDate();
    if (day < 10) {
        day = "0" + day;
    }
    if (format == "MM/dd/YY") {
        var str_format = month + "/" + day + "/" + year;
    } else if (format == "YY-MM-dd") {
        var str_format = year + "-" + month + "-" + day;
    }
    return str_format;
}
//number format func
function number_format(number,len){
    var num_str = String(number);
    if(num_str.indexOf('.') != -1){
        number = parseFloat(num_str.substring(0,num_str.indexOf('.')+len));
    }
    return number;
}

function get_select(name, value, comments, options, fg_disable, fg_hide){
    if (fg_hide){
        dst_str = "<tr style='display:none'>";
    }
    else{
        dst_str = "<tr>";
    }

    dst_str += "<td class='item' value='"+name+"'>"+name+":</td>";
    dst_str += "<td>";
    if (fg_disable){
        dst_str += '<select class="easyui-combobox" id="item"  disabled="true">';
    }
    else{
        dst_str += '<select class="easyui-combobox" id="item"  >';
    }
    for (var i=0;i<options.length;i++){
        var option_value = options[i].replace(/<\/?.+?>/g,""); 
        option_value = option_value.replace(/[\r\n]/g, ""); 
        if ($.trim(options[i]) == $.trim(value)){
            dst_str += '<option value="'+option_value+'" selected>'+option_value+'</option>';
        }
        else{
            dst_str += '<option value="'+option_value+'">'+option_value+'</option>';
        }

    }
    dst_str += "</select>";

    dst_str += '<a href="#" class="easyui-tooltip" title="'+comments+'"><img src="plugins/jquery-easyui/themes/icons/help.png" align="middle" ></a>';
    dst_str += "</td>";
    //dst_str += "<td><a href='#' title='"+comments+"' class='easyui-tooltip'>?</a></td>";
    dst_str += "</tr>";
    return dst_str;
}
function get_input_text(name, value, comments, fg_disable, fg_hide){
    if (fg_hide){
        dst_str = "<tr style='display:none'>";
    }
    else{
        dst_str = "<tr>";
    }

    dst_str += "<td class='item' value='"+name+"'>";
    dst_str += name+":";
    dst_str += "</td>";

    dst_str += "<td>";
    if (fg_disable){
        dst_str += "<input disabled='true' type='text' value='"+value+"'></input>";
    }
    else{
        dst_str += "<input type='text' value='"+value+"'></input>";
    }
    //dst_str += "<a href='#' title='"+comments+"' class='easyui-tooltip'>?</a>";
    //dst_str += "<div title='"+comments+"' class='easyui-tooltip' iconCls:'icon-help' style='padding:10px'>";
    //dst_str += '<div><a href="#" class="easyui-linkbutton easyui-tooltip" title="Help" iconCls="icon-add"></a></div>';
    dst_str += '<a href="#" class="easyui-tooltip" title="'+comments+'"><img src="plugins/jquery-easyui/themes/icons/help.png" ></a>';
    dst_str += "</td>";

    dst_str += "</tr>";
    return dst_str;
}
function get_input_int(name, value, comments, min, max, fg_disable, fg_hide){
    if (fg_hide){
        dst_str = "<tr style='display:none'>";
    }
    else{
        dst_str = "<tr>";
    }

    dst_str += "<td class='item' value='"+name+"'>";
    dst_str += name+":";
    dst_str += "</td>";



    dst_str += "<td>";
    if (fg_disable){
        dst_str += "<input disabled='true' type='number' value='"+value+"' min='"+min+"' max='"+max+"'></input>";
    }
    else{
        dst_str += "<input type='number' value='"+value+"' min='"+min+"' max='"+max+"'></input>";
    }
    //dst_str += "<a href='#' title='"+comments+"' class='easyui-tooltip'>?</a>";
    //dst_str += "<div title='"+comments+"' class='easyui-tooltip' iconCls:'icon-help' style='padding:10px'>";
    //dst_str += '<div><a href="#" class="easyui-linkbutton easyui-tooltip" title="Help" iconCls="icon-add"></a></div>';
    //dst_str += '<a href="#" class="easyui-tooltip" title="'+comments+'"><img src="plugins/jquery-easyui/themes/icons/help.png" ></a>';
    dst_str += "</td>";

    dst_str += "</tr>";
    return dst_str;
}

