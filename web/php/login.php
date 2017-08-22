<?php

$user = $_POST['UserName'];
$password = $_POST['PassWord'];

$host = 'sc-ldap';
$domain = 'marvell.com';
$basedn = 'dc=marvell,dc=com';
$group = 'Workers';

$ad = ldap_connect("ldap://sc-ldap.marvell.com") or die('Could not connect to LDAP server.');
if (!$ad){echo 'Connect Fail!';}
//else {exit();}
//ldap_set_option($ad, LDAP_OPT_PROTOCOL_VERSION, 3);
//ldap_set_option($ad, LDAP_OPT_REFERRALS, 0);
//$bind = ldap_bind($ad, 'liuxin', 'asdasd') or die('Could not bind to AD.');

$result = ldap_bind($ad,$user, $password); 

//$userdn = getDN($ad, $user, $basedn);
if ($result) {
    echo "true";
} else {
    echo "false";
}
ldap_unbind($ad);
?>
