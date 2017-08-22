
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

function searchFilesList(filePath){
    var fso = new ActiveXObject("Scripting.FileSystemObject");
    var SBT_folds = new Array();  
    var f = fso.GetFolder(filePath);  
    var fk = new Enumerator(f.SubFolders);  
    alert(fk);
    for (; !fk.atEnd(); fk.moveNext()) {  
        //if (fk.item().)
        alert(fk.item());
        SBT_folds.push(fk.item());  
        alert (fk.item());
    }  

function Upgrade(){
    MTC.Upgrade();
    var name="SBT version";
    var name_id = "sbt_ver";
    var names_arr = new Array();
    
    names_arr.push("5001");
    names_arr.push("5002");
    names_arr.push("5003");
    serachFilesList("/home/sqa/Img/AndroidTV/");
    var name_default = "5003";
    var versions = GetSelectStr(name, name_id, names_arr, name_default, 6);
    $("#config_table").append(versions);
    new MTC.select({"selector":"select6"});

}

