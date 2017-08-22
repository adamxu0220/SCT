<?php
$testcase_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/";
$case_name = $_POST["case_name"];
$case_abs_path = $_POST["case_abs_path"];
$project_name = $_POST["project_name"];
$file_type = $_POST["file_type"];
$tmp = $_POST["file_id"];
$pos = strpos($tmp, ",");
$config_id = substr($tmp, 0, $pos);
$package_id = substr($tmp, $pos+1, strlen($tmp) - $pos);

$file_info = $_FILES[$config_id];
echo "keys:".json_encode(array_keys($_FILES))."\r\n";
echo "\r\nfile_id:".$tmp."\r\n";
echo "\r\nconfig_id:".$config_id."\r\n";
echo "\r\npackage_id:".$package_id."\r\n";


	if (!file_exists($testcase_path.$project_name))
	{ 
		mkdir ($testcase_path.$project_name, 0777); 
	}
	if (!file_exists($testcase_path.$project_name."/".$case_name))
        {
                mkdir ($testcase_path.$project_name."/".$case_name, 0777);
        }
	$ok = move_uploaded_file($file_info["tmp_name"], $testcase_path.$project_name."/".$case_name."/config.py");
if (!$ok) exit('false');
$file_info = $_FILES[$package_id]; 
	echo "it is case tar.gz file.\r\n";
	if (!file_exists($testcase_path."all")){
		mkdir ($testcase_path."all", 0777);
	}
        echo "tmp_name:".$file_info["tmp_name"]."\r\n";
        echo "file_exist:".file_exists($file_info["tmp_name"])."\r\n";
        echo "dst_name:".$testcase_path."all/".$case_name.".tar.gz\r\n";

	//if (file_exists($testcase_path."/all/".$case_name.".tar.gz))
	$ok = move_uploaded_file($file_info["tmp_name"], $testcase_path."all/".$case_name.".tar.gz");


//$ok = file_put_contents($testcase_path.$project_name."/".$case_name."/config",$file_info);
if (!$ok) exit('false');



$sql = $_POST["sql_cmd"];
$con = mysql_connect("127.0.0.1", "root", "123456");
if (!$con)
  {
  die("Could not connect: " . mysql_error());
  }
$db_selected = mysql_select_db("Case_Dispatcher", $con);

$sql_cmds = split(';',$sql);
$json_array = array();
foreach ($sql_cmds as $sql_cmd){
    $result = mysql_query($sql_cmd, $con);
    if(! $result){echo "MySql Error:\n".mysql_error();exit();}
}
$json_string = json_encode($json_array);
echo $json_string;
mysql_close($con);


?>
