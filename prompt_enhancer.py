import torch
import requests
import json

class LLMPromptEnhancer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 修改這裡：加入 {"multiline": True}
                "user_prompt": ("STRING", {"multiline": True, "default": "A girl in a coffee shop"}),
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a professional Stable Diffusion prompt engineer. Expand the user's description into a detailed, high-quality visual prompt."}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:1234/v1/chat/completions"}), 
                "model_name": ("STRING", {"default": "gemma4"}),
                "api_key": ("STRING", {"default": "not-needed"}),
                "language_mode": (["繁體中文", "簡體中文"], {"default": "繁體中文"}),
                "max_new_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("中文 Prompt", "英文 Prompt")
    FUNCTION = "enhance_prompt"
    CATEGORY = "Prompt Helpers"

    def enhance_prompt(self, user_prompt, system_prompt, api_url, model_name, api_key, language_mode, max_new_tokens, temperature):
        # 1. 根據選單決定語言指令 (保持英文描述，增加模型理解度)
        if language_mode == "繁體中文":
            lang_instruction = "Traditional Chinese (繁體中文)"
            negation_instruction = "DO NOT use Simplified Chinese characters."
        else:
            lang_instruction = "Simplified Chinese (简体中文)"
            negation_instruction = "DO NOT use Traditional Chinese characters."

        # 2. 構建強化的系統指令
        # 我們將使用者的 system_prompt 當作「任務目標」，但用英文來加強「語言規範」
        
        # 這裡我們把邏輯跟使用者的指令分開
        logic_prefix = (
            "### CORE INSTRUCTION ###\n"
            "You are an AI assistant helping with prompt engineering. "
            "Follow the user's task instructions below, but you MUST strictly adhere to the language requirements.\n\n"
            "### LANGUAGE REQUIREMENT ###\n"
            f"The 'chinese_prompt' field MUST be written strictly in {lang_instruction}.\n"
            f"{negation_instruction}\n\n"
            "### FORMAT REQUIREMENT ###\n"
            "You must respond ONLY with a valid JSON object. "
            "Do not include any markdown formatting, code blocks, or extra text.\n"
            "The JSON must contain exactly these two keys: 'chinese_prompt' and 'english_prompt'.\n"
            "Example Output:\n"
            f"{{\"chinese_prompt\": \"...\", \"english_prompt\": \"...\"}}\n\n"
            "### USER TASK DESCRIPTION ###\n"
        )

        # 組合最終的指令：邏輯(英文) + 使用者任務(使用者輸入)
        final_system_prompt = logic_prefix + system_prompt

        # 3. 準備 Payload
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": f"Task: Enhance this prompt: {user_prompt}"}
            ],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "response_format": { "type": "json_object" } 
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            res_json = response.json()
            content = res_json['choices'][0]['message']['content']
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            chinese_out = data.get("chinese_prompt", "JSON Key Error: chinese_prompt")
            english_out = data.get("english_prompt", "JSON Key Error: english_prompt")
            
            return (chinese_out, english_out)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"LLM Node Error: {error_msg}")
            return (error_msg, error_msg)

NODE_CLASS_MAPPINGS = {
    "LLMPromptEnhancer": LLMPromptEnhancer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMPromptEnhancer": "LLM Prompt Enhancer (Multi-Lang)"
}