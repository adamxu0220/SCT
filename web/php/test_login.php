<?php

$user = 'hzxu';
$password = '123456';

$host = 'sc-ldap';
$domain = 'marvell.com';
$basedn = 'dc=marvell,dc=com';
$group = 'Workers';


$ad = ldap_connect("ldap://sc-ldap.marvell.com") or die('Could not connect to LDAP server.');
if (!$ad){echo 'Connect Fail!';}

$result = ldap_bind($ad,$user, $password); 

//$userdn = getDN($ad, $user, $basedn);
if ($result) {
    echo "true";
} else {
    echo "false";
}
ldap_unbind($ad);
?>
