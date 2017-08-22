<?php
//$case_name = $_POST["case_name"];
//$project_name = $_POST["project_name"];
$config_path_upLoadError=$_FILES['config_path']['error'];
$config_path_fileName=$_FILES['config_path']['name'];
$config_path_fileTemName=$_FILES['config_path']['tmp_name'];
$uploadDir="/home/sqa/CaseDispatcher_v2.0/server/TestCase/";

if($config_path_upLoadError>0){ //0表示没有错误发生，文件上传成功
  echo"ERROR：";
  switch($config_path_upLoadError){
   case 1:echo"上传文件超过配置文件规定值。";break; //1表示上传的文件超过了php.ini中upload_max_filesize选项限制的值
   case 2:echo"上传文件超过表单约定值。";break; //2表示上传文件的大小超过了 HTML 表单中 MAX_FILE_SIZE 选项指定的值。
   case 3:echo"上传文件不完全。";break; //3表示文件只有部分被上传。
   case 4:echo"没有上传文件。";break; //4表示没有文件被上传。
  }
 }else{
  if(is_uploaded_file($config_path_fileTemName)){ //确认文件通过HTTP POST上传
   if(!move_uploaded_file($config_path_fileTemName,($uploadDir."aasda"))){ //如果无法将>上传的文件移动到新位置
    echo"文件上传失败，请重新上传。";
   }else{ //否则返回成功信息
    echo"文件上传成功！<br>".date("Y-m-d H:i:s")."<br>上传文件：".$fileName."<br>文件大小：".number_format(($fileSize/1024/1024),2)."Mb"."<br>重命名为：".$fileReName;
   }
  }
 }

?>
