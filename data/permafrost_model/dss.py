import numpy as np

class PSRS_Scorer:
    """
    PSRS (Permafrost Settlement Risk Score) Scorer.
    Combines climate and soil metrics into a composite risk score (0 to 10):
    PSRS = clip(5.0 + 1.5 * (0.4 * Z_ALT + 0.3 * Z_T320 + 0.2 * Z_Hsnow + 0.1 * Z_ROS), 0.0, 10.0)
    """
    def __init__(self):
        # Default historical stats for Yakutsk (Tuymada)
        self.stats = {
            'alt': {'mean': 221.5, 'std': 12.8},
            't320': {'mean': -0.58, 'std': 0.32},
            'snow': {'mean': 35.4, 'std': 8.6},
            'ros': {'mean': 1.6, 'std': 1.1}
        }

    def compute_z(self, val, param):
        """
        Compute standard Z-score for a parameter.
        """
        mean = self.stats[param]['mean']
        std = self.stats[param]['std']
        return (val - mean) / std

    def calculate_score(self, alt, t320, h_snow, ros_days):
        """
        Calculate PSRS score (0 to 10).
        """
        z_alt = self.compute_z(alt, 'alt')
        z_t320 = self.compute_z(t320, 't320')
        z_snow = self.compute_z(h_snow, 'snow')
        z_ros = self.compute_z(ros_days, 'ros')
        
        weighted_z = 0.4 * z_alt + 0.3 * z_t320 + 0.2 * z_snow + 0.1 * z_ros
        score = 5.0 + 1.6 * weighted_z
        return float(np.clip(score, 0.0, 10.0))


class DecisionSupportSystem:
    """
    Decision Support System for public authorities and emergency services (MCHS).
    Translates PSRS scores into actionable response guidelines.
    """
    def __init__(self):
        self.scorer = PSRS_Scorer()

    def evaluate_year(self, alt, t320, h_snow, ros_days):
        """
        Evaluate composite risk and return detailed bilingual recommendations.
        """
        score = self.scorer.calculate_score(alt, t320, h_snow, ros_days)
        
        if score < 4.0:
            level = "LOW"
            color = "GREEN"
            recommendations_ru = [
                "1. Плановый мониторинг: Ежегодное геофизическое и термическое обследование фундаментов зданий.",
                "2. Контроль скважин: Снятие температурных показателей термометрических скважин 2 раза в год.",
                "3. Обычный режим эксплуатации объектов жизнеобеспечения населенного пункта."
            ]
            recommendations_en = [
                "1. Routine monitoring: Annual geophysical and thermal surveys of building foundations.",
                "2. Borehole logging: Retrieve temperature logs from thermometric wells twice a year.",
                "3. Normal operation mode of municipal and civil infrastructure objects."
            ]
        elif score < 7.0:
            level = "MODERATE"
            color = "YELLOW"
            recommendations_ru = [
                "1. Усиленный мониторинг: Переход на ежемесячное обследование фундаментов в теплый сезон.",
                "2. Инженерная превенция: Активация сезонно-действующих охлаждающих устройств (термосифонов).",
                "3. Дренаж: Организация скорейшего отвода талых и дождевых вод от свайных полей во избежание обводнения.",
                "4. Проверка готовности муниципальных коммунальных аварийных бригад."
            ]
            recommendations_en = [
                "1. Enhanced monitoring: Transition to monthly foundation surveys during the warm season.",
                "2. Engineering prevention: Activate seasonal cooling thermopiles (siphons).",
                "3. Active drainage: Organize rapid diversion of melt and rain water from pile fields to prevent waterlogging.",
                "4. Check readiness of municipal utility repair and emergency crews."
            ]
        else:
            level = "EXTREME"
            color = "RED"
            recommendations_ru = [
                "1. Экстренное реагирование: Введение режима ЧС регионального/муниципального характера.",
                "2. Защита населения: Экстренное выселение жителей из деформированных зданий с угрозой обрушения.",
                "3. Защита инфраструктуры: Локальное отключение газораспределительных сетей и ЛЭП в аварийных зонах.",
                "4. Инженерная защита: Проведение срочных строительно-монтажных работ по укреплению несущих свай.",
                "5. Развертывание оперативного штаба МЧС России по координации спасательных сил."
            ]
            recommendations_en = [
                "1. Emergency response: Declare a regional/municipal State of Emergency.",
                "2. Public safety: Urgent evacuation of residents from severely deformed buildings with collapse risk.",
                "3. Utility isolation: Selective isolation of gas distribution lines and power grids in hazard zones.",
                "4. Geotechnical shoring: Execute rapid reinforcement and shoring of structural pile foundations.",
                "5. Mobilization of EMERCOM emergency headquarters to coordinate rescue forces."
            ]
            
        return {
            'score': round(score, 2),
            'level': level,
            'color': color,
            'recommendations_ru': recommendations_ru,
            'recommendations_en': recommendations_en
        }
