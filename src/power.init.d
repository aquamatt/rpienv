#!/bin/bash

### BEGIN INIT INFO
# Provides: power_monitor
# Required-Start: $network
# Required-Stop: $network
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Start and Stop
# Description: Runs power monitor
### END INIT INFO

#       /etc/init.d/power
#
# Starts the power monitor daemon
#
# chkconfig: 345 90 5
# description: Runs power monitor
#
# processname: power.py

prog_dir="/usr/local/rpienv"
pid_dir="/var/run"

pid_file="$pid_dir/power.pid"

PATH=/sbin:/bin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:$PATH

RETVAL=0

is_running(){
  [ -e $pid_file ]
}

start(){
    echo -n $"Starting power monitor: "

    $prog_dir/bin/python $prog_dir/rpienv/power.py --pidfile=$pid_file
    RETVAL=$?
    echo
    return $RETVAL
}

stop(){
    echo -n $"Stopping $prog: "
    if (is_running); then
      $prog_dir/bin/python $prog_dir/rpienv/power.py --pidfile=$pid_file --kill
      RETVAL=$?
      echo
      return $RETVAL
    else
      echo "$pid_file not found"
    fi
}

status(){
    echo -n $"Checking for $pid_file: "

    if (is_running); then
      echo "found"
    else
      echo "not found"
    fi
}

reload(){
    restart
}

restart(){
    if (is_running); then
      $prog_dir/bin/python $prog_dir/rpienv/power.py --pidfile=$pid_file --restart
      RETVAL=$?
      echo
      return $RETVAL
    else
      start
    fi
}


condrestart(){
    is_running && restart
    return 0
}


# See how we were called.
case "$1" in
    start)
	start
	;;
    stop)
	stop
	;;
    status)
	status
	;;
    restart)
	restart
	;;
    reload)
	reload
	;;
    condrestart)
	condrestart
	;;
    *)
	echo $"Usage: $0 {start|stop|status|restart|condrestart}"
	RETVAL=1
esac

exit $RETVAL
