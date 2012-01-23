<?php
  /* Verify BrowserID assertion */ 
  $url = 'https://browserid.org/verify';

  $data = array(
    'assertion' => $_GET['assertion'],
    'audience' => $_GET['audience']
  );

  $params = array('http' => array(
    'method' => 'POST',
    'content' => $data,
    'header' => 'Content-Type: application/json'              
  ));

  echo @stream_get_contents($fp);  
?>