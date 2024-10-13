import json
import openai
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# API配置
API_KEY = 'sk-FzWaHt19fi1h3StQr98xblqLoWR4jvl8I37LCNxxxx'  # 替换为实际的API密钥 获取地址https://open.xiaojingai.com
BASE_URL = 'https://open.xiaojingai.com/v1/'
MODEL = 'gpt-4o'

# 在模块级别设置 API 密钥和基础 URL
openai.api_key = API_KEY
openai.base_url = BASE_URL

# 统计数据
successful_expansions = 0
failed_expansions = 0
total_new_qa_pairs = 0
unsuccessful_questions = []

# 创建一个线程锁
lock = threading.Lock()

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

def parse_json_with_fallback(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fixed_text = text
        fixed_text = re.sub(r'"},"\n', '"},\n', fixed_text)
        fixed_text = re.sub(r'"}"\n', '"}\n', fixed_text)
        fixed_text = re.sub(r'}"$', '}', fixed_text)
        fixed_text = re.sub(r'}]}]"', '}]}]', fixed_text)
        fixed_text = re.sub(r']"\n?$', ']', fixed_text)
        fixed_text = re.sub(r'}]},"', '}]},', fixed_text)
        fixed_text = re.sub(r'}]}\"', '}]}', fixed_text)
        # 移除JSON对象外的多余字符
        start = fixed_text.find('{')
        end = fixed_text.rfind('}') + 1
        if start != -1 and end != -1:
            fixed_text = fixed_text[start:end]
        # 尝试再次解析
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            return None

def process_qa_pair(qa_pair):
    global successful_expansions, failed_expansions, total_new_qa_pairs
    max_retries = 3
    retries = 0
    while retries < max_retries:
        prompt = f"""
给定一个关于学术写作的问题，请生成三个不同的问题变体。每个问题应通过同义词替换或语序调整来改写。原始问题：{qa_pair['input']}。生成的问题应简洁、清晰，并符合学术背景。请以JSON格式返回，每个问题以"问题x"作为键，例如：{{"问题1": "...", "问题2": "...", "问题3": "..."}}。
"""
        response = ask_gpt_question(prompt)
        if response:
            # print(f"Response: {response}")
            parsed_json = parse_json_with_fallback(response)
            if parsed_json:
                new_qa_pairs = []
                for key in parsed_json:
                    question = parsed_json[key].strip()
                    new_qa_pairs.append({"instruction": "", "input": question, "output": ""})
                new_qa_pairs.append(qa_pair)
                with lock:
                    successful_expansions += 1
                    total_new_qa_pairs += len(new_qa_pairs)
                return new_qa_pairs
        retries += 1
    # 如果多次尝试仍失败，记录失败信息
    with lock:
        failed_expansions += 1
        unsuccessful_questions.append(qa_pair['input'])
    return [qa_pair]

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def expand_dataset(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    expanded_dataset = []
    temp_output_file = output_file + '.temp'
    
    successful_expansions = 0
    failed_expansions = 0
    total_new_qa_pairs = 0
    
    with tqdm(total=len(dataset), desc="Processing QA pairs") as pbar:
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_qa = {executor.submit(process_qa_pair, qa_pair): qa_pair for qa_pair in dataset}
            for future in as_completed(future_to_qa):
                result = future.result()
                if result:
                    expanded_dataset.extend(result)
                    with lock:
                        total_new_qa_pairs += len(result)
                        successful_expansions += 1
                else:
                    with lock:
                        failed_expansions += 1
                
                pbar.update(1)
                
                # 实时更新进度信息
                pbar.set_postfix({
                    'Successful': successful_expansions,
                    'Failed': failed_expansions,
                    'New QAs': total_new_qa_pairs
                })
                
                # 实时保存到临时JSON文件
                save_to_json(expanded_dataset, temp_output_file)
    
    # 打乱数据集
    random.shuffle(expanded_dataset)
    
    # 保存最终的扩充后的数据集
    save_to_json(expanded_dataset, output_file)
    
    # 删除临时文件
    if os.path.exists(temp_output_file):
        os.remove(temp_output_file)

    print(f"\nExpanded dataset saved to {output_file}")
    print(f"Original dataset size: {len(dataset)}")
    print(f"Expanded dataset size: {len(expanded_dataset)}")
    print(f"Total new QA pairs generated: {total_new_qa_pairs - len(dataset)}")
    print(f"Successful expansions: {successful_expansions}")
    print(f"Failed expansions: {failed_expansions}")

    # 保存未成功扩展的问题
    if unsuccessful_questions:
        with open('unsuccessful_questions.json', 'w', encoding='utf-8') as f:
            json.dump(unsuccessful_questions, f, ensure_ascii=False, indent=2)
        print(f"Unsuccessful questions saved to unsuccessful_questions.json")

if __name__ == "__main__":
    input_file = "/home/user/Python_project/llm_course/customdata.json"  # 替换为实际的输入文件名
    output_file = "expanded_customdata.json"
    expand_dataset(input_file, output_file)