import io
import json
import uuid
import wave

import pyaudio
import requests

import settings


class VoxService:
    def __init__(self) -> None:
        pass

    def speakers(self):
        response1 = requests.get(
            f"http://{settings.VOX_URL}:{settings.VOX_PORT}/speakers",
        )
        result = json.loads(s=response1.content)
        for speaker in result:
            print(speaker["name"])
            for styles in speaker["styles"]:
                print(f"    id: {styles['id']}    {styles['name']}")

    def voxvoice(self, text: str, voice: int, save: bool = False):
        params = (
            ("text", text),
            ("speaker", voice),
        )
        try:
            response1 = requests.post(
                f"http://{settings.VOX_URL}:{settings.VOX_PORT}/audio_query",
                params=params,
            )
        except:
            pass

        # vox synth
        headers = {"Content-Type": "application/json"}
        try:
            response2 = requests.post(
                f"http://{settings.VOX_URL}:{settings.VOX_PORT}/synthesis",
                headers=headers,
                params=params,
                data=json.dumps(response1.json()),
            )
        except:
            pass

        buff = io.BytesIO(response2.content)
        buff.seek(0)

        # ローカルに保存する場合
        if save:
            fname = f"fill_voice/{text}.wav"
            with open(fname, "wb") as f:
                f.write(response2.content)
            return fname
        return buff


if __name__ == "__main__":
    vs = VoxService()
    buff = vs.voxvoice("隣の客はよく柿食う客だ", 0)
    buff.seek(0)
    wf = wave.open(buff, 'rb')
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)
    stream.stop_stream()
    stream.close()
    pa.terminate()
    wf.close()
