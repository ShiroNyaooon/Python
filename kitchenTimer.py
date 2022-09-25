# ----------------------------------------------------------------
#  キッチンタイマー (ShiroNyaooon)
# ----------------------------------------------------------------
#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

IS_WAIT   = False
PIN_BEEP  = 18
PIN_SDI   = 17
PIN_RCLK  = 22
PIN_SRCLK = 27
PIN_BTNUP = 20
PIN_START = 21
TIMMER_COUNT = 0
TIMMER_STATUS = 0  # 0:WAIT 1:START 2:END

# ----------------------------------------------------------------
#  初期化処理
# ----------------------------------------------------------------
def init():
	
	GPIO.setmode(GPIO.BCM)
	# ブザー
	GPIO.setup(PIN_BEEP, GPIO.OUT, initial=GPIO.HIGH)
	# 7セグメントディスプレイ
	GPIO.setup(PIN_SDI, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(PIN_RCLK, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(PIN_SRCLK, GPIO.OUT, initial=GPIO.LOW)
	# タイマー加算ボタン
	GPIO.setup(PIN_BTNUP, GPIO.IN)
	GPIO.add_event_detect(PIN_BTNUP, GPIO.FALLING, callback=countUp)
	# タイマー開始ボタン
	GPIO.setup(PIN_START, GPIO.IN)
	GPIO.add_event_detect(PIN_START, GPIO.FALLING, callback=timmerStart)
	
	
# ----------------------------------------------------------------
#  7セグメントディスプレイに表示する
# ----------------------------------------------------------------
# INPUT1: 表示する値
# ----------------------------------------------------------------
def lightSegmentDisplay(oNumber):

	# 初期値
	val = 0

	# 74HC595用の値に変換する
	#
	# +----02----+  x02(02):  7セグＡ
	# |          |  x04(04):  7セグＢ
	# 40        04  x08(08):  7セグＣ
	# |          |  x10(16):  7セグＤ
	# +----80----+
	# |          |  x20(32):  7セグＥ
	# 20        08  x40(64):  7セグＦ
	# |          |  x80(128): 7セグＧ
	# +----10----+
	
	if oNumber == 1:
		val = 4+8
	elif oNumber == 2:
		val = 2+4+128+32+16
	elif oNumber == 3:
		val = 2+4+128+8+16
	elif oNumber == 4:
		val = 64+128+4+8
	elif oNumber == 5:
		val = 2+64+128+8+16
	elif oNumber == 6:
		val = 2+64+32+16+8+128
	elif oNumber == 7:
		val = 64+2+4+8
	elif oNumber == 8:
		val = 2+4+8+16+32+64+128
	elif oNumber == 9:
		val = 2+64+128+4+8
	elif oNumber == 0:
		val = 2+4+8+16+32+64

	# ディスプレイ表示
	for i in range(0, 8):	
		GPIO.output(PIN_SDI, 0x80 & (val << i))
		GPIO.output(PIN_SRCLK, GPIO.HIGH)
		time.sleep(0.001)
		GPIO.output(PIN_SRCLK, GPIO.LOW)
	GPIO.output(PIN_RCLK, GPIO.HIGH)
	time.sleep(0.001)
	GPIO.output(PIN_RCLK, GPIO.LOW)

# ----------------------------------------------------------------
#  メイン処理
# ----------------------------------------------------------------
def main():
	global TIMMER_COUNT
	global TIMMER_STATUS

	while True:
		countDown()
		time.sleep(0.1)

# ----------------------------------------------------------------
#  タイマーのカウントアップ
# ----------------------------------------------------------------
def countUp(ev=None):
	global IS_WAIT
	global TIMMER_COUNT
	global TIMMER_STATUS
	
	if TIMMER_STATUS != 2 and IS_WAIT == False:
		IS_WAIT = True
		TIMMER_COUNT += 1
		beepPush()
		lightSegmentDisplay(TIMMER_COUNT)
		if TIMMER_COUNT >= 10:
			TIMMER_COUNT = 0
		time.sleep(0.3)
		IS_WAIT = False

# ----------------------------------------------------------------
#  タイマーのカウントダウン
# ----------------------------------------------------------------
def countDown():
	global TIMMER_COUNT
	global TIMMER_STATUS

	# タイマーカントダウン中
	if TIMMER_STATUS == 1:
		time.sleep(1.0)  # 1分区切りの場合は60に変更する
		TIMMER_COUNT -= 1
		lightSegmentDisplay(TIMMER_COUNT)
		
		if TIMMER_STATUS == 1 and TIMMER_COUNT <= 0:
			TIMMER_STATUS = 2
	
	# アラート中
	elif TIMMER_STATUS == 2:
		beepPush()

# ----------------------------------------------------------------
#  タイマー開始
# ----------------------------------------------------------------
def timmerStart(ev=None):
	global IS_WAIT
	global TIMMER_COUNT
	global TIMMER_STATUS

	if IS_WAIT == False:
		IS_WAIT = True
		
		# タイマー開始
		if TIMMER_STATUS == 0 and TIMMER_COUNT >= 1:
			beepPush()
			TIMMER_STATUS = 1
		
		# タイマー中断
		elif TIMMER_STATUS == 1:
			beepPush()
			TIMMER_STATUS = 0
		
		# アラート終了
		elif TIMMER_STATUS == 2:
			beepPush()
			TIMMER_STATUS = 0
			lightSegmentDisplay(99)
		
		time.sleep(0.3)
		IS_WAIT = False

# ----------------------------------------------------------------
#  プッシュ音
# ----------------------------------------------------------------
def beepPush():
	GPIO.output(PIN_BEEP, GPIO.LOW)
	time.sleep(0.1)
	GPIO.output(PIN_BEEP, GPIO.HIGH)

# ----------------------------------------------------------------
#  直接実行された場合のみ実行する
# ----------------------------------------------------------------
if __name__ == '__main__':

	init()
	try:
		main()
	except KeyboardInterrupt:
		# Ctrl+Cによるプログラム停止時
		lightSegmentDisplay(99)
		GPIO.cleanup()
