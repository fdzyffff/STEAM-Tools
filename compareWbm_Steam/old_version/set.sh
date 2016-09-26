#setenv SSO_COOKIE /tmp/foo
export SSO_COOKIE=/tmp/foo
cern-get-sso-cookie --krb -r -u https://cmswbm.web.cern.ch/cmswbm -o $SSO_COOKIE
