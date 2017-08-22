<?php
$url_arr = split("&", $_SERVER['QUERY_STRING']);
$conn_id = split("=", $url_arr[0]);
$mac_addr = split("=", $url_arr[1]);
$con = mysql_connect("127.0.0.1", "root", "123456");
if (!$con)
  {
  die("Could not connect: " . mysql_error());
  }
$db_selected = mysql_select_db("Case_Dispatcher", $con);
$result = mysql_query("select mac_addr,client_ip,owner,dut_type,sw_version,start_time,status from conn_info where mac_addr = '$mac_addr[1]' and id != $conn_id[1] and start_time>'2015-12-31' order by start_time desc", $con);
if(! $result){echo "MySql Error:\n".mysql_error();exit();}
$json_array = array();
while($row = mysql_fetch_assoc($result)){
    foreach($row as $key=>$value){
        if($key == "status"){
            if($value == "offline"){
                $row[$key] = "<span style='color:dodgerblue;font-weight:bold'>offline</span>";
            }elseif($value == "idle"){
                $row[$key] = "<span style='color:#5ab530;font-weight:bold'>idle</span>";
            }elseif($value == "busy"){
                $row[$key] = "<span style='color:red;font-weight:bold'>busy</span>";
            }else{
                $row[$key] = "<span style='color:black;font-weight:bold'>$value</span>";
            }
        }
        if($key == "sw_version"){
            $row[$key] = str_replace("0x20", " ", $value);
        }
        if($key == "owner"){
            $row[$key] = "<a href='mailto:$value@marvell.com'>$value</a>";
        }
    }
    $json_array[] = $row;
}
$json_string = json_encode($json_array);
echo $json_string;
mysql_close($con);
?>
