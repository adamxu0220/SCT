<?php
$testcase_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/";
$case_name = $_POST["case_name"];
$case_abs_path = $_POST["case_abs_path"];
$project_name = $_POST["project_name"];
$file_type = $_POST["file_type"];
$file_id = $_POST["file_id"];
array_push($_FILES,$_REQUEST);

/*
#$file_info = var_export($_FILES,true);
echo $_FILES."\r\n";
echo "\r\n".$_FILES."\r\nbbb\n\n";


foreach(array_keys($_FILES) as $key){
echo "\r\nkey :" . $key;
echo "\r\nvalue :" . $_FILES[$key]."\r\n";
}
echo array_search($_FILES, "case_config")."\r\n";
*/
$file_info = $_FILES[$file_id];

function upload_config(){
        echo "it is config.\r\n";
        if (!file_exists($testcase_path.$project_name))
        {
                mkdir ($testcase_path.$project_name, 0777);
        }
        if (!file_exists($testcase_path.$project_name."/".$case_name))
        {
                mkdir ($testcase_path.$project_name."/".$case_name, 0777);
        }
        $ok = move_uploaded_file($file_info["tmp_name"], $testcase_path.$project_name."/".$case_name."/config.py");
}

function upload_package(){
        echo "it is case tar.gz file.\r\n";
        if (!file_exists($testcase_path."all")){
                mkdir ($testcase_path."all", 0777);
        }
        echo "tmp_name:".$file_info["tmp_name"]."\r\n";
        echo "file_exist:".file_exists($file_info["tmp_name"])."\r\n";
        echo "dst_name:".$testcase_path."all/".$case_name.".tar.gz\r\n";

        //if (file_exists($testcase_path."/all/".$case_name.".tar.gz))
        $ok = move_uploaded_file($file_info["tmp_name"], $testcase_path."all/".$case_name.".tar.gz");

}

echo "\r\n".$file_info."\r\nbbb\n\n";
if ($file_type == "upload_config" || $file_type == "update_config"){
	echo "it is config.\r\n";
	if (!file_exists($testcase_path.$project_name))
	{ 
		mkdir ($testcase_path.$project_name, 0777); 
	}
	if (!file_exists($testcase_path.$project_name."/".$case_name))
        {
                mkdir ($testcase_path.$project_name."/".$case_name, 0777);
        }
	$ok = move_uploaded_file($file_info["tmp_name"], $testcase_path.$project_name."/".$case_name."/config.py"); 
}
else if ($file_type == "upload_package"){
	echo "it is case tar.gz file.\r\n";
	if (!file_exists($testcase_path."all")){
		mkdir ($testcase_path."all", 0777);
	}
        echo "tmp_name:".$file_info["tmp_name"]."\r\n";
        echo "file_exist:".file_exists($file_info["tmp_name"])."\r\n";
        echo "dst_name:".$testcase_path."all/".$case_name.".tar.gz\r\n";

	//if (file_exists($testcase_path."/all/".$case_name.".tar.gz))
	$ok = move_uploaded_file($file_info["tmp_name"], $testcase_path."all/".$case_name.".tar.gz");
}
else if ($file_type == "update_package"){
        echo "it is case tar.gz file.\r\n";
        echo "tmp_name:".$file_info["tmp_name"]."\r\n";
        echo "file_exist:".file_exists($file_info["tmp_name"])."\r\n";
        echo "dst_name:".$testcase_path."../".$case_abs_path."\r\n";

        //if (file_exists($testcase_path."/all/".$case_name.".tar.gz))
        //unlink($case_abs_path);
        $ok = move_uploaded_file($file_info["tmp_name"], $testcase_path."../".$case_abs_path);
}

else {
	echo "invalid file type:".$file_type."\r\n";
}


//$ok = file_put_contents($testcase_path.$project_name."/".$case_name."/config",$file_info);
if ($ok) exit('true');
exit('false');
?>
