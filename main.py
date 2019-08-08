import sys
import time
import datetime as date
import threading
import paho.mqtt.client as mqtt
import os
import filecmp
import shutil
f = open("info.txt", 'r')

broker = f.readline().strip()
PANID = f.readline().strip()
time_info = []
time_info.append(f.readline().strip())
time_info.append(f.readline().strip())
Device = []
Device.append(f.readline().strip())
Device.append(f.readline().strip())
Device.append(f.readline().strip())
Device.append(f.readline().strip())

f.close()

mqtt_client = []
device_type = ["M", "S1", "S2", "S3"]
check_device = [False, False, False, False]
check_topic = []
timer_list = []

imeiTEXTlist = []
deviceLABELlist = []
deviceOKcount = [0, 0, 0, 0, 0]
deviceFailcount = [0, 0, 0, 0, 0]

mqttFlag = False
connectFlag = False
nowConnectState = False
sampleStartFlag = False
endEventFlag = False

testInterval = [] #threading.Timer(int(time_info[1])*60, connMQTTbroker)
testTimerOut = [] #threading.Timer(3*60, wait_time_out)

autologCount = 0


########################################## MQTT ##########################################

## 로그 발생 시 실행 콜백
def on_log(client, userdata, level, buf):
    print("on_log\t", buf)

## Broker 커넥션 시 실행 콜백
def on_connect(client, userdata, level, buf):
    print("on_connect\t", buf)
    global nowConnectState

    if buf == 0:
        log_appand("Broker Connection Complete")
        log_appand(None)
        nowConnectState = True
        for i in Device:
            if i != "":
                time.sleep(1)
                mqtt_client[0].subscribe('Entity/SHM/Node/'+i+'/Device/Status')

## 디스커넥션 시 실행 콜백
def on_disconnect(client, userdata, rc):
    print("Disconnect")
    global nowConnectState

    log_appand("Disconnect Broker\n")
    nowConnectState = False

# 서버에게서 PUBLISH 메시지를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
    print("On_Message")

    topic = msg.topic
    mqtt_data = str(msg.payload)
    for i in range(len(Device)):
        if (Device[i] != "") and (topic.find(Device[i]) >= 0) and (mqtt_data.find('"GENERIC"') >= 0) and (check_device[i] == False):
            print(Device[i] + "  GENERIC")
            check_device[i] = True
            send_text = "OK Device :" + "\t" + device_type[i] + " " + Device[i]
            log_appand(send_text)
            # make_data_file(str(msg.payload), str(topic))
    print("check deivce ", check_device)

    if False in check_device:
        print("list False")
    else:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


########################################## Func ##########################################

## MQTT Broker Connect
def connMQTTbroker():
    print("Run connMQTTbroker")
    print(nowConnectState)
    if(nowConnectState == False):
        print("Connect Broker")
        log_appand("Connecting...")
        client = mqtt.Client()  # MQTT Client 오브젝트 생성

        client.on_log = on_log  # on_log callback 설정
        client.on_message = on_message  # on_message callback 설정
        client.on_connect = on_connect  # on_connect callback 설정
        client.on_disconnect = on_disconnect #on_disconnect callback 설정
        client.connect(broker)  # MQTT 서버에 연결
        client.loop_start()    #MQTT Loop Start
        mqtt_client.append(client)

        start_sampling()

        testInterval.clear()
        testTimerOut.clear()
        timer = threading.Timer(int(time_info[1]) * 60, connMQTTbroker)
        timer.start()
        testInterval.append(timer)
        timer = threading.Timer(3 * 60, wait_time_out)
        timer.start()
        testTimerOut.append(timer)

## Send Sampleing Start Command
def start_sampling():
    global sampleStartFlag
    print("change sampleStartFlag True")
    sampleStartFlag = True

## 수신 대기 타임아웃
def wait_time_out():
    print("wait timer out")
    for i in mqtt_client:
        i.loop_stop()
        i.disconnect()
    mqtt_client.clear()

def log_appand(text):
    now_time = date.datetime.now()
    f = open(now_time.strftime('%m-%d') + "LOG.txt", 'a')
    if(text != None):
        f.writelines(str(now_time.strftime('%Y-%m-%d %H:%M:%S')) + "\t" + text + '\n')
    else:
        f.writelines("\n")
    f.close()

def end_timer():
    global endEventFlag
    endEventFlag = True

log_appand(None)
log_appand("Test Start")
log_appand("Broker :\t" + broker)
log_appand("PANID : \t" + PANID)
log_appand("TotalTime :\t" + time_info[0])
log_appand("interval :\t" + time_info[1])

for i in range(len(Device)):
    text = device_type[i] + " :\t\t" + Device[i]
    log_appand(str(text))

if time_info[0] != "0":
    testTime = threading.Timer(int(time_info[0])*60, end_timer).start()

connMQTTbroker()

####################################################################################################################

while(1):
    if((nowConnectState == True) and (sampleStartFlag == True)):
        print("Sample Start")
        log_appand("Send Sample Start Command")
        mqtt_client[0].publish("Entity/SHM/Node/" + PANID + "/OTA",
                            '{"nId":"' + PANID + '","nT":"SHM","status":{"OP":"Sample"},"timestamp":' + str(
                                int(time.time())) + '}')
        sampleStartFlag = False

    if(endEventFlag):
        print("Test Complete")
        log_appand("Test Complete")
        testInterval.cancel()
        testTimerOut.cancel()
        for i in mqtt_client:
            i.loop_stop()
            i.disconnect()
        mqtt_client.clear()
        break
