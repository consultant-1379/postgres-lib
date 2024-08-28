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

log info "Running ERICPostgreslib RPM Post-Install"

function set_global_path() {
  python_bin=$1
  SITE=`/usr/bin/${python_bin} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
  retcode=$?
  if [ ${retcode} -ne 0 ]; then
    log error "Failed to get python site-packages directory for ${python_bin}."
  fi

  PTH_PATH="$SITE/pglib.pth"
  echo "/opt/ericsson/postgres/" > ${PTH_PATH}
  retcode=$?
  if [ ${retcode} -ne 0 ]; then
    log error "Failed to set contents to the file ${PTH_PATH}."
  fi
}

# setting global path for the pglib
set_global_path python
set_global_path python3

log info "Finished ERICPostgreslib RPM Post-Install"