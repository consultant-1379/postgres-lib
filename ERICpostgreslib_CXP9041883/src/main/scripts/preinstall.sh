#!/bin/bash

log(){
  msg=$2
  dev_log=/dev/log
  if [[ -S "$dev_log" ]]; then
    case $1 in
    info)
      logger -s -t postgres-lib-install -p 'user.notice' "$msg"
    ;;
    error)
      logger -s -t postgres-lib-install -p 'user.error' "$msg"
    ;;
    esac
  else
    case $1 in
    info)
      echo "$(date +'%b  %u %T') postgres-lib-install [INFO]" "$msg"
    ;;
    error)
      echo "$(date +'%b  %u %T') postgres-lib-install [ERROR]" "$msg"
    ;;
    esac
  fi
}

log info "Running pg_lib RPM Pre-Install"

grep "SLES" /etc/os-release > /dev/null 2>&1
IS_SLES=$?

grep "Red Hat Enterprise Linux" /etc/redhat-release > /dev/null 2>&1
IS_RHEL=$?

pip_install () {
  pip=$1
  pkg_name=$2
  out=$(/usr/bin/"${pip}" install "${pkg_name}" 2>&1)
  # shellcheck disable=SC2181
  if [ $? -ne 0 ]; then
    log error "Failed to install ${pkg_name} via pip"
    log error "PIP OUTPUT: ${out}"
    exit 1
  fi
}

# If postgres-lib gets installed in integrated solutions uncomment the next
# section and ensure pip will installed the packages
#if [ ${IS_RHEL} -eq 0 ]; then
#  pip_install pip2 "psycopg2==2.7.7"
#  pip_install pip2 "psycopg2-binary==2.8.6"
#fi

log info "Finished pg_lib RPM Pre-Install"
