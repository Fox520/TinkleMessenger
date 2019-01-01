<?php
if(isset($_FILES['testname']['name'])){
	$allowed =  array('gif','png' ,'jpg');
	$uploaddir = "img/";
	$uploadfile = $uploaddir . basename($_FILES['testname']['name']);
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