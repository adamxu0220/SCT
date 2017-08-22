<?php
$sbt_ver = $_POST["sbt_ver"];
$client_id = $_POST["client_id"];
$dut_type = $_POST["dut_type"];
$owner = $_POST["owner"];
$version = $_POST["version"];
$start_time=date("Y-m-d H:i",time());
$deadline=date("Y-m-d H:i",time()+(7 * 24 * 60 * 60));
$con = mysql_connect("127.0.0.1", "root", "123456");
if (!$con)
  {
  die("Could not connect: " . mysql_error());
  }
$db_selected = mysql_select_db("Case_Dispatcher", $con);
$sql_cmd = "insert case_cmd_pool (dut_type, cmd_owner, case_id, client_id, status, create_time, deadline, case_parametar) value ('$dut_type', '$owner', '451', $client_id, 'not run', '$start_time', '$deadline', '-version$version')";
$result = mysql_query($sql_cmd, $con);
if(! $result){echo "MySql Error:\n".mysql_error();exit();}

$sql_cmd = "select id from case_cmd_pool where create_time='$start_time' and deadline='$deadline'";
$result = mysql_query($sql_cmd, $con);
if(! $result){echo "MySql Error:\n".mysql_error();exit();}


$json_array = array();
while($row = mysql_fetch_assoc($result)){
    $config_id= $row['id'];
    break;
}

/*
$src_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/ANDROIDTV_SPRINT_BG4CT/fastboot_burn_standard_new_v2.0/config.py";
$des_config_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$config_id/config.py";
if(!file_exists($des_config_path)){
        mkdir("/home/sqa/CaseDispatcher_v2.0/server/TestCase/Config/$config_id", 0777);
        chmod($des_config_path,0777);
    }
echo copy($src_config_path, $des_config_path);

$content = @file_get_contents($des_config_path);
if($content){
    $content=str_replace('Img_Version1 = "SBT5005"', 'Img_Version1 = "'.$version.'"', $content);
    file_put_contents($des_config_path, $content);
}
*/
//$json_string = json_encode($json_array);
//echo $json_string;
mysql_close($con);
?>
