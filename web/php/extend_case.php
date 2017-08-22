<?php
$testcase_path = "/home/sqa/CaseDispatcher_v2.0/server/TestCase/";
$case_name = $_POST["case_name"];
$project_name = $_POST["project_name"];


$extend_case_name = $_POST["extend_case_name"];
$extend_project_name = $_POST["extend_project_name"];

$src_path = $testcase_path.$project_name."/".$case_name."/config.py";
$dst_project_fold = $testcase_path.$extend_project_name;
$dst_case_fold = $testcase_path.$extend_project_name."/".$extend_case_name;
$dst_path = $dst_case_fold."/config.py";
if (!file_exists($dst_project_fold))
{ 
	mkdir ($dst_project_fold, 0777); 
}
if (!file_exists($dst_case_fold))
{
	mkdir ($dst_case_fold, 0777);
}
$ok = copy($src_path, $dst_path); 
if ($ok) exit('true');
exit('false');
?>
