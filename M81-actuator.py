#M81をアクチュエーターに合わせて結果を保存するためのプログラム。使い方は開始、終了地点を入力してヨーイドンで実行するだけ
#pip install lakeshoreでlakeshoreインストール必須。多分keyboardあたりがwindowsでしか動かないかも
from lakeshore import SSMSystem #M81のこと
from time import sleep
from math import sqrt
import csv,datetime,os,keyboard, time

print("Connect M81")
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


try:
    os.makedirs('M81-actuator-records',exist_ok=True) #open dir
    # CSVファイル設定
    now = datetime.datetime.today()
    hourstr = "_" + now.strftime("%H%M%S")
    filename = "M81-actuator_" + now.strftime("%Y%m%d") + hourstr + ".csv"
    #filepath = os.path.join('M81-actuator-records', filename)
    
    print("測定は**モードを使用して位置と速度を決定してください")
    start_point = float(input("開始地点を入力してください[mm]:"))
    end_point = float(input("終了地点を入力してください[mm]:"))
    speed = float(input("移動速度を入力してください[mm/s]:"))
    measure_interval_distance = float(input("測定したい間隔[mm]を入力してください:"))
    
    total_distance = end_point - start_point
    time_per_interval = measure_interval_distance / speed #各測定間隔の時間
    number_of_measurements = int(total_distance / measure_interval_distance) + 1 #測定回数(終了点も含むためプラス１)
    
    
    S1.enable() #S1(電流モジュール)を起動
    sleep(1)
    print("S1モジュール起動しました")
    
    with open(os.path.join("M81-actuator-records",filename), 'w', newline='') as f: #create CSV file
        writer = csv.writer(f)
        writer.writerow(["測定地点[mm]","R[V]","theta[Θ]"]) #最初の一行に説明を書き込む
        
        start_time = time.time()
        next_measurement_time = start_time
        
        for i in range(number_of_measurements):
            current_time = time.time()
            while current_time < next_measurement_time:
                time.sleep(next_measurement_time - current_time)  # 次の測定時刻まで待機
                current_time = time.time()
            
            current_position = start_point + (i * measure_interval_distance)# 現在の測定位置を計算
            #ロックインアンプデータ取得
            lock_in_magnitude = M1.get_lock_in_r()#LockinモードのRを取得
            lock_in_theta = M1.get_lock_in_theta()
            print(f"lock_in_magnitude:{lock_in_magnitude}")
            print(f"lock_in_theta:{lock_in_theta}")
            
            data = [current_position, lock_in_magnitude, lock_in_theta]
            writer.writerow(data)
            
            next_measurement_time += time_per_interval  #次の測定時間を設定
            
        # 最後のポイントが正確に終了地点でない場合、最後の測定を実施
        if current_position < end_point:
            #ロックインアンプデータ取得
            lock_in_magnitude = M1.get_lock_in_r()#LockinモードのRを取得
            lock_in_theta = M1.get_lock_in_theta()
            print(f"lock_in_magnitude:{lock_in_magnitude}")
            print(f"lock_in_theta:{lock_in_theta}")
            data = [current_position, lock_in_magnitude, lock_in_theta]
            writer.writerow(data)
        

# キーボード割り込みが発生した場合
except KeyboardInterrupt:
    print("ユーザーによってプログラムが中断されました。")
    S1.disable()

except Exception as e:
    print(e)

finally:
    S1.disable()
    f.close()