<?php

$uploaddir = 'display/';
$allowed =  array('png' ,'jpg');
if((isset($_FILES['testname']['name']))){
	$uploadfile = $uploaddir . basename($_FILES['testname']['name']);
	if(file_exists($uploadfile)) unlink($uploadfile);
	$ext = pathinfo($uploadfile, PATHINFO_EXTENSION);
	if(!in_array($ext,$allowed) ) {
	    echo 'error';
	}else{
		if(move_uploaded_file($_FILES['testname']['tmp_name'], $uploadfile)){
			echo "Uploaded";
		}
	}
	
}else{
    echo "Not uploaded";
}

?>