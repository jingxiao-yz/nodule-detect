#!/bin/bash

while true
do

	#先停止上次进程
	pythonpath='/home/predict/manage.py'
	PID=`ps -ef | grep $pythonpath | grep -v grep | awk '{print $2}'`
	if [ -n "$PID" ]
	then
	kill -9 $PID
	fi

	#脚本启动当前时间
	nowtime=$(date "+%Y-%m-%d %H:%M:%S")
	echo "$nowtime: 已启动$pythonpath" >> /home/predict/awake_manage.log
	#下次重启时间(明天凌晨3点)
	restarttime="$(date -d tomorrow "+%Y-%m-%d") 03:00:00"
	echo "$pythonpath 下次重启时间：${restarttime}" >> /home/predict/awake_manage.log

	#转为时间戳
	nowtime_stamp=$(date --date="$nowtime" +%s)
	restarttime_stamp=$(date --date="$restarttime" +%s)

	#启动应用
	nohup /root/anaconda3/bin/python /home/predict/manage.py >> /home/predict/manage.log &

	#获取将要休眠的时间(秒)
	sleeptime=$((restarttime_stamp - nowtime_stamp))
	#如果sleeptime小于或等于0
	if [ $sleeptime -le 0 ]
	then
	break
	fi
	# echo "休眠：${sleeptime}s"
	#开始等待，直至明天凌晨，开始下一次循环

	sleep "${sleeptime}"

done


####    后台启动命令，重启日志输出到awake_manage.log里面
####    nohup /home/predict/awake_manage.sh >> /home/predict/awake_manage.log &