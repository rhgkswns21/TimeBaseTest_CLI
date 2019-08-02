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
timer = []

imeiTEXTlist = []
deviceLABELlist = []
deviceOKcount = [0, 0, 0, 0, 0]
deviceFailcount = [0, 0, 0, 0, 0]
mqttFlag = False
connectFlag = False
autologCount = 0

## MQTT Broker Connect
def connMQTTbroker(broker):
    print("Run connMQTTbroker")
    global connectFlag
    global mqttFlag

    connectFlag = False
    # time_list = threading.Timer(60, mqttconnectTimer)
    # time_list.start()
    # timer.append(time_list)

    if(mqttFlag == False):
        print("Connect Broker")
        log_appand("Connecting...")
        client = mqtt.Client()  # MQTT Client 오브젝트 생성

        client.on_log = on_log  # on_log callback 설정
        client.on_message = on_message  # on_message callback 설정
        client.on_connect = on_connect  # on_connect callback 설정
        client.on_disconnect = on_disconnect #on_disconnect callback 설정
        client.connect(broker)  # MQTT 서버에 연결

        connectFlag = True
        mqtt_client.append(client)

        client.loop_start()    #MQTT Loop Start
        # client.loop_forever()

def log_appand(text):
    now_time = date.datetime.now()
    f = open(now_time.strftime('%m-%d') + "LOG.txt", 'a')
    if(text != None):
        f.writelines(str(now_time.strftime('%Y-%m-%d %H:%M:%S')) + "\t" + text + '\n')
    else:
        f.writelines("\n")
    f.close()

def on_log(client, userdata, level, buf):
    print("on_log\t", buf)

def on_connect(client, userdata, level, buf):
    print("on_connect\t", buf)
    global mqttFlag

    if buf == 0:
        log_appand("Broker Connection Complete")
        log_appand(None)
        mqttFlag = True
        for i in Device:
            if i != "":
                time.sleep(1)
                mqtt_client[0].subscribe('Entity/SHM/Node/'+i+'/Device/Status')

def on_disconnect(client, userdata, level, buf):
    print("Disconnect")
    global mqttFlag

    log_appand("Disconnect Broker\n")
    mqttFlag = False

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

log_appand(None)
log_appand("Broker :\t" + broker)
log_appand("PANID : \t" + PANID)
log_appand("TotalTime :\t" + time_info[0])
log_appand("interval :\t" + time_info[1])
for i in range(len(Device)):
    text = device_type[i] + " :\t\t" + Device[i]
    log_appand(str(text))

connMQTTbroker(broker)

while(1):
    time.sleep(1)

####################################################################################################################

