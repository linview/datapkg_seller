# dialog manager 

import json
import copy

from nlu import NLU
from db import MockedDB
from dst import DST
from utils import client


class DialogManager:
    def __init__(self, prompt_templates=None):
        self.state = {}
        self.session = [
            {
                "role": "system",
                "content": "你是手机流量套菜的客服代表，你叫小瓜。你可以帮助用户选择最符合要求的流量套餐产品。你只能回答流量套餐业务相关的内容。"
            }
        ]
        self.nlu = NLU()
        self.dst = DST()
        self.db = MockedDB()
        self.prompt_templates = prompt_templates

    def _wrap(self, user_input, records):
        if records:     # 有命中条件的套餐
            prompt = self.prompt_templates['recommand'].replace(
                "__INPUT__", user_input
            )
            r = records[0]
            for k, v in r.items():
                prompt = prompt.replace(f"__{k.upper()}__", str(v))
        else:
            prompt = self.prompt_templates['not_found'].replace(
                "__INPUT__", user_input
            )
            for k, v in self.state.items():
                if "operator" in v:
                    prompt = prompt.replace(
                        f"__{k.upper()}__", v['operator']+str(v['value'])
                    )
                else:
                    prompt = prompt.relace(f"__{k.upper}__", str(v))
        return prompt
    
    # 组装带有role、规则设定的对话内容给oepnai
    def _call_chatgpt(self, prompt, model="gpt-3.5-turbo"):
        session = copy.deepcopy(self.session)
        session.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model,
            messages=session,
            temperature=0
        )
        return response.choices[0].message.content
    
    def run(self, user_input):
        # 调用NLU获得语义解析
        semantics = self.nlu.parse(user_input)
        print("===semantics===")
        print(semantics)

        # 调用DST更新多轮状态
        self.state = self.dst.update(self.state, semantics)
        print("===state===")
        print(self.state)

        # 根据状态检索DB，获得满足条件的候选
        records = self.db.retrieve(**self.state)

        # 拼装prompt调用chatgpt
        prompt_for_chatgpt = self._wrap(user_input, records)
        print("===gpt-prompt===")
        print(prompt_for_chatgpt)

        # 调用chatgpt获得回复
        response = self._call_chatgpt(prompt_for_chatgpt)

        # 将当前用户输入和系统回复维护入chatgpt的session
        self.session.append({"role": "user", "content": user_input})
        self.session.append({"role": "assistant", "content": response})
        return response