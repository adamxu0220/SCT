<?php


$dir = $_POST["src_path"];
//echo "src_path:$dir";
//$dir="/mnt/external/Image_from_SBT";
$file_num = 0;
$json_array = array(); 
$header_len = strlen($dir)+1;
//echo " <span><b> $dir </b></span><br />\n";
function getimagefolder( $dirName ){ 
	if ( $handle = opendir( "$dirName" ) ) {
		while ( false !== ( $item = readdir( $handle ) ) ) { 
			if ( $item != "." && $item != ".." ) { 
				if ( is_dir( "$dirName/$item" ) ) { 
					getimagefolder( "$dirName/$item" );
					//echo " <span><b> $dirName/$item </b></span><br />\n";
					$s=0;
				}
				else { 
					if(strstr($item,"bl_normal.subimg.gz")){
						//echo " <span><b> $dirName/$item </b></span><br />\n";
						global $file_num;
						global $json_array;
						global $header_len;
						//$json_array[$file_num] = substr($dirName, $header_len);
						$json_array[$file_num] = substr($dirName, $header_len,-8);
						//echo " <span><b> $file_num </b></span><br />\n";
						//echo " <span><b>$json_array[$file_num] </b></span><br />\n";
						$file_num++;

					}
				} 
			}
		}
		closedir( $handle ); 
		if(strstr($dirName,"bl_normal.subimg.gz")){
			$loop = explode("bl_normal.subimg.gz",$dirName);
			$countArr = count($loop)-1;
			//if(empty($loop[$countArr])){
			//	echo " <span style='color:#297C79;'><b>hello $dirName </b></span><br />\n";
			//}
		}
	}else{
		//die("Failed to open dir!");
                return;
	}
}
getimagefolder($dir);
$json_string = json_encode($json_array);
echo $json_string; 

?>






