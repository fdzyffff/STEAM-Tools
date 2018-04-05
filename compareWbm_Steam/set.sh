#setenv SSO_COOKIE /tmp/foo
export SSO_COOKIE=/tmp/xgao_sso
cern-get-sso-cookie --krb -r -u https://cmswbm.cern.ch/cmsdb -o $SSO_COOKIE
#cern-get-sso-cookie --krb -r -u https://mmm.cern.ch/owa/# -o $SSO_COOKIE
