<?php
    $dut_type = $_POST["dut_type"];
    $case_name = $_POST["case_name"];
    $task_id = $_POST["task_id"];
    $case_owner = split("=", $_SERVER['QUERY_STRING']);
    if($task_id != ""){
        $default_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$task_id/config.py";   
    }else{
        $user_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/$dut_type/$case_name/.config_$case_owner[1].py.swp";
        if(file_exists($user_config_path)){
            $default_config_path = $user_config_path;
        }else{
            $default_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/$dut_type/$case_name/config.py";
        }
    }
    $config_file = fopen($default_config_path, "r") or die("false");
    echo fread($config_file,filesize($default_config_path));
    fclose($config_file);
?>
