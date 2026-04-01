"""
智能配置简化器

提供一键配置、智能推荐、自动优化等功能，降低用户使用门槛。
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class SmartConfigurator:
    """智能配置器 - 简化配置复杂度"""
    
    # 预设配置模板
    PRESETS = {
        'beginner': {
            'name': '新手模式',
            'description': '最简单配置，只需设置 API Key',
            'config': {
                'model_name': 'deepseek-chat',  # 自动识别提供商
                'temperature': 0.3,
                'initial_concurrency': 5,
                'max_concurrency': 8,
                'timeout': 60,
            }
        },
        
        'balanced': {
            'name': '平衡模式',
            'description': '性能与质量的平衡（推荐）',
            'config': {
                'model_name': 'deepseek-chat',
                'temperature': 0.3,
                'top_p': 0.8,
                'initial_concurrency': 8,
                'max_concurrency': 12,
                'timeout': 60,
                'enable_two_pass': True,
                'skip_review_if_local_hit': True,
            }
        },
        
        'quality': {
            'name': '高质量模式',
            'description': '翻译质量优先，适合重要文档',
            'config': {
                'draft_model_name': 'deepseek-chat',
                'review_model_name': 'gpt-4-turbo',
                'draft_temperature': 0.3,
                'review_temperature': 0.5,
                'initial_concurrency': 6,
                'max_concurrency': 10,
                'timeout': 90,
            }
        },
        
        'speed': {
            'name': '快速模式',
            'description': '翻译速度优先，适合大批量',
            'config': {
                'model_name': 'deepseek-chat',
                'temperature': 0.3,
                'initial_concurrency': 15,
                'max_concurrency': 20,
                'timeout': 45,
                'cache_capacity': 5000,
            }
        },
    }
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
    
    def quick_setup(self, api_key: str, preset: str = 'beginner') -> Dict[str, Any]:
        """
        快速设置 - 一键完成配置
        
        Args:
            api_key: API 密钥
            preset: 预设模式 (beginner/balanced/quality/speed)
            
        Returns:
            配置字典
        """
        if preset not in self.PRESETS:
            raise ValueError(f"未知预设：{preset}，可选值：{list(self.PRESETS.keys())}")
        
        # 获取预设配置
        config = self.PRESETS[preset]['config'].copy()
        
        # 添加 API 密钥
        config['api_keys'] = {
            'deepseek': {
                'api_key': api_key,
                'base_url': 'https://api.deepseek.com'
            }
        }
        
        # 添加版本信息
        config['_version'] = 'v3.0.0'
        config['_preset'] = preset
        
        return config
    
    def auto_optimize(self, current_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动优化配置 - 根据使用情况智能调整
        
        Args:
            current_config: 当前配置
            
        Returns:
            优化后的配置
        """
        optimized = current_config.copy()
        
        # 如果频繁超时，增加 timeout
        # TODO: 从历史数据中分析
        
        # 如果成功率低，降低并发
        # TODO: 从历史数据中分析
        
        # 如果是第一次使用，使用新手模式
        if '_first_run' not in optimized:
            optimized.update(self.PRESETS['beginner']['config'])
            optimized['_first_run'] = True
        
        return optimized
    
    def create_config_file(self, api_key: str, preset: str = 'beginner', 
                          output_path: Optional[str] = None) -> str:
        """
        创建配置文件 - 一键生成完整配置
        
        Args:
            api_key: API 密钥
            preset: 预设模式
            output_path: 输出路径（默认 config/config.json）
            
        Returns:
            配置文件路径
        """
        config = self.quick_setup(api_key, preset)
        
        # 确定输出路径
        if output_path is None:
            output_path = self.config_path
        else:
            output_path = Path(output_path)
        
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置文件已创建：{output_path}")
        print(f"   使用模式：{self.PRESETS[preset]['name']}")
        print(f"   API Key: {'*' * 10}{api_key[-4:]}")
        
        return str(output_path)
    
    def get_recommendation(self, scenario: str) -> Dict[str, Any]:
        """
        获取场景推荐配置
        
        Args:
            scenario: 使用场景
            
        Returns:
            推荐配置
        """
        recommendations = {
            'technical_docs': {
                'name': '技术文档翻译',
                'preset': 'quality',
                'tips': [
                    '使用高质量模式确保术语准确',
                    '建议准备术语库',
                    '温度参数设置为 0.2-0.3'
                ]
            },
            
            'literature': {
                'name': '文学翻译',
                'preset': 'quality',
                'tips': [
                    '使用更高温度参数（0.5-0.7）',
                    '校对阶段很重要',
                    '建议使用 GPT-4 进行校对'
                ]
            },
            
            'bulk_translation': {
                'name': '批量翻译',
                'preset': 'speed',
                'tips': [
                    '提高并发数到 15-20',
                    '增加缓存容量',
                    '可以适当降低超时时间'
                ]
            },
            
            'daily_use': {
                'name': '日常使用',
                'preset': 'balanced',
                'tips': [
                    '使用平衡模式即可',
                    '无需过多调整参数',
                    '关注术语库积累'
                ]
            },
        }
        
        if scenario not in recommendations:
            return recommendations['daily_use']
        
        return recommendations[scenario]
    
    def validate_and_fix(self, config: Dict[str, Any]) -> tuple[bool, list]:
        """
        验证配置并自动修复常见问题
        
        Args:
            config: 配置字典
            
        Returns:
            (是否成功，问题列表)
        """
        issues = []
        fixed = False
        
        # 检查 API Key
        if 'api_key' not in str(config.get('api_keys', {})):
            issues.append({
                'type': 'error',
                'field': 'api_keys',
                'message': '缺少 API 密钥配置'
            })
        
        # 检查并发数
        if config.get('initial_concurrency', 0) > config.get('max_concurrency', 0):
            issues.append({
                'type': 'warning',
                'field': 'concurrency',
                'message': 'initial_concurrency 不能大于 max_concurrency'
            })
            # 自动修复
            config['max_concurrency'] = config['initial_concurrency']
            fixed = True
        
        # 检查温度参数
        temp = config.get('temperature', 0.3)
        if temp < 0 or temp > 2:
            issues.append({
                'type': 'error',
                'field': 'temperature',
                'message': f'temperature 超出范围 [0, 2]，当前值：{temp}'
            })
            # 自动修复到默认值
            config['temperature'] = 0.3
            fixed = True
        
        success = len([i for i in issues if i['type'] == 'error']) == 0
        
        return success, issues


