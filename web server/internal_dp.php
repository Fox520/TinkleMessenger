<?php

if(isset($_GET["username"])){
	$username = $_GET["username"];
	$file = "display/default.png";
	$newfile = "display/".$username.".png";
	if(file_exists($newfile)) unlink($newfile);
	copy($file, $newfile);

}else{
	echo "What the **** are you doing";
}

?>