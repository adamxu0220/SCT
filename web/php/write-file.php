<?php
    function get_case_name($task_id){
        $sql = "select name,case_info.id,case_cmd_pool.id,case_cmd_pool.case_id from case_info,case_cmd_pool where case_cmd_pool.case_id=case_info.id and case_cmd_pool.id=$task_id";
        $con = mysql_connect("127.0.0.1", "root", "123456");
        $db_selected = mysql_select_db("Case_Dispatcher", $con);
        $result = mysql_query($sql, $con);
        $row = mysql_fetch_assoc($result);
        $case_name = $row["name"];
        mysql_close($con);
        return $case_name;
    }
    $url_arr = split("&", $_SERVER['QUERY_STRING']);
    $case_owner = split("=", $url_arr[0]);
    $dut_type = split("=", $url_arr[1]);
    $dut_type_path = strtoupper($dut_type[1]);
    $task_json = $_POST;
    foreach($task_json as $key=>$value){
        $task_id = $key;
        $case_name = get_case_name($task_id);
        $task_config_json = $value;
        $task_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$task_id/config.py";
        $user_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/$dut_type_path/$case_name/.config_$case_owner[1].py.swp";
        //echo $user_config_path;
        if(!file_exists($task_config_path)){
            mkdir("/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$task_id", 0777);
            chmod($task_config_path,0777);
        }
        $config_file = fopen($task_config_path, "w") or die("Unable to write config file!");
        $user_config_file = fopen($user_config_path, "w") or die("Unable to write user config file!");
        foreach($task_config_json as $opt_key=>$opt_value){
            $option = $opt_key;
            $option_val = $opt_value;
            fwrite($config_file,"$option=$option_val\n");
            fwrite($user_config_file,"$option=$option_val\n");
        }
        fclose($config_file);
        fclose($user_config_file);
    }
?>
