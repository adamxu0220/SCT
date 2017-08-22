<?php
$url_arr = split("=", $_SERVER['QUERY_STRING']);
$filename = "/home/sqa/CaseDispatcher_v2.0/server/Log/$url_arr[1]/result.html";
if(file_exists($filename)){
    echo "true";
}else{
    echo "false";
}
?>  