def main():
    """主函数 - 演示使用"""
    print("=" * 70)
    print("智能配置简化器")
    print("=" * 70)
    print()
    
    configurator = SmartConfigurator()
    
    # 演示 1: 快速设置
    print("1️⃣  快速设置（一键配置）:")
    print("-" * 70)
    
    config = configurator.quick_setup(
        api_key="sk-test-key-12345",
        preset='beginner'
    )
    
    print(f"✅ 生成配置（新手模式）:")
    print(f"   模型：{config['model_name']}")
    print(f"   并发：{config['initial_concurrency']}-{config['max_concurrency']}")
    print(f"   超时：{config['timeout']}秒")
    print()
    
    # 演示 2: 场景推荐
    print("2️⃣  场景推荐:")
    print("-" * 70)
    
    scenarios = ['technical_docs', 'literature', 'bulk_translation', 'daily_use']
    
    for scenario in scenarios:
        rec = configurator.get_recommendation(scenario)
        print(f"  {rec['name']:15s} → 推荐：{rec['preset']}模式")
        for tip in rec['tips'][:2]:
            print(f"    💡 {tip}")
    
    print()
    
    # 演示 3: 验证和自动修复
    print("3️⃣  验证和自动修复:")
    print("-" * 70)
    
    test_config = {
        'initial_concurrency': 10,
        'max_concurrency': 5,  # 错误：小于 initial
        'temperature': 3.0,    # 错误：超出范围
    }
    
    success, issues = configurator.validate_and_fix(test_config)
    
    print(f"  验证结果：{'✅ 通过' if success else '❌ 有问题'}")
    print(f"  发现问题：{len(issues)}个")
    
    for issue in issues:
        icon = "❌" if issue['type'] == 'error' else "⚠️"
        print(f"    {icon} [{issue['field']}] {issue['message']}")
    
    print()
    print("4️⃣  可用预设模式:")
    print("-" * 70)
    
    for key, preset in configurator.PRESETS.items():
        print(f"  {key:12s}: {preset['name']} - {preset['description']}")
    
    print()
    print("=" * 70)
    print("✅ 使用智能配置器，只需 3 步即可完成配置:")
    print("   1. 选择预设模式（beginner/balanced/quality/speed）")
    print("   2. 输入 API Key")
    print("   3. 运行 quick_setup() 或 create_config_file()")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())
