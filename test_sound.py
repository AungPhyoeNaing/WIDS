import ctypes, os
path = os.path.abspath(r'voice_audios\Jarvis-(MCU)-J.A.R.V.I.S-2026-07-14-23-40-Hello-,-Sir-,-Our-Intrusion-Detection-System-is.mp3')
print('path:', path)

error_buf = ctypes.create_unicode_buffer(256)

res1 = ctypes.windll.winmm.mciSendStringW(f'open "{path}" alias jarvis_voice', None, 0, None)
print('res1 (open):', res1)
if res1 != 0:
    ctypes.windll.winmm.mciGetErrorStringW(res1, error_buf, 256)
    print('error1:', error_buf.value)

res2 = ctypes.windll.winmm.mciSendStringW('play jarvis_voice wait', None, 0, None)
print('res2 (play):', res2)
if res2 != 0:
    ctypes.windll.winmm.mciGetErrorStringW(res2, error_buf, 256)
    print('error2:', error_buf.value)
