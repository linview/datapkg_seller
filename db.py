# pseudo db for NLU/DST
class MockedDB:
    def __init__(self) -> None:
        self.data = [
            {"name": "经济套餐", "price": 50, "data": 10, "requirement": None},
            {"name": "畅游套餐", "price": 180, "data": 100, "requirement": None},
            {"name": "无限套餐", "price": 300, "data": 1000, "requirement": None},
            {"name": "校园套餐", "price": 150, "data": 200, "requirement": "在校生"},
        ]

    def retrieve(self, **kwargs):
        if kwargs is None:
            return {}
        records = []

        for r in self.data:
            select = True
            if r["requirement"]:
                if "status" not in kwargs or kwargs["status"] != r["requirement"]:  # 非在校生
                    continue
            for k, v in kwargs.items():
                if k == "sort":
                    continue
                if k == "data" and v["value"] == "无上限":  
                    if r[k] != 1000:
                        select = False
                        break
                if "operator" in v:
                    if not eval(str(r[k]) + v["operator"] + str(v["value"])):
                        select = False
                        break
                elif str(r[k]) != str(v):
                    select = False
                    break
            if select:
                records.append(r)
        if len(records) <= 1:
            return records
        key = "price"       # 默认price为排序字段
        reverse = False     # 默认升序
        if "sort" in kwargs:
            key = kwargs['sort']['value']
            reverse = kwargs["sort"]["order"] == "descend"
        return sorted(records, key=lambda x: x[key], reverse=reverse)
    