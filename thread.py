import time
import threading
import math

class Task:
    now = 0
    isContinue = True
    
    def __init__(self, json, tools):
        self.json = json
        self.tools = tools

    def execute(self):
        self.tools.setPower(False)
        while len(self.json['steps']) > self.now :
            print("Step"+str(self.now)+" Length: "+ str(len(self.json['steps'])))
            step = self.json['steps'][self.now]
            

            if step['type'] == 'heat':
                count = 0
                # TTSで読み上げ処理
                self.tools.TTS(step['description'])
                time.sleep(5)
                # 加熱処理
                while self.tools.getTemp() <= step['heat_strength']-5:
                    print(self.tools.getTemp())
                    self.tools.setPower(True)
                    if count % 15 == 0:
                        self.tools.TTS("目標温度まで、あと{}℃".format(math.floor(step['heat_strength'] - 5 - self.tools.getTemp())))
                    time.sleep(1)
                    count += 1

                self.tools.TTS("目標温度に到達しました。")
                time.sleep(3)

                # 温度維持
                self.tools.TTS("{}秒間この温度を維持します。".format(step['duration']))
                start = time.time()
                print("----")
                print(time.time() - start)
                self.isContinue = True
                print(self.isContinue)
                while time.time() - start < step['duration'] and self.isContinue:
                    print(self.tools.getTemp())
                    temp = self.tools.getTemp()
                    if step['heat_strength'] + 1 < temp:
                        self.tools.setPower(False)
                    elif step['heat_strength'] - 1 > temp:
                        self.tools.setPower(True)
                    time.sleep(1)
                self.tools.setPower(False)
                
            elif step['type'] == 'add':
                # 追加処理
                weight_previous = 0
                count = 0
                self.tools.TTS("調整中です。デバイスを動かさないでください。")
                time.sleep(3)
                self.tools.beep()
                self.tools.tareWeight()
                time.sleep(3)

                # TTSで読み上げ処理
                self.tools.TTS(step['description'])
                time.sleep(5)

                self.isContinue = True
                print(self.isContinue)
                while self.isContinue:
                    print("--")

                    weight = self.tools.getWeight()
                    print("Now: {}C".format(weight))
                    print("Difer from previous: {}C".format(abs(weight - weight_previous)))
                    if abs(weight - weight_previous) < 3:
                        if step['add_grams'] - 15 < weight and step['add_grams'] + 15 > weight:
                            self.tools.beep()
                            time.sleep(1.5)
                            self.tools.TTS('{}グラム。適量です。'.format(math.floor(weight)))
                            time.sleep(3)
                            break
                    if count % 4 == 0:
                        self.tools.TTS('{}グラム'.format(math.floor(weight)))
                    weight_previous = weight
                    count += 1
                    time.sleep(1)
            else:
                self.tools.TTS(step['description'])
                time.sleep(4)
                self.tools.TTS('完了しましたらボタンを押してください。')
                self.isContinue = True
                print(self.isContinue)
                while self.isContinue:
                    time.sleep(0.1)

            time.sleep(2)
            self.now = self.now + 1
        self.tools.TTS('料理が出来上がりました！')
        






    def record(self):
        count = 0
        self.json = {}
        self.json["steps"] = []

        def recordTemp():
            print("温度を記録")
            self.tools.TTS("加熱処理を記録します")
            while True:
                print("温度変化: {}".format(self.tools.getTemp() - zero_temp))
                if self.tools.isButton():
                    self.json["steps"].append({
                        "type": "heat",
                        "description": "加熱する",
                        "heat_strength": math.floor(self.tools.getTemp()),
                        })
                    self.tools.TTS("加熱処理を完了します。")
                    zero_temp = self.tools.getTemp()
                    print(json)
                    break
                time.sleep(1)
            time.sleep(4)
        def recordWeight(): 
            print("重量を記録")
            self.tools.TTS("追加処理を記録します")
            while True:
                print("重量変化: {}".format(self.tools.getWeight()))
                if self.tools.isButton():
                    self.json["steps"].append({
                        "type": "add",
                        "description": "追加する",
                        "add_grams": math.floor(self.tools.getWeight()),
                        })
                    self.tools.tareWeight()
                    self.tools.TTS("追加処理を完了します。")
                    print(self.json)
                    break
                time.sleep(1)
            time.sleep(4)
        while True:
            self.tools.TTS("作業を開始してください。")
            start = time.time()
            zero_temp = self.tools.getTemp()
            self.tools.tareWeight()
            while True:
                print("温度変化: {}".format(self.tools.getTemp() - zero_temp))
                print("重量変化: {}".format(self.tools.getWeight()))
                if self.tools.getTemp() - zero_temp > 10:
                    recordTemp()

                elif self.tools.getWeight() > 50:
                    recordWeight()
                elif self.tools.isButton():
                    self.tools.TTS("記録を終了します。")
                    print(self.json)
                    return self.json
                time.sleep(1)
