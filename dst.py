
class DST:
    def __init__(self) -> None:
        pass

    def update(self, state, nlu_semantics):
        if "name" in nlu_semantics:         # 套餐名
            state.clear()

        if "sort" in nlu_semantics:
            slot = nlu_semantics["sort"]["value"]   # 检索用的条件字段
            if slot in state and state[slot]["operator"] == "==":
                del state[slot]
        for k, v in nlu_semantics.items():
            state[k] = v
        return state