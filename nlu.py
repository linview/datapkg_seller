import json
import os, copy
from utils import client

INSTRUCTION="""
你的任务是识别用户对手机流量套餐产品的选择条件
每种流量套餐包含三个属性：名称，月费价格，月流量
根据用户输入，识别用户在上述三个属性上的意图
"""
OUTPUT_FORMAT="""
按JSON格式输出
1. name(名称)字段为string类型,取值范围: 经济套餐，畅游套餐，无限套餐，校园套餐 或 null;

2. price(月费)字段为一个结构体 或 null, 包含两个字段:
2.1 operator, string类型, 取值范围: '<=', '>=', '=='
2.2 value, int类型，取值范围>=0
2.3 order, string类型，取值范围: "descend", "ascend"

3. data(流量)字段取值为一个结构体 或 None, 包含两个字段:
3.1 operator, string类型, 取值范围: '<=', '>=', '=='
3.2 value, int类型，取值范围>=0
3.3 order, string类型，取值范围: "descend", "ascend"

4. 用户意图可以包含按price 或 data排序, 用sort字段表示，取值为一个结构体:
4.1 结构体中 "order"="descend"表示从大到小降序排序，用"value"字段保存被排序的字段
4.2 结构体中 "order"="ascend"表示从小到大升序排序，用"value"字段保存被排序的字段

输出内容只包含用户提到的字段，不要猜测任何用户未直接提到的字段，不输数值为null的字段

"""
EXAMPLES="""
便宜的套餐：{"sort":{"order"="ascend","value"="price"}}
有没有不限流量的：{"data":{"operator":"==","value":"10086"}}
流量大的：{"sort":{"order"="descend","value"="data"}}
100G以上流量的套餐最便宜的是哪个:{"sort":{"order"="ascend","value"="price"},"data":{"operator":">=","value":100}}
月费不超过200的:{"price":{"operator":"<=","value":200}}
就要月费180那个套餐:{"price":{"operator":"==","value":180}}
经济套餐：{"name":"经济套餐"}
"""

class NLU:
    def __init__(self) -> None:
        self.prompt_template = f"""
        设定：
        {INSTRUCTION}
        输出格式：
        {OUTPUT_FORMAT}
        例如：
        {EXAMPLES}
        上下文：
        用户输入:
        __INPUT__
        """
    
    def _get_completion(self, prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,      # randomness, 0 is minimum
        )
        semantics = json.loads(response.choices[0].message.content)
        return {k: v for k, v in semantics.items() if v}

    def _sensorship(self, prompt, model="gpt-3.5-turbo"):
        response = client.moderations.create(
            input=prompt
        )
        moderation_output = response.results[0].categories
        def check_harms(categories):
            harm_issues = {}
            for k, v in categories.dict().items():
                if v is True:
                    harm_issues.update({k:v})
            return harm_issues
        harm_issues = check_harms(moderation_output)
        if len(harm_issues) == 0:
            return True
        print(f"{harm_issues=}")
        return False

    def parse(self, user_input):
        if not self._sensorship(user_input):
            return "检测到恶意信息，我无法回答"
        prompt = self.prompt_template.replace("__INPUT__", user_input)
        return self._get_completion(prompt)