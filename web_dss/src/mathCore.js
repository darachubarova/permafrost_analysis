// Math core module for Permafrost degradation and Hydrological risks in Yakutia
// Ported from permafrost_model Python package for C:\Diploma\permafrost_analysis\web_dss

export class StefanClassicModel {
  constructor(E = 4.3448) {
    this.E = E;
  }

  predict(DDT) {
    if (DDT < 0) return 0.0;
    return this.E * Math.sqrt(DDT);
  }
}

export class StefanHybridModel {
  constructor(E_base = 4.1866, beta = 0.00155) {
    this.E_base = E_base;
    this.beta = beta;
  }

  predict(DDT, H_snow) {
    if (DDT < 0) return 0.0;
    return this.E_base * Math.sqrt(DDT) * (1.0 + this.beta * H_snow);
  }
}

export class EmpiricalRegressionModel {
  constructor(c0 = 197.99, c1 = 0.0096, c2 = -0.0051, c3 = 0.370, c4 = -0.0045) {
    this.c0 = c0;
    this.c1 = c1;
    this.c2 = c2;
    this.c3 = c3;
    this.c4 = c4;
  }

  predict(DDT, DDF, H_snow, P_summer) {
    return this.c0 + this.c1 * DDT + this.c2 * DDF + this.c3 * H_snow + this.c4 * P_summer;
  }
}

export class SoilThermalTrendModel {
  constructor(slope = 0.02150, intercept = -43.44) {
    this.slope = slope;
    this.intercept = intercept;
  }

  predict(year) {
    return this.slope * year + this.intercept;
  }

  getFailureYear() {
    if (this.slope <= 0) return Infinity;
    return -this.intercept / this.slope;
  }
}

export class HydroPropagationModel {
  constructor() {
    this.default_lags = {
      lensk_yakutsk: 4.4,
      olekminsk_yakutsk: 3.9,
      yakutsk_zhigansk: 3.8
    };
    this.coef_a0 = -120.0;
    this.coef_a1 = 0.38;
    this.coef_a2 = 0.42;
  }

  predictPeakLevel(h_lensk, h_olek) {
    return this.coef_a0 + this.coef_a1 * h_lensk + this.coef_a2 * h_olek;
  }

  evaluateWarning(level) {
    if (level >= 850) {
      return {
        status: "CRITICAL",
        msg_ru: "Угроза масштабных затоплений, разрушения береговой линии и дамб (Порог 850 см пройден!)",
        msg_en: "Threat of massive flooding, coastline erosion, and dam failures (850 cm threshold crossed!)"
      };
    } else if (level >= 700) {
      return {
        status: "WARNING",
        msg_ru: "Выход воды на пойму, подтопление дачных участков и дорог (Порог 700 см пройден)",
        msg_en: "Water flooding floodplains, submerging dacha plots and low roads (700 cm threshold crossed)"
      };
    }
    return {
      status: "NORMAL",
      msg_ru: "Уровень воды в пределах нормы",
      msg_en: "River water levels are within safe seasonal parameters"
    };
  }
}

export class PSRS_Scorer {
  constructor() {
    this.stats = {
      alt: { mean: 221.5, std: 12.8 },
      t320: { mean: -0.58, std: 0.32 },
      snow: { mean: 35.4, std: 8.6 },
      ros: { mean: 1.6, std: 1.1 }
    };
  }

  compute_z(val, param) {
    const mean = this.stats[param].mean;
    const std = this.stats[param].std;
    return (val - mean) / std;
  }

  calculateScore(alt, t320, h_snow, ros_days) {
    const z_alt = this.compute_z(alt, 'alt');
    const z_t320 = this.compute_z(t320, 't320');
    const z_snow = this.compute_z(h_snow, 'snow');
    const z_ros = this.compute_z(ros_days, 'ros');

    const weighted_z = 0.4 * z_alt + 0.3 * z_t320 + 0.2 * z_snow + 0.1 * z_ros;
    const score = 5.0 + 1.6 * weighted_z;
    return Math.min(Math.max(score, 0.0), 10.0);
  }
}

export class DecisionSupportSystem {
  constructor() {
    this.scorer = new PSRS_Scorer();
  }

  evaluateYear(alt, t320, h_snow, ros_days) {
    const score = this.scorer.calculateScore(alt, t320, h_snow, ros_days);
    let level, color, recommendations_ru, recommendations_en;

    if (score < 4.0) {
      level = "LOW";
      color = "GREEN";
      recommendations_ru = [
        "1. Плановый мониторинг: Ежегодное геофизическое и термическое обследование фундаментов зданий.",
        "2. Контроль скважин: Снятие температурных показателей термометрических скважин 2 раза в год.",
        "3. Обычный режим эксплуатации объектов жизнеобеспечения населенного пункта."
      ];
      recommendations_en = [
        "1. Routine monitoring: Annual geophysical and thermal surveys of building foundations.",
        "2. Borehole logging: Retrieve temperature logs from thermometric wells twice a year.",
        "3. Normal operation mode of municipal and civil infrastructure objects."
      ];
    } else if (score < 7.0) {
      level = "MODERATE";
      color = "YELLOW";
      recommendations_ru = [
        "1. Усиленный мониторинг: Переход на ежемесячное обследование фундаментов в теплый сезон.",
        "2. Инженерная превенция: Активация сезонно-действующих охлаждающих устройств (термосифонов).",
        "3. Дренаж: Организация скорейшего отвода талых и дождевых вод от свайных полей во избежание обводнения.",
        "4. Проверка готовности муниципальных коммунальных аварийных бригад."
      ];
      recommendations_en = [
        "1. Enhanced monitoring: Transition to monthly foundation surveys during the warm season.",
        "2. Engineering prevention: Activate seasonal cooling thermopiles (siphons).",
        "3. Active drainage: Organize rapid diversion of melt and rain water from pile fields to prevent waterlogging.",
        "4. Check readiness of municipal utility repair and emergency crews."
      ];
    } else {
      level = "EXTREME";
      color = "RED";
      recommendations_ru = [
        "1. Экстренное реагирование: Введение режима ЧС регионального/муниципального характера.",
        "2. Защита населения: Экстренное выселение жителей из деформированных зданий с угрозой обрушения.",
        "3. Защита инфраструктуры: Локальное отключение газораспределительных сетей и ЛЭП в аварийных зонах.",
        "4. Инженерная защита: Проведение срочных строительно-монтажных работ по укреплению несущих свай.",
        "5. Развертывание оперативного штаба МЧС России по координации спасательных сил."
      ];
      recommendations_en = [
        "1. Emergency response: Declare a regional/municipal State of Emergency.",
        "2. Public safety: Urgent evacuation of residents from severely deformed buildings with collapse risk.",
        "3. Utility isolation: Selective isolation of gas distribution lines and power grids in hazard zones.",
        "4. Geotechnical shoring: Execute rapid reinforcement and shoring of structural pile foundations.",
        "5. Mobilization of EMERCOM emergency headquarters to coordinate rescue forces."
      ];
    }

    return {
      score: Number(score.toFixed(2)),
      level,
      color,
      recommendations_ru,
      recommendations_en
    };
  }
}
