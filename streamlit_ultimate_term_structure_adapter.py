#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit系统适配器 - 终极版AI期限结构分析系统
将终极版分析器适配到现有的Streamlit期货Trading Agents系统中
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# 导入终极版分析器
from ultimate_term_structure_analyzer import UltimateTermStructureAnalyzer

class StreamlitUltimateTermStructureAdapter:
    """Streamlit系统适配器 - 终极版期限结构分析"""
    
    def __init__(self, deepseek_api_key: str = None, serper_api_key: str = None, data_dir: str = None):
        self.analyzer = UltimateTermStructureAnalyzer(
            deepseek_api_key=deepseek_api_key,
            serper_api_key=serper_api_key,
            data_dir=data_dir,
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_variety_for_streamlit(self, variety: str, analysis_date: str = None, model_mode: str = "chat") -> Dict[str, Any]:
        """
        为Streamlit系统提供期限结构分析
        
        Args:
            variety: 品种代码
            analysis_date: 分析日期
            model_mode: 模型模式 ('chat' 或 'reasoner')
        
        Returns:
            符合Streamlit系统格式的分析结果
        """
        try:
            # 执行终极版分析
            ultimate_result = self.analyzer.analyze_variety(
                variety=variety,
                analysis_date=analysis_date,
                model_mode=model_mode
            )
            
            if "error" in ultimate_result:
                return {
                    "error": ultimate_result["error"],
                    "success": False,
                    "analysis_time": datetime.now().isoformat(),
                    "model_used": model_mode
                }
            
            # 转换为Streamlit系统格式
            streamlit_result = self._convert_to_streamlit_format(ultimate_result)
            
            return streamlit_result
            
        except Exception as e:
            self.logger.error(f"期限结构分析失败: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "analysis_time": datetime.now().isoformat(),
                "model_used": model_mode
            }
    
    def _convert_to_streamlit_format(self, ultimate_result: Dict[str, Any]) -> Dict[str, Any]:
        """将终极版结果转换为Streamlit系统格式"""
        
        variety = ultimate_result.get("variety", "")
        chinese_name = ultimate_result.get("chinese_name", "")
        analysis_date = ultimate_result.get("analysis_date", "")
        model_mode = ultimate_result.get("model_mode", "chat")
        integrated_analysis = ultimate_result.get("integrated_analysis", {})
        report = ultimate_result.get("report", "")
        charts = ultimate_result.get("charts", [])
        references = ultimate_result.get("references", [])
        
        # 提取关键指标
        metrics = self._extract_key_metrics(integrated_analysis)
        
        # 构建符合Streamlit格式的结果
        streamlit_result = {
            # 基本信息
            "success": True,
            "analysis_time": datetime.now().isoformat(),
            "data_date": analysis_date,
            "model_used": f"deepseek-{model_mode}",
            "analysis_version": "ultimate_v2.0",
            "search_enhanced": True,
            
            # 品种信息
            "variety": variety,
            "chinese_name": chinese_name,
            "analysis_date": analysis_date,
            
            # AI分析报告
            "ai_analysis": report,
            
            # 关键指标
            "metrics": metrics,
            
            # 数据质量信息
            "data_quality": integrated_analysis.get("data_quality", {}),
            
            # 结构分析
            "structure_analysis": integrated_analysis.get("structure_analysis", {}),
            
            # Full Carry分析
            "full_carry_analysis": integrated_analysis.get("full_carry_analysis", {}),
            
            # 便利收益分析
            "convenience_yield_analysis": integrated_analysis.get("convenience_yield_analysis", {}),
            
            # 价差分析
            "spread_analysis": integrated_analysis.get("spread_analysis", {}),
            
            # 产业分析
            "industry_analysis": integrated_analysis.get("industry_analysis", {}),
            
            # 风险评估
            "risk_assessment": integrated_analysis.get("risk_assessment", {}),
            
            # 图表数据 - 转换为主界面期望的格式
            "charts_html": charts if isinstance(charts, list) else [],
            
            # 引用信息
            "references": references if isinstance(references, list) else [],
            "reference_count": len(references) if isinstance(references, list) else 0,
            
            # 置信度评分
            "confidence_score": self._calculate_confidence_score(integrated_analysis),
            
            # 外部数据
            "external_data": integrated_analysis.get("external_data", {}),
            
            # 使用统计
            "usage": {
                "prompt_tokens": 0,  # 终极版不提供token统计
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        return streamlit_result
    
    def _extract_key_metrics(self, integrated_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """提取关键指标"""
        
        metrics = {}
        
        # 数据质量指标
        data_quality = integrated_analysis.get("data_quality", {})
        metrics["data_quality_percentage"] = data_quality.get("quality_percentage", 0)
        metrics["data_quality_level"] = data_quality.get("quality_level", "未知")
        
        # 期限结构指标
        structure_analysis = integrated_analysis.get("structure_analysis", {})
        if "error" not in structure_analysis:
            metrics["structure_type"] = structure_analysis.get("structure_type", "未知")
            metrics["near_price"] = structure_analysis.get("near_price", 0)
            metrics["far_price"] = structure_analysis.get("far_price", 0)
            metrics["absolute_spread"] = structure_analysis.get("absolute_spread", 0)
            metrics["relative_spread"] = structure_analysis.get("relative_spread", 0)
            metrics["structure_strength"] = structure_analysis.get("structure_strength", "未知")
            
            # 流动性指标
            liquidity_analysis = structure_analysis.get("liquidity_analysis", {})
            if liquidity_analysis:
                metrics["main_contract"] = liquidity_analysis.get("main_contract", "未知")
                metrics["liquidity_grade"] = liquidity_analysis.get("liquidity_grade", "未知")
                metrics["main_volume_ratio"] = liquidity_analysis.get("main_volume_ratio", 0)
        
        # 价差分析指标
        spread_analysis = integrated_analysis.get("spread_analysis", {})
        if "error" not in spread_analysis:
            segments = spread_analysis.get("spread_segments", {})
            if segments:
                metrics["near_main_spread"] = segments.get("near_main_spread", 0)
                metrics["main_second_spread"] = segments.get("main_second_spread", 0)
            
            rhythm = spread_analysis.get("rhythm_analysis", {})
            if rhythm:
                metrics["current_rhythm"] = rhythm.get("current_rhythm", "未知")
        
        # 便利收益指标
        convenience_yield = integrated_analysis.get("convenience_yield_analysis", {})
        if "status" in convenience_yield and convenience_yield["status"] != "数据不完整":
            metrics["inventory_percentile"] = convenience_yield.get("inventory_percentile", 0)
            metrics["inventory_signal"] = convenience_yield.get("inventory_signal", "未知")
        
        # 风险指标
        risk_assessment = integrated_analysis.get("risk_assessment", {})
        metrics["risk_level"] = risk_assessment.get("risk_level", "未知")
        metrics["risk_score"] = risk_assessment.get("risk_score", 0)
        
        # 产业指标
        industry_analysis = integrated_analysis.get("industry_analysis", {})
        metrics["variety_type"] = industry_analysis.get("variety_type", "未知")
        
        return metrics
    
    def _calculate_confidence_score(self, integrated_analysis: Dict[str, Any]) -> float:
        """计算综合置信度评分"""
        
        scores = []
        
        # 数据质量评分 (0.3权重)
        data_quality = integrated_analysis.get("data_quality", {})
        quality_percentage = data_quality.get("quality_percentage", 0)
        scores.append((quality_percentage / 100, 0.3))
        
        # 结构分析完整性 (0.25权重)
        structure_analysis = integrated_analysis.get("structure_analysis", {})
        if "error" not in structure_analysis and structure_analysis:
            structure_score = 0.8 if structure_analysis.get("structure_type") != "未知" else 0.5
            scores.append((structure_score, 0.25))
        else:
            scores.append((0.3, 0.25))
        
        # 价差分析完整性 (0.2权重)
        spread_analysis = integrated_analysis.get("spread_analysis", {})
        if "error" not in spread_analysis and spread_analysis:
            scores.append((0.75, 0.2))
        else:
            scores.append((0.4, 0.2))
        
        # 外部数据获取情况 (0.15权重)
        external_data = integrated_analysis.get("external_data", {})
        if external_data and "error" not in external_data:
            # 检查是否有搜索结果
            has_external = any(
                data.get("results") for data in external_data.values() 
                if isinstance(data, dict) and "results" in data
            )
            external_score = 0.8 if has_external else 0.5
            scores.append((external_score, 0.15))
        else:
            scores.append((0.3, 0.15))
        
        # Full Carry和便利收益分析 (0.1权重)
        full_carry = integrated_analysis.get("full_carry_analysis", {})
        convenience_yield = integrated_analysis.get("convenience_yield_analysis", {})
        
        theory_score = 0.5  # 基础分
        if "status" in full_carry and full_carry["status"] != "数据缺失":
            theory_score += 0.2
        if "status" in convenience_yield and convenience_yield["status"] != "数据不完整":
            theory_score += 0.2
        
        scores.append((theory_score, 0.1))
        
        # 计算加权平均
        total_score = sum(score * weight for score, weight in scores)
        total_weight = sum(weight for _, weight in scores)
        
        final_score = total_score / total_weight if total_weight > 0 else 0.5
        
        # 确保分数在合理范围内
        return max(0.3, min(0.95, final_score))

# 为了保持向后兼容，创建一个全局函数接口
def analyze_variety_ultimate(variety: str, analysis_date: str = None, model_mode: str = "chat") -> Dict[str, Any]:
    """
    终极版期限结构分析的全局接口函数
    用于替换原有的期限结构分析函数
    """
    adapter = StreamlitUltimateTermStructureAdapter()
    return adapter.analyze_variety_for_streamlit(variety, analysis_date, model_mode)

# 异步版本接口
async def analyze_variety_ultimate_async(variety: str, analysis_date: str = None, model_mode: str = "chat") -> Dict[str, Any]:
    """
    终极版期限结构分析的异步接口函数
    用于替换原有的异步期限结构分析函数
    """
    # 在异步环境中调用同步函数
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, analyze_variety_ultimate, variety, analysis_date, model_mode)

if __name__ == "__main__":
    # 测试适配器
    adapter = StreamlitUltimateTermStructureAdapter()
    
    print("🔧 测试终极版期限结构分析适配器")
    print("="*60)
    
    # 测试分析
    variety = "C"
    result = adapter.analyze_variety_for_streamlit(variety, "2025-01-10", "chat")
    
    if result.get("success"):
        print("✅ 适配器测试成功！")
        print(f"📊 品种: {result.get('variety')} ({result.get('chinese_name')})")
        print(f"📈 置信度: {result.get('confidence_score', 0):.2f}")
        print(f"🎯 数据质量: {result.get('metrics', {}).get('data_quality_level', '未知')}")
        print(f"📋 引用数量: {result.get('reference_count', 0)}")
        print(f"📊 图表数量: {len(result.get('charts_html', []))}")
    else:
        print("❌ 适配器测试失败")
        print(f"错误: {result.get('error')}")
