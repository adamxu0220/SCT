<?php
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
    if(! $result){echo "MySql Error:\n".mysql_error();echo $sql_cmd;exit();}
    while($row = mysql_fetch_assoc($result)){
        $json_array[] = $row;
    }
}
$json_string = json_encode($json_array);
echo $json_string;
mysql_close($con);
?>
