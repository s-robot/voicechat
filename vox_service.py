import io
import json
import uuid

import requests
import simpleaudio as sa

import gpt_env


class VoxService:
    def __init__(self) -> None:
        pass

    def speakers(self):
        response1 = requests.get(
            f"http://{gpt_env.vox_url}:{gpt_env.vox_port}/speakers",
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
                f"http://{gpt_env.vox_url}:{gpt_env.vox_port}/audio_query",
                params=params,
            )
        except:
            pass

        # vox synth
        headers = {"Content-Type": "application/json"}
        try:
            response2 = requests.post(
                f"http://{gpt_env.vox_url}:{gpt_env.vox_port}/synthesis",
                headers=headers,
                params=params,
                data=json.dumps(response1.json()),
            )
        except:
            pass

        buff = io.BytesIO(response2.content)
        buff.seek(0)
        # wave_obj = sa.WaveObject.from_wave_file(buff)
        # play_obj = wave_obj.play()
        # play_obj.wait_done()

        # ローカルに保存する場合
        if save:
            fname = f"fill_voice/{text}.wav"
            with open(fname, "wb") as f:
                f.write(response2.content)
            return fname
        return buff


if __name__ == "__main__":
    vs = VoxService()
    # vs.speakers()
    vs.voxvoice("隣の客はよく柿食う客だ", 0)
