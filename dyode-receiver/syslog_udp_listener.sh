#!/usr/bin/tclsh
package require udp ; # load the required UDP Package

echo "press CTRL-C to stop." ;

set port 514 ; # default SYSlog port
set logfile "/home/lowside/syslog/highside_syslog.log" ; # set the log filename to log data to

# Capture the UDP data here
proc udp_triggered {} {
    global dg logfile ; # ensure the global variables work in this procedure
    set rcdata [read $dg(udp)] ; # grab the UDP data within rcdata
    set udp_log [open $logfile a] ; # open the specified logfile to append to (auto-creates if does not exist)
    puts $udp_log $rcdata ; # place the UDP data line into the log file
    close $udp_log ; # close the log file
    return
}

set dg(udp) [udp_open $port] ; # setup the UDP capture port
fileevent $dg(udp) readable udp_triggered ; # setup the event trigger when the UDP port becomes readable and execute the procedure to capture the data
vwait forever ; # activates the (fileevent) trigger to wait for UDP data