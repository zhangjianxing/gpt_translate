import os
import time

import openai
import sqlitedict
from openai import OpenAI

from ai_translator.utils import LOG
from .model import Model


class OpenAIModel(Model):
    sqlitedict = sqlitedict.SqliteDict('./my_db.sqlite', autocommit=True)

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def make_request(self, prompt):
        if OpenAIModel.sqlitedict.get(prompt):
            print(f"dist result: {prompt}")
            return OpenAIModel.sqlitedict[prompt], True
        result, success = self._make_request(prompt)
        if success:
            OpenAIModel.sqlitedict[prompt] = result
            OpenAIModel.sqlitedict.commit(True)
        return result, success

    def _make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt-3.5-turbo":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message.content.strip()
                else:
                    response = self.client.completions.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.RateLimitError as e:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except openai.APIConnectionError as e:
                print("The server could not be reached")
                print(
                    e.__cause__)  # an underlying Exception, likely raised within httpx.            except requests.exceptions.Timeout as e:
            except openai.APIStatusError as e:
                print("Another non-200-range status code was received")
                print(e.status_code)
                print(e.response)
            except Exception as e:
                raise Exception(f"发生了未知错误：{e}")
        return "", False
