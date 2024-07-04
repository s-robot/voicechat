import json
import time
from typing import Generator

import openai
from openai.types.chat import ChatCompletionAssistantMessageParam, ChatCompletionMessageParam, ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

import settings


class GptServiceError(Exception):
    """Custom exception class for GptService errors."""

    def __init__(self, message="GPT service failed after 3 attempts"):
        self.message = message
        super().__init__(self.message)


class GptService:
    def __init__(self) -> None:
        openai.api_key = settings.OPENAI_KEY
        self.messages: list[ChatCompletionMessageParam] = []

    def system_message(self, content: str):
        return ChatCompletionSystemMessageParam(content=content, role="system")

    def user_message(self, content: str):
        return ChatCompletionUserMessageParam(content=content, role="user")

    def assistant_message(self, content: str):
        return ChatCompletionAssistantMessageParam(content=content, role="assistant")

    def genarate(self, messages: list[ChatCompletionMessageParam], model: str) -> Generator[str, None, None]:
        attempts = 0
        while attempts < 3:
            try:
                res = openai.chat.completions.create(
                    timeout=30,
                    model=model,
                    messages=messages,
                    max_tokens=512,
                    stream=True,
                )
                result = ""
                for chunk in res:
                    if chunk.choices[0].finish_reason == "stop":
                        break
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                print(f"Attempt {attempts + 1} failed: {e}")
                attempts += 1
                if attempts < 3:
                    print("Retrying in 3 seconds...")
                    time.sleep(3)
                else:
                    print("Timeout error after 3 attempts.")
                    raise GptServiceError()
        raise GptServiceError()

    def onetime(self, input: str, prompt: str = "You are a helpful assistant.", model="gpt-4o") -> str:
        messages: list[ChatCompletionMessageParam] = []
        messages.append(self.system_message(prompt))
        messages.append(self.user_message(input))
        result = ""
        res = self.genarate(self.messages, model)
        for r in res:
            result += r
        if result is None:
            result = ""
        return result

    def chat(self, input: str, prompt: str = "You are a helpful assistant.", model="gpt-4o"):
        if self.messages == []:
            self.messages.append(self.system_message(prompt))
        self.messages.append(self.user_message(input))
        res = self.genarate(self.messages, model)
        buffer = ""
        separators = ["、", "。", "？", "！", "\n"]
        for r in res:
            buffer += r
            if any(sep in buffer for sep in separators):
                buffer = buffer.strip()
                if buffer != "":
                    yield buffer
                buffer = ""
        buffer = buffer.strip()
        if buffer != "":
            yield buffer
        return

    def addres(self, res: str):
        self.messages.append(self.assistant_message(res))

    def clearchat(self):
        self.messages = []


if __name__ == "__main__":
    isStart = True
    start_time = time.perf_counter()
    gs = GptService()
    res = gs.chat("SFCについて教えて", model="gpt-4o")
    for r in res:
        print(r)
        if isStart:
            execution_time = time.perf_counter() - start_time
            print(execution_time)
            isStart = False
    # while True:
    #     usertext = input("GPT >>")
    #     res = gs.chat("こんにちは")
    #     for r in res:
    #         print(r)
