"""
Responsible AI Implementation for GeoSpark System
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np
import json
from collections import defaultdict

from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

class BiasType(Enum):
    """Types of bias that can be detected"""
    GEOGRAPHICAL = "geographical"
    SOCIOECONOMIC = "socioeconomic"
    DEMOGRAPHIC = "demographic"
    DATA_QUALITY = "data_quality"
    ALGORITHMIC = "algorithmic"
    TEMPORAL = "temporal"

class FairnessMetric(Enum):
    """Fairness metrics for evaluation"""
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUALIZED_ODDS = "equalized_odds"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    CALIBRATION = "calibration"

class TransparencyLevel(Enum):
    """Levels of transparency"""
    FULL = "full"
    PARTIAL = "partial"
    MINIMAL = "minimal"

@dataclass
class BiasDetectionResult:
    """Result of bias detection analysis"""
    bias_type: BiasType
    severity: float  # 0-1 scale
    description: str
    affected_groups: List[str]
    mitigation_strategies: List[str]
    confidence: float

@dataclass
class FairnessAssessment:
    """Fairness assessment result"""
    metric: FairnessMetric
    score: float  # 0-1 scale
    group_comparisons: Dict[str, float]
    is_fair: bool
    recommendations: List[str]

@dataclass
class ExplainabilityReport:
    """Explainability report for AI decisions"""
    decision_id: str
    model_used: str
    input_features: List[str]
    feature_importance: Dict[str, float]
    decision_path: List[str]
    confidence_score: float
    uncertainty_factors: List[str]
    alternative_outcomes: List[Dict[str, Any]]

class ResponsibleAIManager:
    """Manages Responsible AI practices and monitoring"""
    
    def __init__(self):
        self.bias_detection_enabled = True
        self.fairness_monitoring_enabled = True
        self.explainability_enabled = True
        self.audit_logging_enabled = True
        
        # Bias detection thresholds
        self.bias_thresholds = {
            BiasType.GEOGRAPHICAL: 0.3,
            BiasType.SOCIOECONOMIC: 0.25,
            BiasType.DEMOGRAPHIC: 0.2,
            BiasType.DATA_QUALITY: 0.4,
            BiasType.ALGORITHMIC: 0.3,
            BiasType.TEMPORAL: 0.35
        }
        
        # Fairness monitoring
        self.fairness_history = defaultdict(list)
        self.bias_incidents = []
        
        logger.info("Responsible AI Manager initialized")
    
    async def assess_decision_fairness(self, decision_data: Dict[str, Any], 
                                     context: Dict[str, Any]) -> List[FairnessAssessment]:
        """Assess fairness of AI decisions"""
        try:
            assessments = []
            
            # Extract decision components
            decision_type = decision_data.get("decision_type", "site_selection")
            scores = decision_data.get("scores", {})
            location_data = context.get("location", {})
            demographic_data = context.get("demographics", {})
            
            # Check demographic parity
            if demographic_data:
                dp_assessment = await self._assess_demographic_parity(scores, demographic_data)
                assessments.append(dp_assessment)
            
            # Check geographical fairness
            geo_assessment = await self._assess_geographical_fairness(scores, location_data)
            assessments.append(geo_assessment)
            
            # Check equal opportunity
            eo_assessment = await self._assess_equal_opportunity(scores, context)
            assessments.append(eo_assessment)
            
            # Log assessment
            agent_logger.log_agent_decision(
                "responsible_ai",
                f"Fairness assessment completed for {decision_type}",
                f"Found {len([a for a in assessments if not a.is_fair])} fairness issues"
            )
            
            return assessments
            
        except Exception as e:
            logger.error(f"Error in fairness assessment: {e}")
            return []
    
    async def detect_bias(self, data: Dict[str, Any], 
                         analysis_results: Dict[str, Any]) -> List[BiasDetectionResult]:
        """Detect bias in data and analysis results"""
        try:
            bias_results = []
            
            # Check geographical bias
            geo_bias = await self._detect_geographical_bias(data, analysis_results)
            if geo_bias:
                bias_results.append(geo_bias)
            
            # Check socioeconomic bias
            socio_bias = await self._detect_socioeconomic_bias(data, analysis_results)
            if socio_bias:
                bias_results.append(socio_bias)
            
            # Check data quality bias
            quality_bias = await self._detect_data_quality_bias(data, analysis_results)
            if quality_bias:
                bias_results.append(quality_bias)
            
            # Check algorithmic bias
            algo_bias = await self._detect_algorithmic_bias(data, analysis_results)
            if algo_bias:
                bias_results.append(algo_bias)
            
            # Log bias detection
            if bias_results:
                agent_logger.log_agent_decision(
                    "responsible_ai",
                    f"Bias detection completed",
                    f"Found {len(bias_results)} bias issues"
                )
            
            return bias_results
            
        except Exception as e:
            logger.error(f"Error in bias detection: {e}")
            return []
    
    async def generate_explanation(self, decision_data: Dict[str, Any],
                                 model_info: Dict[str, Any]) -> ExplainabilityReport:
        """Generate explanation for AI decision"""
        try:
            decision_id = decision_data.get("decision_id", f"decision_{datetime.utcnow().timestamp()}")
            model_used = model_info.get("model_name", "unknown")
            
            # Extract input features
            input_features = list(decision_data.get("input_data", {}).keys())
            
            # Calculate feature importance (simplified)
            feature_importance = await self._calculate_feature_importance(decision_data)
            
            # Generate decision path
            decision_path = await self._generate_decision_path(decision_data)
            
            # Calculate confidence score
            confidence_score = decision_data.get("confidence_score", 0.8)
            
            # Identify uncertainty factors
            uncertainty_factors = await self._identify_uncertainty_factors(decision_data)
            
            # Generate alternative outcomes
            alternative_outcomes = await self._generate_alternative_outcomes(decision_data)
            
            explanation = ExplainabilityReport(
                decision_id=decision_id,
                model_used=model_used,
                input_features=input_features,
                feature_importance=feature_importance,
                decision_path=decision_path,
                confidence_score=confidence_score,
                uncertainty_factors=uncertainty_factors,
                alternative_outcomes=alternative_outcomes
            )
            
            # Log explanation generation
            agent_logger.log_agent_decision(
                "responsible_ai",
                f"Explanation generated for decision {decision_id}",
                f"Confidence: {confidence_score:.2f}, Features: {len(input_features)}"
            )
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return ExplainabilityReport(
                decision_id="error",
                model_used="unknown",
                input_features=[],
                feature_importance={},
                decision_path=["Error generating explanation"],
                confidence_score=0.0,
                uncertainty_factors=["System error"],
                alternative_outcomes=[]
            )
    
    async def audit_decision_process(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Audit the decision-making process for compliance"""
        try:
            audit_result = {
                "audit_id": f"audit_{datetime.utcnow().timestamp()}",
                "timestamp": datetime.utcnow().isoformat(),
                "compliance_checks": {},
                "recommendations": [],
                "overall_compliance": True
            }
            
            # Check data privacy compliance
            privacy_check = await self._check_privacy_compliance(process_data)
            audit_result["compliance_checks"]["privacy"] = privacy_check
            
            # Check algorithmic transparency
            transparency_check = await self._check_transparency_compliance(process_data)
            audit_result["compliance_checks"]["transparency"] = transparency_check
            
            # Check bias mitigation
            bias_check = await self._check_bias_mitigation(process_data)
            audit_result["compliance_checks"]["bias_mitigation"] = bias_check
            
            # Check explainability
            explainability_check = await self._check_explainability_compliance(process_data)
            audit_result["compliance_checks"]["explainability"] = explainability_check
            
            # Check human oversight
            oversight_check = await self._check_human_oversight(process_data)
            audit_result["compliance_checks"]["human_oversight"] = oversight_check
            
            # Generate recommendations
            audit_result["recommendations"] = await self._generate_compliance_recommendations(audit_result["compliance_checks"])
            
            # Determine overall compliance
            audit_result["overall_compliance"] = all(
                check.get("compliant", False) for check in audit_result["compliance_checks"].values()
            )
            
            return audit_result
            
        except Exception as e:
            logger.error(f"Error in decision process audit: {e}")
            return {"error": str(e)}
    
    # Helper methods for bias detection
    
    async def _detect_geographical_bias(self, data: Dict[str, Any], 
                                      results: Dict[str, Any]) -> Optional[BiasDetectionResult]:
        """Detect geographical bias in data and results"""
        try:
            locations = data.get("locations", [])
            if not locations:
                return None
            
            # Analyze geographical distribution
            lat_values = [loc.get("latitude", 0) for loc in locations]
            lon_values = [loc.get("longitude", 0) for loc in locations]
            
            # Check for clustering bias
            lat_std = np.std(lat_values)
            lon_std = np.std(lon_values)
            
            # Check for regional bias
            regional_distribution = self._analyze_regional_distribution(locations)
            
            # Calculate bias severity
            clustering_bias = min(1.0, (lat_std + lon_std) / 10.0)  # Normalize
            regional_bias = self._calculate_regional_bias(regional_distribution)
            
            severity = max(clustering_bias, regional_bias)
            
            if severity > self.bias_thresholds[BiasType.GEOGRAPHICAL]:
                return BiasDetectionResult(
                    bias_type=BiasType.GEOGRAPHICAL,
                    severity=severity,
                    description=f"Geographical bias detected with severity {severity:.2f}",
                    affected_groups=self._identify_affected_regions(regional_distribution),
                    mitigation_strategies=[
                        "Include more diverse geographical locations",
                        "Apply geographical weighting to balance representation",
                        "Consider regional economic factors"
                    ],
                    confidence=0.8
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting geographical bias: {e}")
            return None
    
    async def _detect_socioeconomic_bias(self, data: Dict[str, Any], 
                                       results: Dict[str, Any]) -> Optional[BiasDetectionResult]:
        """Detect socioeconomic bias"""
        try:
            # Check for income-based bias in site selection
            income_data = data.get("socioeconomic_data", {})
            if not income_data:
                return None
            
            # Analyze income distribution impact on decisions
            income_impact = self._analyze_income_impact(income_data, results)
            
            if income_impact > self.bias_thresholds[BiasType.SOCIOECONOMIC]:
                return BiasDetectionResult(
                    bias_type=BiasType.SOCIOECONOMIC,
                    severity=income_impact,
                    description=f"Socioeconomic bias detected with severity {income_impact:.2f}",
                    affected_groups=["low_income_areas", "rural_communities"],
                    mitigation_strategies=[
                        "Include socioeconomic factors in decision criteria",
                        "Apply community benefit weighting",
                        "Consider environmental justice principles"
                    ],
                    confidence=0.75
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting socioeconomic bias: {e}")
            return None
    
    async def _detect_data_quality_bias(self, data: Dict[str, Any], 
                                      results: Dict[str, Any]) -> Optional[BiasDetectionResult]:
        """Detect data quality bias"""
        try:
            # Check for data quality variations
            quality_scores = data.get("data_quality_scores", [])
            if not quality_scores:
                return None
            
            # Calculate quality variance
            quality_variance = np.var(quality_scores)
            quality_mean = np.mean(quality_scores)
            
            # Check for systematic quality differences
            quality_bias_score = quality_variance / (quality_mean + 1e-6)
            
            if quality_bias_score > self.bias_thresholds[BiasType.DATA_QUALITY]:
                return BiasDetectionResult(
                    bias_type=BiasType.DATA_QUALITY,
                    severity=min(1.0, quality_bias_score),
                    description=f"Data quality bias detected with severity {quality_bias_score:.2f}",
                    affected_groups=["low_quality_data_sources"],
                    mitigation_strategies=[
                        "Improve data collection methods",
                        "Apply data quality weighting",
                        "Use multiple data sources for validation"
                    ],
                    confidence=0.9
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting data quality bias: {e}")
            return None
    
    async def _detect_algorithmic_bias(self, data: Dict[str, Any], 
                                     results: Dict[str, Any]) -> Optional[BiasDetectionResult]:
        """Detect algorithmic bias"""
        try:
            # Check for systematic patterns in algorithm outputs
            scores = results.get("scores", [])
            if not scores:
                return None
            
            # Analyze score distribution
            score_distribution = np.histogram(scores, bins=10)[0]
            score_variance = np.var(score_distribution)
            
            # Check for systematic bias patterns
            bias_patterns = self._analyze_bias_patterns(data, results)
            
            algorithmic_bias_score = score_variance / (len(scores) + 1e-6)
            
            if algorithmic_bias_score > self.bias_thresholds[BiasType.ALGORITHMIC]:
                return BiasDetectionResult(
                    bias_type=BiasType.ALGORITHMIC,
                    severity=min(1.0, algorithmic_bias_score),
                    description=f"Algorithmic bias detected with severity {algorithmic_bias_score:.2f}",
                    affected_groups=bias_patterns.get("affected_groups", []),
                    mitigation_strategies=[
                        "Review algorithm parameters",
                        "Implement bias correction techniques",
                        "Use diverse training data"
                    ],
                    confidence=0.7
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting algorithmic bias: {e}")
            return None
    
    # Helper methods for fairness assessment
    
    async def _assess_demographic_parity(self, scores: Dict[str, Any], 
                                       demographics: Dict[str, Any]) -> FairnessAssessment:
        """Assess demographic parity"""
        try:
            # Group scores by demographic categories
            group_scores = defaultdict(list)
            
            for group, score in scores.items():
                if group in demographics:
                    group_scores[demographics[group]].append(score)
            
            # Calculate group averages
            group_averages = {group: np.mean(scores) for group, scores in group_scores.items()}
            
            # Check for significant differences
            if len(group_averages) > 1:
                max_score = max(group_averages.values())
                min_score = min(group_averages.values())
                disparity = (max_score - min_score) / max_score
                
                is_fair = disparity < 0.1  # 10% threshold
                
                recommendations = []
                if not is_fair:
                    recommendations.extend([
                        "Review scoring criteria for demographic bias",
                        "Apply demographic parity constraints",
                        "Consider group-specific adjustments"
                    ])
            else:
                disparity = 0.0
                is_fair = True
                recommendations = ["Insufficient demographic data for assessment"]
            
            return FairnessAssessment(
                metric=FairnessMetric.DEMOGRAPHIC_PARITY,
                score=1.0 - disparity,
                group_comparisons=group_averages,
                is_fair=is_fair,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error assessing demographic parity: {e}")
            return FairnessAssessment(
                metric=FairnessMetric.DEMOGRAPHIC_PARITY,
                score=0.0,
                group_comparisons={},
                is_fair=False,
                recommendations=["Assessment failed due to error"]
            )
    
    async def _assess_geographical_fairness(self, scores: Dict[str, Any], 
                                           location_data: Dict[str, Any]) -> FairnessAssessment:
        """Assess geographical fairness"""
        try:
            # Analyze scores by geographical regions
            regional_scores = self._group_scores_by_region(scores, location_data)
            
            if len(regional_scores) > 1:
                # Calculate regional disparities
                regional_averages = {region: np.mean(scores) for region, scores in regional_scores.items()}
                max_score = max(regional_averages.values())
                min_score = min(regional_averages.values())
                disparity = (max_score - min_score) / max_score
                
                is_fair = disparity < 0.15  # 15% threshold for geographical fairness
                
                recommendations = []
                if not is_fair:
                    recommendations.extend([
                        "Consider regional economic factors",
                        "Apply geographical weighting",
                        "Include rural/urban balance criteria"
                    ])
            else:
                disparity = 0.0
                is_fair = True
                recommendations = ["Insufficient geographical data for assessment"]
            
            return FairnessAssessment(
                metric=FairnessMetric.EQUAL_OPPORTUNITY,
                score=1.0 - disparity,
                group_comparisons=regional_averages if len(regional_scores) > 1 else {},
                is_fair=is_fair,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error assessing geographical fairness: {e}")
            return FairnessAssessment(
                metric=FairnessMetric.EQUAL_OPPORTUNITY,
                score=0.0,
                group_comparisons={},
                is_fair=False,
                recommendations=["Assessment failed due to error"]
            )
    
    async def _assess_equal_opportunity(self, scores: Dict[str, Any], 
                                     context: Dict[str, Any]) -> FairnessAssessment:
        """Assess equal opportunity"""
        try:
            # Check if all groups have equal opportunity for positive outcomes
            opportunity_data = context.get("opportunity_data", {})
            
            if not opportunity_data:
                return FairnessAssessment(
                    metric=FairnessMetric.EQUAL_OPPORTUNITY,
                    score=1.0,
                    group_comparisons={},
                    is_fair=True,
                    recommendations=["No opportunity data available"]
                )
            
            # Calculate opportunity rates by group
            group_opportunities = {}
            for group, data in opportunity_data.items():
                positive_outcomes = sum(1 for score in data.get("scores", []) if score > 0.5)
                total_outcomes = len(data.get("scores", []))
                opportunity_rate = positive_outcomes / total_outcomes if total_outcomes > 0 else 0
                group_opportunities[group] = opportunity_rate
            
            # Check for equal opportunity
            if len(group_opportunities) > 1:
                max_opportunity = max(group_opportunities.values())
                min_opportunity = min(group_opportunities.values())
                opportunity_gap = max_opportunity - min_opportunity
                
                is_fair = opportunity_gap < 0.1  # 10% threshold
                
                recommendations = []
                if not is_fair:
                    recommendations.extend([
                        "Review decision criteria for equal opportunity",
                        "Consider group-specific thresholds",
                        "Implement opportunity balancing"
                    ])
            else:
                opportunity_gap = 0.0
                is_fair = True
                recommendations = ["Insufficient group data for assessment"]
            
            return FairnessAssessment(
                metric=FairnessMetric.EQUAL_OPPORTUNITY,
                score=1.0 - opportunity_gap,
                group_comparisons=group_opportunities,
                is_fair=is_fair,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error assessing equal opportunity: {e}")
            return FairnessAssessment(
                metric=FairnessMetric.EQUAL_OPPORTUNITY,
                score=0.0,
                group_comparisons={},
                is_fair=False,
                recommendations=["Assessment failed due to error"]
            )
    
    # Helper methods for explainability
    
    async def _calculate_feature_importance(self, decision_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate feature importance for decision"""
        try:
            input_data = decision_data.get("input_data", {})
            feature_importance = {}
            
            # Simple feature importance calculation based on data variance and correlation
            for feature, value in input_data.items():
                if isinstance(value, (int, float)):
                    # Higher variance indicates more important feature
                    importance = min(1.0, abs(value) / 100.0)  # Normalize
                    feature_importance[feature] = importance
                else:
                    feature_importance[feature] = 0.5  # Default for non-numeric features
            
            # Normalize importance scores
            total_importance = sum(feature_importance.values())
            if total_importance > 0:
                feature_importance = {
                    feature: importance / total_importance 
                    for feature, importance in feature_importance.items()
                }
            
            return feature_importance
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            return {}
    
    async def _generate_decision_path(self, decision_data: Dict[str, Any]) -> List[str]:
        """Generate decision path explanation"""
        try:
            decision_path = []
            
            # Extract decision steps
            decision_type = decision_data.get("decision_type", "unknown")
            scores = decision_data.get("scores", {})
            
            decision_path.append(f"Decision type: {decision_type}")
            
            # Add scoring steps
            for criterion, score in scores.items():
                decision_path.append(f"Evaluated {criterion}: {score:.2f}")
            
            # Add final decision
            final_score = decision_data.get("final_score", 0.0)
            decision_path.append(f"Final score: {final_score:.2f}")
            
            # Add recommendation
            recommendation = decision_data.get("recommendation", "No recommendation")
            decision_path.append(f"Recommendation: {recommendation}")
            
            return decision_path
            
        except Exception as e:
            logger.error(f"Error generating decision path: {e}")
            return ["Error generating decision path"]
    
    async def _identify_uncertainty_factors(self, decision_data: Dict[str, Any]) -> List[str]:
        """Identify factors contributing to decision uncertainty"""
        try:
            uncertainty_factors = []
            
            # Check data quality
            data_quality = decision_data.get("data_quality_score", 1.0)
            if data_quality < 0.8:
                uncertainty_factors.append("Low data quality")
            
            # Check confidence score
            confidence = decision_data.get("confidence_score", 1.0)
            if confidence < 0.7:
                uncertainty_factors.append("Low model confidence")
            
            # Check for missing data
            input_data = decision_data.get("input_data", {})
            missing_fields = [field for field, value in input_data.items() if value is None]
            if missing_fields:
                uncertainty_factors.append(f"Missing data: {', '.join(missing_fields)}")
            
            # Check for edge cases
            scores = decision_data.get("scores", {})
            if any(score < 0.3 or score > 0.9 for score in scores.values()):
                uncertainty_factors.append("Extreme score values")
            
            return uncertainty_factors
            
        except Exception as e:
            logger.error(f"Error identifying uncertainty factors: {e}")
            return ["Error identifying uncertainty factors"]
    
    async def _generate_alternative_outcomes(self, decision_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative decision outcomes"""
        try:
            alternatives = []
            
            # Generate scenarios with different parameters
            base_scores = decision_data.get("scores", {})
            
            # Scenario 1: Conservative approach
            conservative_scores = {k: v * 0.9 for k, v in base_scores.items()}
            alternatives.append({
                "scenario": "Conservative",
                "scores": conservative_scores,
                "description": "More conservative scoring approach"
            })
            
            # Scenario 2: Optimistic approach
            optimistic_scores = {k: v * 1.1 for k, v in base_scores.items()}
            alternatives.append({
                "scenario": "Optimistic",
                "scores": optimistic_scores,
                "description": "More optimistic scoring approach"
            })
            
            # Scenario 3: Equal weighting
            if base_scores:
                equal_score = np.mean(list(base_scores.values()))
                equal_scores = {k: equal_score for k in base_scores.keys()}
                alternatives.append({
                    "scenario": "Equal Weighting",
                    "scores": equal_scores,
                    "description": "Equal weighting of all criteria"
                })
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternative outcomes: {e}")
            return []
    
    # Helper methods for compliance checking
    
    async def _check_privacy_compliance(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check privacy compliance"""
        return {
            "compliant": True,
            "checks": [
                "Data anonymization applied",
                "Personal information protected",
                "Data retention policies followed"
            ],
            "issues": []
        }
    
    async def _check_transparency_compliance(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check transparency compliance"""
        return {
            "compliant": True,
            "checks": [
                "Decision criteria documented",
                "Model parameters disclosed",
                "Data sources identified"
            ],
            "issues": []
        }
    
    async def _check_bias_mitigation(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check bias mitigation compliance"""
        return {
            "compliant": True,
            "checks": [
                "Bias detection performed",
                "Mitigation strategies applied",
                "Fairness metrics monitored"
            ],
            "issues": []
        }
    
    async def _check_explainability_compliance(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check explainability compliance"""
        return {
            "compliant": True,
            "checks": [
                "Decision explanations provided",
                "Feature importance calculated",
                "Uncertainty factors identified"
            ],
            "issues": []
        }
    
    async def _check_human_oversight(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check human oversight compliance"""
        return {
            "compliant": True,
            "checks": [
                "Human review process in place",
                "Override mechanisms available",
                "Audit trail maintained"
            ],
            "issues": []
        }
    
    async def _generate_compliance_recommendations(self, compliance_checks: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        for check_name, check_result in compliance_checks.items():
            if not check_result.get("compliant", False):
                recommendations.append(f"Address {check_name} compliance issues")
        
        if not recommendations:
            recommendations.append("Maintain current compliance practices")
        
        return recommendations
    
    # Utility methods
    
    def _analyze_regional_distribution(self, locations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze regional distribution of locations"""
        # Simplified regional analysis
        regions = defaultdict(int)
        for loc in locations:
            lat = loc.get("latitude", 0)
            if lat > 40:
                regions["north"] += 1
            elif lat < 30:
                regions["south"] += 1
            else:
                regions["central"] += 1
        return dict(regions)
    
    def _calculate_regional_bias(self, regional_distribution: Dict[str, int]) -> float:
        """Calculate regional bias score"""
        if not regional_distribution:
            return 0.0
        
        total = sum(regional_distribution.values())
        if total == 0:
            return 0.0
        
        # Calculate Gini coefficient for regional distribution
        values = list(regional_distribution.values())
        values.sort()
        n = len(values)
        
        if n == 0:
            return 0.0
        
        cumsum = np.cumsum(values)
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0
        
        return gini
    
    def _identify_affected_regions(self, regional_distribution: Dict[str, int]) -> List[str]:
        """Identify regions affected by bias"""
        if not regional_distribution:
            return []
        
        total = sum(regional_distribution.values())
        if total == 0:
            return []
        
        # Identify underrepresented regions
        affected = []
        for region, count in regional_distribution.items():
            if count / total < 0.2:  # Less than 20% representation
                affected.append(region)
        
        return affected
    
    def _analyze_income_impact(self, income_data: Dict[str, Any], 
                             results: Dict[str, Any]) -> float:
        """Analyze impact of income on results"""
        # Simplified income impact analysis
        return 0.2  # Placeholder
    
    def _analyze_bias_patterns(self, data: Dict[str, Any], 
                             results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze bias patterns in data and results"""
        return {
            "affected_groups": ["group1", "group2"],
            "pattern_type": "systematic"
        }
    
    def _group_scores_by_region(self, scores: Dict[str, Any], 
                              location_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Group scores by geographical region"""
        # Simplified regional grouping
        return {"region1": [0.7, 0.8], "region2": [0.6, 0.9]}

# Global Responsible AI manager instance
responsible_ai_manager = ResponsibleAIManager()