import logging
import os
import json
import requests
from typing import Dict, Any

class AIModels:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载API配置"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'chatgpt': {'api_key': '', 'api_base': 'https://api.openai.com/v1'},
            'deepseek': {'api_key': '', 'api_base': 'https://api.deepseek.com/v1'},
            'kimi': {'api_key': '', 'api_base': 'https://api.moonshot.cn/v1'},
            'ollama': {'api_base': 'http://localhost:11434'}
        }
    
    def save_config(self, config: Dict[str, Any]):
        """保存API配置"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        self.config = config
    
    def analyze(self, code_data: str, model: str = 'chatgpt') -> Dict[str, Any]:
        """调用AI模型进行代码分析"""
        self.logger.info(f'Starting AI model analysis using {model}...')
        
        if model not in self.config:
            raise ValueError(f'不支持的AI模型: {model}')
            
        if model == 'chatgpt':
            return self._analyze_with_chatgpt(code_data)
        elif model == 'deepseek':
            return self._analyze_with_deepseek(code_data)
        elif model == 'kimi':
            return self._analyze_with_kimi(code_data)
        elif model == 'ollama':
            return self._analyze_with_ollama(code_data)
    
    def _analyze_with_chatgpt(self, code_data: str) -> Dict[str, Any]:
        """使用ChatGPT进行分析"""
        config = self.config['chatgpt']
        if not config['api_key']:
            raise ValueError('请先配置ChatGPT API密钥')
            
        headers = {
            'Authorization': f'Bearer {config["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-4',
            'messages': [
                {'role': 'system', 'content': '你是一个专业的代码审计专家，请分析以下代码中的潜在问题和安全漏洞。'},
                {'role': 'user', 'content': code_data}
            ]
        }
        
        response = requests.post(
            f"{config['api_base']}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'analysis': result['choices'][0]['message']['content'],
                'model': 'ChatGPT'
            }
        else:
            raise Exception(f'ChatGPT API调用失败: {response.text}')
    
    def _analyze_with_deepseek(self, code_data: str) -> Dict[str, Any]:
        """使用DeepSeek进行分析"""
        config = self.config['deepseek']
        if not config['api_key']:
            raise ValueError('请先配置DeepSeek API密钥')
            
        # TODO: 实现DeepSeek API调用
        return {'analysis': '暂未实现DeepSeek API调用', 'model': 'DeepSeek'}
    
    def _analyze_with_kimi(self, code_data: str) -> Dict[str, Any]:
        """使用Kimi进行分析"""
        config = self.config['kimi']
        if not config['api_key']:
            raise ValueError('请先配置Kimi API密钥')
            
        # TODO: 实现Kimi API调用
        return {'analysis': '暂未实现Kimi API调用', 'model': 'Kimi'}
    
    def _analyze_with_ollama(self, code_data: str) -> Dict[str, Any]:
        """使用Ollama进行分析"""
        config = self.config['ollama']
        
        data = {
            'model': 'codellama',
            'prompt': f'请分析以下代码中的潜在问题和安全漏洞：\n{code_data}',
            'stream': False
        }
        
        response = requests.post(
            f"{config['api_base']}/api/generate",
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'analysis': result['response'],
                'model': 'Ollama'
            }
        else:
            raise Exception(f'Ollama API调用失败: {response.text}')