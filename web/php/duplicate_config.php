<?php
$src_id = $_POST["src_id"];
$des_id = $_POST["des_id"];
$src_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$src_id/config.py";
$des_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$des_id/config.py";
if(!file_exists($des_config_path)){
        mkdir("/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$des_id", 0777);
        chmod($des_config_path,0777);
    }
echo copy($src_config_path, $des_config_path);
?>