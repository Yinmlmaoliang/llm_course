import json
import openai
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# API配置
API_KEY = 'sk-FzWaHt19fi1h3StQr98xblqLoWR4jvl8I37LCNCkJWqxxxx'  # 替换为实际的API密钥 获取地址https://open.xiaojingai.com
BASE_URL = 'https://open.xiaojingai.com/v1/'
MODEL = 'gpt-4o'

# 设置 API 密钥和基础 URL
openai.api_key = API_KEY
openai.base_url = BASE_URL

# 创建一个线程锁用于同步打印
print_lock = threading.Lock()

# 创建一个计数器和锁来跟踪进度
counter = 0
counter_lock = threading.Lock()

def ask_gpt_question(prompt):
    max_retries = 3
    for _ in range(max_retries):
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(1)  # 短暂等待后重试
    return None

def update_qa_pair(qa_pair, index, total):
    global counter
    prompt = f"为了优化一个大型语言模型，我正在收集关于学术论文撰写的问答数据，目的是让模型能够模仿大学教授对学生关于学术论文撰写对的提问做出答复。请探讨以下关于学术论文写作的问题，确保提供清晰、逻辑严密的回答，以帮助学生理解和应用相关概念：{qa_pair['input']}"
    new_answer = ask_gpt_question(prompt)
    
    with print_lock:
        with counter_lock:
            counter += 1
            current_count = counter
        print(f"\n处理第 {current_count}/{total} 个问答对")
        print(f"原问题: {qa_pair['input']}")
        print(f"原答案: {qa_pair['output']}")
        if new_answer:
            qa_pair['output'] = new_answer
            print(f"新答案: {new_answer}")
        else:
            print("获取新答案失败，保留原答案")
    
    return qa_pair

def update_dataset(input_file, output_file, max_workers=10):
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    total = len(dataset)
    updated_dataset = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_qa = {executor.submit(update_qa_pair, qa_pair, i, total): i for i, qa_pair in enumerate(dataset)}
        for future in as_completed(future_to_qa):
            updated_qa_pair = future.result()
            updated_dataset.append(updated_qa_pair)

    # 保存更新后的数据集
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_dataset, f, ensure_ascii=False, indent=2)

    print(f"\n更新后的数据集已保存到 {output_file}")
    print(f"原始数据集大小: {len(dataset)}")
    print(f"更新后数据集大小: {len(updated_dataset)}")

if __name__ == "__main__":
    input_file = "/home/user/Python_project/llm_course/expanded_customdata.json"  # 替换为实际的输入文件名
    output_file = "/home/user/Python_project/llm_course/updated_customdatamore.json"
    update_dataset(input_file, output_file)