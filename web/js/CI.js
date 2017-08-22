function getResultInfo_fromCI(CI_id){
    constraint = "and a.group_id="+CI_id;
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

