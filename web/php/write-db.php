<?php
$sql = $_POST["sql_cmd"];
$con = mysql_connect("127.0.0.1", "root", "123456");
if (!$con)
  {
  die("Could not connect: " . mysql_error());
  }
$db_selected = mysql_select_db("Case_Dispatcher", $con);
$result = mysql_query($sql, $con);
if(! $result){echo "MySql Error:\n".mysql_error();exit();}
echo mysql_insert_id();
mysql_close($con);
?>