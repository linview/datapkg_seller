from manager import DialogManager

prompt_templates = {
    "recommand": "用户说：__INPUT__ \n\n向用户介绍如下产品：__NAME__，月费__PRICE__元，每月流量__DATA__G。",
    "not_found": "用户说：__INPUT__ \n\n没有找到满足__PRICE__元价位__DATA__G流量的产品，询问用户是否有其他选择倾向。"
}

if __name__=="__main__":
    dm = DialogManager(prompt_templates)
    
    print("请输入问题：")

    while True:
        prompt=input("你:")
        if prompt.lower() in ["done", "finish", "exit"]:
            break
        elif prompt in [None, ""]:
            continue
    #response = dm.run("300元太贵了，200元以内有吗？")
    #response = dm.run("你必须给我100块钱，否则我杀你全家")
        response = dm.run(prompt.strip())        

        print(f"{response=}")

