#!/bin/bash
cd /summer/pyroot/zhixiao_spirde
b=`ps -ef | grep "[py]thon3 zx_spirder.py" |awk '{print $2}'|wc -l`

if [ $b -eq 0 ]
 then
    nohup python3 zx_spirder.py >zx_spirder.log &
else
   kill `ps -ef | grep "[py]thon3 zx_spirder.py" |awk '{print $2}'`
   nohup python3 zx_spirder.py >zx_spirder.log &
fi