# def startBT_event(self):
#     print("startBT click")
#     self.log_appand("Start Button click")
#
#     broker = self.brokerTEXT.text()
#     time_info.append(self.testimeTEXT.text())
#     time_info.append(self.intervaltimeTEXT.text())
#
#     now_time = date.datetime.now()
#     set_time = now_time + date.timedelta(minutes=int(time_info[0]))
#     if time_info[0] == '0':
#         send_text = "TestTime : " + now_time.strftime('%Y-%m-%d %H:%M:%S') + " - "
#         self.log_appand(send_text)
#     else:
#         send_text = "TestTime : " + now_time.strftime('%Y-%m-%d %H:%M:%S') + " - " + set_time.strftime('%Y-%m-%d %H:%M:%S')
#         self.log_appand(send_text)
#
#     send_text = "Time Interval : " + time_info[1] + " Minutes"
#     self.log_appand(send_text)
#     send_text = "Broker IP : " + broker
#     self.log_appand(send_text)
#     print("broker : ", broker)
#
#     Device.clear()
#     for i in range(len(self.imeiTEXTlist)):
#         Device.append(self.imeiTEXTlist[i].text())
#     self.text_edit_start()
#
#     self.connMQTTbroker(broker)
#     time.sleep(1)
#     self.intervalTimer()
#     if time_info[0] != '0':
#         time_list = threading.Timer(int(time_info[0])*60, self.testTimer)
#         time_list.start()
#         timer.append(time_list)
#
# def logBT_event(self):
#     print("logBT click")
#     self.log_appand("LOG Button click")
#     Device.clear()
#     for i in range(len(self.imeiTEXTlist)):
#         Device.append(self.imeiTEXTlist[i].text())
#     self.log_start()
#     self.client1.loop_stop()
#     self.client1.disconnect()
#
# def exitBT_event(self):
#     print("exitBT click")
#     self.client.disconnect()
#     for i in timer:
#         i.cancel()
#     QCoreApplication.instance().quit()
#
# def saveBT_event(self):
#     print("saveBT click")
#     now_time = date.datetime.now().strftime('%Y-%m-%d %H%M%S')
#     f = open(now_time + "log.txt", "a")
#     save_text = self.logbox.toPlainText()
#     f.write(save_text)
#     f.close()
#
# def text_edit_start(self):
#     for i in range(len(Device)):
#         log_text = device_type[i] + " : " + Device[i]
#         self.log_appand(str(log_text))
#
# def waitTimer(self):
#     print("Wait Timer")
#     for i in range(len(Device)):
#         if check_device[i] == False:
#             log_txt = str("FAIL Device : " + "\t" + device_type[i] + " " + Device[i])
#             self.log_appand(log_txt)
#     self.client.loop_stop()
#     self.client.disconnect()
#
#     for i in range(len(check_device)):
#         if Device[i] != "":
#             if check_device[i] == True:
#                 self.deviceOKcount[i] = self.deviceOKcount[i] + 1
#             else:
#                 self.deviceFailcount[i] = self.deviceFailcount[i] + 1
#
#     if False in check_device:
#         self.deviceFailcount[4] = self.deviceFailcount[4] + 1
#     else:
#         self.deviceOKcount[4] = self.deviceOKcount[4] + 1
#
#     for i in range(len(device_type)):
#         self.deviceLABELlist[i].setText(device_type[i] + "\t" + str(self.deviceOKcount[i]) + "    /    " + str(self.deviceFailcount[i]))
#     self.totalLABEL.setText("Total\t" + str(self.deviceOKcount[4]) + "    /    " + str(self.deviceFailcount[4]))
#
#     self.autologCount = self.autologCount + 1
#     if(self.autologCount >= 10):
#         self.autologCount = 0
#         self.saveBT_event()
#
#     self.comparison()
#
#
#
# def intervalTimer(self):
#     print("interval timer")
#     if self.mqttFlag == False:
#         self.connMQTTbroker(self.brokerTEXT.text())
#     time.sleep(1)
#     self.sample_start()
#     time_list = threading.Timer((int(time_info[1])*60)-2, self.intervalTimer)
#     time_list.start()
#     timer.append(time_list)
#     set_time = date.datetime.now() + date.timedelta(minutes=int(time_info[1]))
#     send_text = "Next Sampling Start Time : " + str(set_time.strftime('%Y-%m-%d %H:%M:%S'))
#     self.log_appand(send_text)
#
# def testTimer(self):
#     print("testTimer")
#     self.log_appand("Test Complete")
#     self.client.loop_stop()
#     self.client.disconnect()
#     for i in timer:
#         i.cancel()
#
# def mqttconnectTimer(self):
#     print("mqttconnectTimer")
#     if self.mqttFlag == False:
#         self.intervalTimer()
#
# def log_start(self):
#     print("Log Start...")
#     self.client1 = mqtt.Client()  # MQTT Client 오브젝트 생성
#     self.client1.on_connect = self.on_connect_log
#     self.client1.on_disconnect = self.on_disconnect_log
#     self.client1.connect(self.brokerTEXT.text())  # MQTT 서버에 연결
#     self.client1.loop_start()
#     for i in Device:
#         if i != "":
#             self.client1.publish("Entity/SHM/Node/"+i+"/OTA",'{"nId":"'+i+'","nT":"SHM","status":{"OP":"TestLog"},"timestamp":'+str(int(time.time()))+'}')
#
# def sample_start(self):
#     print("Sample_Start....")
#     self.log_appand("Sampleing Start")
#     PANID = self.panidTEXT.text()
#     self.client.publish("Entity/SHM/Node/" + PANID + "/OTA", '{"nId":"' + PANID + '","nT":"SHM","status":{"OP":"Sample"},"timestamp":' + str(int(time.time())) + '}')
#     for i in range(len(check_device)):
#         if Device[i] == "":
#             check_device[i] = True
#         else:
#             check_device[i] = False
#
#     time_list = threading.Timer(120, self.waitTimer)
#     # time_list = threading.Timer(30, self.waitTimer)    #Test Time
#     time_list.start()
#     timer.append(time_list)
#
# def connMQTTbroker(self, broker):
#     print("Run connMQTTbroker")
#
#     self.connectFlag = False
#     time_list = threading.Timer(60, self.mqttconnectTimer)
#     time_list.start()
#     timer.append(time_list)
#
#     if(self.mqttFlag == False):
#         print("Connect Broker")
#         self.log_appand("Connecting...")
#         self.client = mqtt.Client()  # MQTT Client 오브젝트 생성
#
#         self.client.on_log = self.on_log  # on_log callback 설정
#         self.client.on_message = self.on_message  # on_message callback 설정
#         self.client.on_connect = self.on_connect  # on_connect callback 설정
#         self.client.on_disconnect = self.on_disconnect #on_disconnect callback 설정
#         self.client.connect(broker)  # MQTT 서버에 연결
#
#         self.connectFlag = True
#
#         self.client.loop_start()    #MQTT Loop Start
#
# def on_log(self, *args):
#     print(args[3])
#
# def on_connect_log(self, *args):
#     print(args[3])
#     if args[3] == 0:
#         self.log_appand("Broker Connection Complete")
#
# def on_disconnect_log(self, *args):
#     print("Disconnect")
#     self.log_appand("Disconnect Broker\n")
#
# def on_connect(self, *args):
#     print(args[3])
#     if args[3] == 0:
#         self.log_appand("Broker Connection Complete")
#         self.mqttFlag = True
#         for i in Device:
#             if i != "":
#                 time.sleep(1)
#                 self.client.subscribe('Entity/SHM/Node/'+i+'/Device/Status')
#
# def on_disconnect(self, *args):
#     print("Disconnect")
#     self.log_appand("Disconnect Broker\n")
#     self.mqttFlag = False
#
# # 서버에게서 PUBLISH 메시지를 받을 때 호출되는 콜백
# def on_message(self, mqttc, obj, msg):
#     print("On_Message")
#     topic = msg.topic
#     mqtt_data = str(msg.payload)
#     for i in range(len(Device)):
#         if (Device[i] != "") and (topic.find(Device[i]) >= 0) and (mqtt_data.find('"GENERIC"') >= 0) and (check_device[i] == False):
#             print(Device[i] + "  GENERIC")
#             check_device[i] = True
#             send_text = "OK Device :" + "\t" + device_type[i] + " " + Device[i]
#             self.log_appand(send_text)
#             self.make_data_file(str(msg.payload), str(topic))
#     print("check deivce ", check_device)
#
#     if False in check_device:
#         print("list False")
#     else:
#         self.client.loop_stop()
#         self.client.disconnect()
#
# def log_appand(self, text):
#     now_time = date.datetime.now()
#     print_text = str(now_time.strftime('%Y-%m-%d %H:%M:%S')) + "\t" + text
#     self.logbox.append(print_text)
#
# def make_data_file(self, mqtt_data, topic):
#     split_topic = topic.split('/')
#     print(split_topic[3])
#     check_topic.append(split_topic[3])
#     f = open("checkDATA/now" + split_topic[3] + ".txt", 'w')
#     test_data2 = mqtt_data.split('"accelerometer":"')
#     print(test_data2)
#     test_data3 = test_data2[1].split('"}')
#     print(test_data3)
#     split_test = test_data3[0].split('n')
#     print(split_test)
#     delete_text = []
#     for i in range(0, len(split_test) - 1):
#         delete_text.append(split_test[i].rstrip('\\').rstrip('r').rstrip('\\'))
#         f.write(delete_text[i])
#         f.write("\n")
#     f.close()
#
# def comparison(self):
#     for i in check_topic:
#         print("Comparison" + i)
#         if os.path.isfile("checkDATA/pre" + i + ".txt"):
#             if filecmp.cmp("checkDATA/pre" + i + ".txt", "checkDATA/now" + i + ".txt"):
#                 print(i + "의 내용이 동일")
#                 self.log_appand(i + " Same Data")
#             else:
#                 print(i + "의 내용이 다름")
#         shutil.copyfile("checkDATA/now" + i + ".txt", "checkDATA/pre" + i + ".txt")
#     check_topic.clear()
#
# # make dir
# if not (os.path.isdir("checkDATA")):
#     os.makedirs(os.path.join("checkDATA"))

