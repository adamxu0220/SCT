<?php
$dir = $_POST["src_path"];
$json_array = array();
if (false != ($handle = opendir ( $dir ))) {
    $i=0;
    while ( false !== ($file = readdir ( $handle )) ) {
        if ($file != "." && $file != "..") {
                $json_array[$i]=$file;
                $i++;
            }
        }
        closedir ( $handle );
}

$json_string = json_encode($json_array);
echo $json_string;
?>
