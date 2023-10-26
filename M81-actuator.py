#M81をアクチュエーターに合わせて結果を保存するためのプログラム。使い方は開始、終了地点を入力してヨーイドンで実行するだけ
#pip install lakeshoreでlakeshoreインストール必須。多分keyboardあたりがwindowsでしか動かないかも
from lakeshore import SSMSystem #M81のこと
from time import sleep
from math import sqrt
import csv,datetime,os,keyboard

M81 = SSMSystem() #初期値ではUSBから接続、ip指定でTCPで接続
#M81=SSMSystem.connect_tcp('10.10.10.13',7777, 100) #多分これでethernetから接続する

S1 = M81.get_source_module(1) #ソースモジュール
M1 = M81.get_measure_module(1) #計測モジュール

S1.set_shape('SINUSOID') #sin波のこと
S1.set_frequency(10000) #周波数[Hz]
S1.set_current_amplitude(0.01) #電流[A]
S1.set_current_offset(0)
S1.configure_i_range(0, max_ac_level=0.1) #Range設定(autoを使うか、max_level,max_ac_level,max_dc_level)どれか一つ指定
S1.set_cmr_source('INTernal') #CMRのソースを設定
S1.enable_cmr() #CMRを有効化

#advanced setting
S1.use_ac_coupling() #カップリングをACに設定

M1.setup_lock_in_measurement('S1', 0.1) #S1の周波数を参照信号にし、timeconstantを100msに設定

#端からの距離
distance = 50

#csv setting
now = datetime.datetime.today()
hourstr = "_" + now.strftime("%H%M%S")
filename = "M81-actuator_" + now.strftime("%Y%m%d") + hourstr + ".csv"

try:
    os.makedirs('M81-actuator-records',exist_ok=True) #open dir
    with open(os.path.join('M81-actuator-records',filename), 'a', newline= '') as f: #create CSV file
        writer = csv.writer(f)
        writer.writerow(["距離[mm]","R[V]","theta[Θ]"])
    S1.enable() #S1(電流モジュール)を起動
    
    A = float(input("開始地点を入力してください[mm]:"))
    B = float(input("終了地点を入力してください[mm]:"))
    speed = float(input("速度を入力してください:"))#速度はmm/sで欲しいけどどうなってるかわからん
    space = float(input("測定したい間隔[mm]を入力してください:"))
    
    while True:

        sleep(1.5)

        lock_in_magnitude = M1.get_lock_in_r()#LockinモードのRを取得
        lock_in_theta = M1.get_lock_in_theta()
        print(f"lock_in_magnitude:{lock_in_magnitude}")
        print(f"lock_in_theta:{lock_in_theta}")

        #enterが押されるごとにcsvに書き込む
        if keyboard.is_pressed("enter"):
            print(f"距離:{distance}mm R:{lock_in_magnitude:.7f} theta:{lock_in_theta:.7f}")
            data = [distance,lock_in_magnitude,lock_in_theta]
            writer.writerow(data)
            distance += 2

except KeyboardInterrupt:
    S1.disable() #S1を停止
    f.close
    pass

except Exception as e:
    print(e)
    pass
