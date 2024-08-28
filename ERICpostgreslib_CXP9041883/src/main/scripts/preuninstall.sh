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

log info "Running ERICPostgreslib RPM Pre-Uninstall"

function unset_global_path() {
  python_bin=$1
  SITE=`/usr/bin/${python_bin} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
  retcode=$?
  if [ ${retcode} -ne 0 ]; then
    log error "Failed to get python site-packages directory for ${python_bin}."
    exit 1
  fi

  PTH_PATH="$SITE/pglib.pth"
  rm -f ${PTH_PATH}
  retcode=$?
  if [ ${retcode} -ne 0 ]; then
    log error "Failed to remove ${PTH_PATH}."
    exit 1
  fi
}

if [ "$1" = "0" ]; then
  # unset global path for the pglib
  unset_global_path python
  log info "Global path for pyu unset for python 2."
  unset_global_path python3
  log info "Global path for pyu unset for python 3."
elif [ "$1" = "1" ]; then
  log info "Nothing to do during upgrade."
fi

log info "Finished ERICPostgreslib RPM Pre-Uninstall"
