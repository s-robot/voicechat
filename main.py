import os
import random
import threading
import time
from queue import Queue
from threading import Thread

import pyaudio
import simpleaudio as sa
import speech_recognition as sr

import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_KEY or ""
from gpt_service import GptService
from noun_service import noun_list
from vox_service import VoxService

gs = GptService()
vs = VoxService()


def look_for_audio_input():
    """
    オーディオIF一覧
    """
    pa = pyaudio.PyAudio()

    for i in range(pa.get_device_count()):
        print(pa.get_device_info_by_index(i))
        print()

    pa.terminate()


def play_noun_or_fill(filler_queue: Queue):
    if not filler_queue.empty():
        fetched_index, file = filler_queue.get_nowait()
        print(f"start play voice for index {fetched_index}")
        play_chat(file)
    else:
        play_fill()


def play_fill():
    fillvoices = ["そっかそっか", "そうかぁー", "そうだねー", "えっとぉー", "えっとねぇー", "うーんとね"]
    wave_obj = sa.WaveObject.from_wave_file(f"fill_voice/{random.choice(fillvoices)}.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()


def play_exit():
    exitvoices = ["じゃあね", "またね", "元気でね", "また話そうね", "バイバイ"]
    wave_obj = sa.WaveObject.from_wave_file(f"fill_voice/{random.choice(exitvoices)}.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()


def play_chat(file):
    wave_obj = sa.WaveObject.from_wave_file(file)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def fetch_voice(q: Queue, text, index):
    result = vs.voxvoice(text, 0)
    q.put_nowait((index, result))
    print(f"Fetched voice for index {index}")


def create_noun_fill(q: Queue, text, index):
    nlist = noun_list(text)
    print(nlist)
    if len(nlist) > 0:
        noun = random.choice(nlist)
        nounfills = [f"あー{noun}かぁ", f"{noun}ねぇ", f"{noun}かぁ", f"{noun}の話ね", f"おー{noun}ね"]
        nounfill = random.choice(nounfills)
        threading.Thread(target=fetch_voice, args=(q, nounfill, index)).start()
        print(f"Add fetch nounfill: {nounfill}")


def text_fetcher(recog: sr.Recognizer, audio: sr.AudioData, queue: Queue, threads: list[Thread], error_queue: Queue, filler_queue: Queue):
    text: str = ""
    try:
        text = recog.recognize_openai(audio, model="whisper-1")  # type: ignore
    except Exception as e:
        print(f"Error: {e}")
        error_queue.put_nowait("🐙🙉聞き取りエラー🙉🐙")

    if text == "":
        error_queue.put_nowait("🐙🙉聞き取りエラー🙉🐙")
        return

    print(f"user: {text}")
    if "じゃあね" in text or "またね" in text or "バイバイ" in text:
        error_queue.put_nowait("👋see you!!👋")
        return

    threading.Thread(target=create_noun_fill, args=(filler_queue, text, 999)).start()

    res = gs.chat(text, prompt="あなたはuserの友達のIT系大学生「ソータ」として振る舞ってください。若い女の子の口調で、一人称は「ソータ」です。", model="gpt-3.5-turbo-0125")
    index = 0
    result = ""
    for text in res:
        print(f"Text fetched: {text}")
        result += text
        thread = threading.Thread(target=fetch_voice, args=(queue, text, index))
        threads.append(thread)
        thread.start()
        print(f"Add fetch thread for index {index}")
        index += 1
    gs.addres(result)


def process_text(recog: sr.Recognizer, audio: sr.AudioData) -> bool:
    queue: Queue = Queue()
    filler_queue: Queue = Queue()
    error_queue: Queue = Queue()
    threads: list[Thread] = []
    played_indexes: set = set()

    # テキストの取得スレッドを開始
    threading.Thread(target=text_fetcher, args=(recog, audio, queue, threads, error_queue, filler_queue)).start()

    # フェッチした音声を順に再生
    isFirst = True
    while isFirst and error_queue.empty():
        play_noun_or_fill(filler_queue)
        while any(thread.is_alive() for thread in threads) or not queue.empty():
            if not queue.empty():
                fetched_index, file = queue.get_nowait()
                if fetched_index == len(played_indexes):
                    isFirst = False
                    print(f"start play voice for index {fetched_index}")
                    play_chat(file)
                    played_indexes.add(fetched_index)
                else:
                    queue.put_nowait((fetched_index, file))
            time.sleep(0.1)
    while not error_queue.empty():
        e = error_queue.get_nowait()
        print(e)
        if e == "👋see you!!👋":
            play_exit()
            return False
    return True


def realtime_textise():
    # 音声入力
    while True:
        r = sr.Recognizer()
        r.energy_threshold = 1000
        with sr.Microphone() as source:
            print("発話どうぞ💬")
            audio = r.listen(source)
        if not process_text(r, audio):
            break


if __name__ == "__main__":
    look_for_audio_input()
    realtime_textise()
