
function UpdateSelf(){
        var customizecase_type = $("#customize_type").find('.selected').attr("value");

        var project_name = $("#project_name").find('.selected').attr("value");
        var case_type = $("#case_type").find('.selected').attr("value");
        var case_description = $("#case_description").val();
        var case_name;
        if ($("#case_name").find('.selected') != undefined){
            case_name = $("#case_name").find('.selected').attr("value");
        }
        else {
            case_name =  $("#case_name").val();
        }
        //alert ("\r\ntype:"+customizecase_type+"\r\nproject:"+project_name+"\r\ncase_type:"+case_type+"\r\ncase_name:"+case_name+"\r\ncase_description:"+case_description);
        if (customizecase_type == "Update Case" || customizecase_type == "Extend Case"){
            sql_cmd = "select name from dut_type where name != 'gtvv4_4k' and name != 'gtvv4_cedar' and name != 'gtvv4_bg2' and name != 'gtv_bat' and name != 'jellybean' and name != 'ics' and name != 'gtvv4_willow' and name != 'bg2q4k' and name != 'LinuxRDK';select distinct case_type from case_info where dut_type='"+project_name+"';";

            sql_cmd += "select name as case_name from case_info where dut_type='"+project_name+"' and case_type='"+case_type+"';";
            sql_cmd += "select distinct case_type as case_type_full from case_info";
            addNewCase_common(customizecase_type, sql_cmd, project_name, case_type, case_name, case_description);
        }
        else if (customizecase_type == "Add New Case"){
            sql_cmd = "select name from dut_type where name != 'gtvv4_4k' and name != 'gtvv4_cedar' and name != 'gtvv4_bg2' and name != 'gtv_bat' and name != 'jellybean' and name != 'ics' and name != 'gtvv4_willow' and name != 'bg2q4k' and name != 'LinuxRDK';select distinct case_type from case_info;";
            sql_cmd += "select distinct case_type as case_type_full from case_info";
            //alert(sql_cmd);
            addNewCase_common(customizecase_type, sql_cmd, project_name, case_type, case_name, case_description);
        }

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

function AddDutType(arr_types, default_type){
    var project_names_str = GetSelectStr("project name", "project_name", arr_types, default_type, 6);
    $("#config_table").append(project_names_str);
    new MTC.select({"selector":"select6"});

    $("#project_name").change(function(){
        UpdateSelf();
    });
}
function AddCaseType(arr_types, default_type){
    var case_types_str = GetSelectStr("case type", "case_type", arr_types, default_type, 7);
    $("#config_table").append(case_types_str);
    new MTC.select({"selector":"select7"});

    $("#case_type").change(function(){
        UpdateSelf();
    });

}
function AddExtendDutType(arr_types, default_type){
    var project_names_str = GetSelectStr("extend project name", "extend_project_name", arr_types, default_type, 10);
    $("#config_table").append(project_names_str);
    new MTC.select({"selector":"select10"});
}
function AddExtendCaseType(arr_types, default_type){
    var case_types_str = GetSelectStr("extend case type", "extend_case_type", arr_types, default_type, 11);
    $("#config_table").append(case_types_str);
    new MTC.select({"selector":"select11"});
}
function AddCaseDescription(case_description){
    if (case_description == undefined || case_description == 'undefined'){
        $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case_description:</td><td><input type='text' id='case_description'></input></td></tr>");
    }
    else {
        $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case_description:</td><td><input type='text' id='case_description' value='"+case_description+"'></input></td></tr>");
    }
}
function AddCaseNames(arr_types, default_type){
    var case_names_str = GetSelectStr("case name", "case_name", arr_types, default_type, 9);
    $("#config_table").append(case_names_str);
    new MTC.select({"selector":"select9"});

    $("#case_name").change(function(){
        var project_name = $("#project_name").find('.selected').attr("value");
        var case_type = $("#case_type").find('.selected').attr("value");
        var case_name = $("#case_name").find('.selected').attr("value");
        var sql_cmd = "select description,path from case_info where dut_type='"+project_name+"' and case_type='"+case_type+"' and name='"+case_name+"'";
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
                if(data=="false"){return}
                var json = eval('(' + data + ')');
                $("#case_description").val(json[0]['description']);                
                $("#case_abs_path").val(json[0]['path']);
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
function AddNewCaseName(){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case name:</td><td><input type='text' id='case_name'></input></td></tr>");
}
function ExtendCaseName(){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >extend name:</td><td><input type='text' id='extend_case_name'></input></td></tr>");
}
function UploadCaseConfig(){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >config path:</td><td><input type='file' name='config_path', id='config_path'></td></tr>");
}
function UploadCasePackage(){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case path:</td><td><input type='file' name='case_path', id='case_path'></td></tr>");
}

function CaseAbsPath(){
    $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case abs path:</td><td><input type='text' disabled='true' id='case_abs_path'></td></tr>");
}


function AddCustomizeCaseType(default_value){
    var arr = new Array();
    arr.push("Add New Case", "Update Case", "Extend Case");
    customize_type_str = GetSelectStr("Customize Test", "customize_type", arr, default_value, 8);
    //alert(customize_type_str);
    $("#config_table").append(customize_type_str);
    new MTC.select({"selector":"select8"});

    $("#customize_type").change(function(){
        UpdateSelf();
    });
}


function addNewCase_common(type, sql_cmd, first_project_name, first_case_type, first_case_name, case_description){
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
            if(data=="false"){return}
            MTC.AddCase();
            $("#config_table").empty();
            AddCustomizeCaseType(type);
            $("#em").innerHTML = "Customize Test Case";
            focused = false;
            var src_json = {};
            var json = eval('(' + data + ')');
            var project_names_str="", case_types_str="", case_names_str="";
            var arr_project_names = new Array();
            var arr_case_types = new Array();
            var arr_case_names = new Array();
            var arr_case_types_full = new Array();

            for(var i=0;i<json.length;i++){
                if (undefined!=json[i]['name']){
                     arr_project_names.push(json[i]['name']);
                }
                if (undefined!=json[i]['case_type']){
                     arr_case_types.push(json[i]['case_type']);
                }
                if (undefined!=json[i]['case_name']){
                     arr_case_names.push(json[i]['case_name']);
                }
                if (undefined!=json[i]['case_type_full']){
                     arr_case_types_full.push(json[i]['case_type_full']);
                }

            }
            var arr_extend_project_names = arr_project_names.concat();
            if (first_project_name == undefined){
                first_project_name = arr_project_names[0];
            }
            if (first_case_type == undefined){
                first_case_type = arr_case_types[0];
            }
            if (first_case_name == undefined){
                first_case_name = arr_case_names[0];
            }
            AddDutType(arr_project_names, first_project_name);
            AddCaseType(arr_case_types, first_case_type);
            if (type == "Add New Case"){
                AddNewCaseName();
            }
            else {
                AddCaseNames(arr_case_names, first_case_name);
            }

            if (type != "Extend Case"){
                UploadCaseConfig();
                UploadCasePackage();
            }
            else {
                AddExtendDutType(arr_extend_project_names, first_project_name);
                AddExtendCaseType(arr_case_types_full, first_case_type);
                ExtendCaseName();
            }
            AddCaseDescription(case_description);
            CaseAbsPath();
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

function addNewCase(){
    sql_cmd =  "select name from dut_type where name != 'gtvv4_4k' and name != 'gtvv4_cedar' and name != 'gtvv4_bg2' and name != 'gtv_bat' and name != 'jellybean' and name != 'ics' and name != 'gtvv4_willow' and name != 'bg2q4k' and name != 'LinuxRDK';select distinct case_type from case_info";
    addNewCase_common("Add New Case", sql_cmd);
    /*
    $.ajax({
        type: "post",
        url: "/php/read-db.php",
        async: false,
        data: {
            sql_cmd: "select name from dut_type where name != 'gtvv4_4k' and name != 'gtvv4_cedar' and name != 'gtvv4_bg2' and name != 'gtv_bat' and name != 'jellybean' and name != 'ics' and name != 'gtvv4_willow' and name != 'bg2q4k' and name != 'LinuxRDK';select distinct case_type from case_info"
        },
        beforeSend: function(XMLHttpRequest){
            $("#shade-bg").show();
        },
        success: function(data, textStatus){
            if(data=="false"){return}
            MTC.AddCase();
            //$("#case_id").text(case_id);
            $("#config_table").empty();
	    AddCustomizeCaseType("Add New Case");
            $("#em").innerHTML = "Customize Test Case";
            focused = false;
            var src_json = {};
            var json = eval('(' + data + ')');
            var project_names_str="", case_types_str="";
            var first_project_name=undefined,first_case_type=undefined;
            
            for(var i=0;i<json.length;i++){
                if (first_project_name==undefined && undefined!=json[i]['name']){
                     first_project_name=json[i]['name'];
                }
                if (first_case_type==undefined && undefined!=json[i]['case_type']){
                     first_case_type=json[i]['case_type'];
                }
                if (first_case_type!=undefined && first_case_type!=undefined){break;}
            }
            project_names_str += "<tr><td class='item' >project name:</td>";
            //project_names_str += "<td><div id='project_name'><select>"
            project_names_str += "<td><div class='select select6' id='project_name'><div class='selected' value='"+first_project_name+"'>"+first_project_name+"</div><div class='selectHandler'><i class='caret'></i></div><ul class='options' style='margin-left:0px;'>";
            case_types_str += "<tr><td class='item' >case type:</td>";
            case_types_str += "<td><div class='select select7' id='case_type'><div class='selected' value='"+first_case_type+"'>"+first_case_type+"</div><div class='selectHandler'><i class='caret'></i></div><ul class='options' style='margin-left:0px;'>";

            

            for(var i=0;i<json.length;i++){
                var project_name = json[i]['name'];
                var case_type = json[i]['case_type'];
                if (project_name != undefined){
                    //project_names_str += "<option value='"+project_name+"'>"+project_name+"</option>";
                    project_names_str += "<li class='option' value='"+project_name+"'>"+project_name+"</li>";
                }
                if (case_type != undefined){
                    //ase_types_str += "<option value='"+case_type+"'>"+case_type+"</option>";
                    case_types_str += "<li class='option' value='"+case_type+"'>"+case_type+"</li>";
                }
            }
            project_names_str+="</ul></div></td></tr>";
            case_types_str+="</ul></div></td></tr>";
            $("#config_table").append(project_names_str);
            $("#config_table").append(case_types_str);
            new MTC.select({"selector":"select6"});
            new MTC.select({"selector":"select7"});
	    //new MTC.select({"selector":"select8"});
            
            $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case name:</td><td><input type='text' id='case_name'></input></td></tr>");
            $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case path:</td><td><input type='file' name='case_path', id='case_path'></td></tr>");
            $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >config path:</td><td><input type='file' name='config_path', id='config_path'></td></tr>");
            $("#config_table").append("<tr><td style='word-break:keep-all' class='item' >case_description:</td><td><input type='text' id='case_description'></input></td></tr>");

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
    */
}

