import { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Activity,
  Thermometer,
  Droplets,
  Database,
  Calendar,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Info,
  Globe,
  Sun,
  Moon,
  TrendingDown,
  ArrowRight,
  Settings,
  BookOpen,
  FileCode,
  Play,
  Download,
  RefreshCw,
  X
} from 'lucide-react';
import './App.css';
import {
  StefanClassicModel,
  StefanHybridModel,
  EmpiricalRegressionModel,
  SoilThermalTrendModel,
  HydroPropagationModel,
  DecisionSupportSystem
} from './mathCore';
import historicalDataRaw from './historicalData.json';

// Ensure data is sorted by year
const historicalData = Object.values(historicalDataRaw).sort((a, b) => a.year - b.year);

// Bilingual Dictionary
const t = {
  ru: {
    brandName: "МЕРЗЛОТА-ЧС",
    brandDesc: "система поддержки принятия решений ГО ЧС",
    authorName: "Разработано для ВКР",
    langToggle: "EN",
    themeToggleLight: "Светлая",
    themeToggleDark: "Тёмная",
    alertBanner: "Внимание: Зафиксировано долгосрочное повышение температуры грунтов на глубине 3.2м по тренду Якутска!",
    
    // Sidebar Tabs
    tabOverview: "Мониторинг и Обзор",
    tabDss: "Оценка риска ЧС",
    tabAlt: "Модели Протаивания",
    tabRiver: "Паводки на Лене",
    tabArchive: "Архив Наблюдений",
    tabSoil: "Стабильность Грунтов",
    
    // Overview tab
    overviewTitle: "Монитор зоны вечной мерзлоты",
    overviewDesc: "Комплексный анализ состояния многолетнемерзлых грунтов Центральной Якутии и рисков для инфраструктуры",
    kpiAvgAlt: "Ср. глубина протаивания",
    kpiAvgAltDesc: "За период 2005-2024 гг.",
    kpiMaxTemp: "Пик. темп. грунта (3.2м)",
    kpiMaxTempDesc: "Экстремальный прогрев 2021 г.",
    kpiMaxFlood: "Исторический паводок",
    kpiMaxFloodDesc: "г. Ленск (май 2009 г.)",
    kpiRiskYear: "Опасные годы",
    kpiRiskYearDesc: "Умеренный/Высокий уровень риска",
    
    introTitle: "Обоснование математической модели",
    introText1: "Данный аналитический комплекс разработан на основе долгосрочных климатологических и геокриологических данных наблюдений в Якутии за последние 20 лет.",
    introText2: "Из-за прогрессирующего потепления климата в Якутске скорость деградации вечной мерзлоты возросла. Средняя глубина сезонного таяния (ALT) увеличилась, что вызывает просадки грунтов, разрушение дорожного полотна, а также угрожает устойчивости свайных оснований зданий и инженерных коммуникаций.",
    introBullet1: "Индексы МЧС: Разработан взвешенный многофакторный индекс PSRS для выработки регламентов спасательных служб.",
    introBullet2: "Модели протаивания: Интегрированы классические уравнения теплопроводности Стефана и гибридные эмпирические модели.",
    introBullet3: "Прогноз паводков: Линейно-динамический лаг волны позволяет оперативно предупреждать затопление жилых зон.",
    
    // DSS tab
    dssTitle: "Оценка геотехнического риска возникновения ЧС",
    dssDesc: "Многофакторный индекс PSRS (Permafrost Stability Risk Score) и операционные регламенты реагирования",
    dssSliders: "Параметры симуляции грунтов",
    dssDiagram: "Интерактивная деформация свайного поля",
    dssScore: "Индекс PSRS",
    dssLevel: "Уровень опасности",
    dssLow: "Низкий",
    dssMod: "Умеренный",
    dssExt: "Экстремальный",
    dssRecs: "Оперативный регламент служб",
    
    sliderAlt: "Глубина протаивания (ALT)",
    sliderT320: "Температура грунта (3.2м)",
    sliderSnow: "Макс. высота снежного покрова",
    sliderRos: "Дни дождя на снег (ROS)",
    
    diagramAir: "Атмосфера",
    diagramActive: "Слой протаивания (ALT): ",
    diagramFrozen: "Вечная мерзлота (Стабильная)",
    diagramPile: "Железобетонная свая",
    diagramNormal: "Норма",
    diagramStrain: "КРИТИЧЕСКИЙ СДВИГ / ДЕФОРМАЦИЯ ФУНДАМЕНТА!",
    
    // ALT Models tab
    altTitle: "Математическое моделирование глубины протаивания",
    altDesc: "Сравнительный анализ теплопроводных моделей Стефана и многофакторной регрессии",
    altParams: "Климатические предикторы года",
    altModelComp: "Сравнение выходов моделей (ALT, см)",
    altDdt: "Сумма градусо-суток таяния (DDT)",
    altDdf: "Сумма градусо-суток замерзания (DDF)",
    altPrecip: "Летние осадки (precip_summer)",
    
    stefanClassic: "Стефан (Классический)",
    stefanHybrid: "Стефан (Снеговой гибрид)",
    empRegression: "Многофакторная регрессия",
    modelDiffMeasured: "Погрешность относительно факта: ",
    noMeasured: "Нет фактических замеров в этом режиме",
    
    // Notebook specific strings
    notebookTitle: "Интерактивный Jupyter-ноутбук модели",
    notebookRunAll: "Запустить всё",
    notebookRestart: "Сбросить ядро",
    notebookDownload: "Скачать блокнот",
    notebookClose: "Закрыть блокнот",
    notebookStatusReady: "Ядро: Python 3 (Ready)",
    notebookStatusBusy: "Ядро: Вычисления...",
    notebookInputHeader: "Интерактивные параметры ячейки",
    
    // River Tab
    riverTitle: "Прогнозирование паводков на реке Лена",
    riverDesc: "Динамическая гидродинамическая модель распространения паводковой волны по Ленску и Олёкминску",
    riverParams: "Показания верховых гидропостов (см)",
    riverForecast: "Прогноз для низовых створов (см)",
    riverLenskPeak: "Пик паводка в Ленске",
    riverOlekPeak: "Пик паводка в Олёкминске",
    riverYktPeak: "Прогноз уровня у Якутска",
    riverTimeLag: "Ожидаемый добег волны: 4.1 дня",
    riverAlertNormal: "Уровень воды в норме. Угроза отсутствует.",
    riverAlertWarning: "ВНИМАНИЕ! Вода выходит на пойму. Подтопление дач и прибрежных дорог.",
    riverAlertDanger: "ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ! Прорыв защитной дамбы Якутска! Риск затопления жилых кварталов.",
    
    // Archive Tab
    archiveTitle: "Историческая база данных наблюдений (2005-2024)",
    archiveDesc: "Нажмите на любую строку или точку на графике, чтобы мгновенно загрузить показатели этого года в симуляторы СППР!",
    archiveLoadMsg: "Данные {year} года успешно загружены во все калькуляторы!",
    archiveHeaderYear: "Год",
    archiveHeaderDdt: "DDT",
    archiveHeaderDdf: "DDF",
    archiveHeaderSnow: "Снег (см)",
    archiveHeaderTemp: "Т (3.2м, °С)",
    archiveHeaderAlt: "Факт ALT (см)",
    archiveHeaderFlood: "Пик Якутск (см)",
    archiveHeaderAnoms: "Аномалии / Сигналы",
    chartTitle: "Интерактивный график многолетних трендов Якутска",
    legendDdt: "Градусо-сутки таяния (DDT) [Левая шкала]",
    legendAlt: "Глубина протаивания (ALT, см) [Правая шкала]",
    
    // Soil Stability Tab
    soilTitle: "Термическая деградация и несущая способность свай",
    soilDesc: "Экстраполяционное прогнозирование прочности оснований при оттаивании до 2060 года",
    soilParams: "Параметры прогноза времени",
    soilTimeline: "Год долгосрочного прогноза",
    soilTrendValue: "Прогнозная температура грунта (3.2м)",
    soilStatusSafe: "Фундамент стабилен. Мерзлота твердая.",
    soilStatusDanger: "АВАРИЙНОЕ ОТТАИВАНИЕ! Температура грунта выше 0°С. Полная потеря несущей способности свай!",
    soilFailureTitle: "Расчетный год разрушения свайных полей",
    soilYearsLeft: "Осталось лет до перехода через 0°С:",
    
    tabGuide: "Гид по Системе",
    guideTitle: "Путеводитель и База Знаний СППР",
    guideDesc: "Пошаговое руководство, описание математических моделей и технологий прогнозирования деградации вечной мерзлоты",
    guideLaunchTour: "Запустить интерактивный тур",
    guideTheoryTitle: "Теоретические и математические основы",
    guideTheoryDesc: "Система объединяет классические физические уравнения, современные эмпирические регрессии и гидродинамические модели добега волны.",
    
    theoryStefanTitle: "1. Физическая модель Стефана (ALT)",
    theoryStefanBody: "Классическое уравнение Стефана используется для расчета глубины сезонного протаивания (ALT) на основе баланса тепла. Формула связывает протаивание с суммой градусо-суток таяния (DDT) и свойствами грунта: ALT = sqrt((2 * λ * DDT) / (ρ * L)). В гибридной версии также учитывается снеговое утепление, снижающее отдачу тепла зимой.",
    
    theoryDssTitle: "2. Геотехнические риски и индекс PSRS",
    theoryDssBody: "Многофакторный индекс PSRS (Permafrost Stability Risk Score) вычисляет риск деформаций оснований. С ростом температуры грунта снижается удельное сцепление мерзлой породы со свайным бетоном. При росте ALT свая теряет боковую анкеровку, что приводит к выдавливанию или осадке свайных полей.",
    
    theoryRiverTitle: "3. Прогноз паводков на Лене",
    theoryRiverBody: "Динамическая гидрологическая модель рассчитывает уровень воды в Якутске по верховым гидропостам Ленск и Олёкминск: H_Ykt = α * H_Lensk + β * H_Olek + γ. Среднее время добега волны составляет 4.1 дня, предоставляя службам ГО ЧС критическое время для предупреждения населения.",
    
    theorySoilTitle: "4. Прогноз несущей способности до 2060 г.",
    theorySoilBody: "Климатический тренд потепления в Якутске (повышение температур грунта на 0.046°С/год) используется для экстраполяции. При приближении температуры на глубине 3.2м к 0°С несущая способность свай стремится к нулю, что приводит к разрушению инженерных конструкций.",
    
    tourTitle: "Обучающий тур",
    tourPrev: "Назад",
    tourNext: "Далее",
    tourFinish: "Завершить",
    tourIndicator: "Шаг {step} из 6",
    
    tourStepTitle_0: "Мониторинг криолитозоны",
    tourStepDesc_0: "Добро пожаловать в СППР! Этот модуль показывает текущую климатическую обстановку: глубину таяния (ALT) и температуру на глубине 3.2м. Справа вы видите живую схему свайного фундамента, уходящего в мерзлый грунт.",
    
    tourStepTitle_1: "Симулятор рисков и свай",
    tourStepDesc_1: "Здесь рассчитывается индекс PSRS для служб ГО ЧС. Попробуйте сдвинуть ползунок ALT или температуры грунта: свая на схеме начнет испытывать сдвиг и подсветится красными стрелками критических сдвиговых напряжений!",
    
    tourStepTitle_2: "Ядра расчета протаивания",
    tourStepDesc_2: "Сравнение трех математических моделей расчета сезонного таяния (ALT) от DDT и осадков: физического уравнения Стефана, гибридной модели с учетом снега и многофакторной регрессии, откалиброванной по фактам. Обратите внимание: названия моделей в карточках сравнения и в математической справке внизу теперь кликабельны! Нажмите на любое подчеркнутое название, чтобы открыть интерактивный Jupyter-ноутбук модели.",
    
    tourStepTitle_3: "Прогнозирование паводков",
    tourStepDesc_3: "Этот модуль рассчитывает паводковые уровни у Якутска на основе верховых постов Ленска и Олёкминска. Система автоматически рассчитывает лаг волны (4.1 дня) и предупреждает при угрозах прорыва дамбы.",
    
    tourStepTitle_4: "Исторический архив",
    tourStepDesc_4: "База данных Якутска за 20 лет. Кликните на любую строку таблицы или точку на графике, и все симуляторы СППР мгновенно загрузят данные этого года для ретроспективного анализа чрезвычайных ситуаций!",
    
    tourStepTitle_5: "Прочность свай до 2060 года",
    tourStepDesc_5: "Долгосрочный прогноз деградации вечной мерзлоты. На основе линейного климатического тренда Якутии система определяет расчетный год потери несущей способности свай и выводит обратный отсчет."
  },
  en: {
    brandName: "PERMAFROST-EMERCOM",
    brandDesc: "emergency decision support system",
    authorName: "Developed for Thesis",
    langToggle: "RU",
    themeToggleLight: "Light",
    themeToggleDark: "Dark",
    alertBanner: "Warning: Long-term temperature trend at 3.2m depth shows significant soil warming in Yakutsk area!",
    
    // Sidebar Tabs
    tabOverview: "Overview & Monitor",
    tabDss: "Risk Evaluator (EMERCOM)",
    tabAlt: "Thaw Depth Models",
    tabRiver: "Lena River Floods",
    tabArchive: "Historical Database",
    tabSoil: "Soil Stability",
    
    // Overview tab
    overviewTitle: "Geocryological Monitoring Dashboard",
    overviewDesc: "Integrated analysis of permafrost degradation and infrastructural risks in Central Yakutia",
    kpiAvgAlt: "Avg Thaw Depth (ALT)",
    kpiAvgAltDesc: "For historical period 2005-2024",
    kpiMaxTemp: "Peak Soil Temp (3.2m)",
    kpiMaxTempDesc: "Recorded during hot summer 2021",
    kpiMaxFlood: "Historical Peak Flood",
    kpiMaxFloodDesc: "Lensk station (May 2009)",
    kpiRiskYear: "Critical Risk Years",
    kpiRiskYearDesc: "Years with Moderate/High risk level",
    
    introTitle: "Mathematical Model Rationale",
    introText1: "This decision support complex is built using 20 years of continuous climatological and geocryological observations in the Republic of Sakha (Yakutia).",
    introText2: "Driven by rapid regional warming, the active layer thickness (ALT) has expanded significantly. This creates major geotechnical stress, causing building foundations to settle, roads to deform, and pipelines to experience severe shear stresses.",
    introBullet1: "EMERCOM Protocols: The multi-criteria PSRS index transforms physical measurements into operational mitigation action items.",
    introBullet2: "Predictive Models: Combines physical classical Stefan heat flow, hybrid snow-insulated Stefan, and multi-variable regressions.",
    introBullet3: "Flood Propagation: A linear lag propagation model calculates river peak levels to issue timely flood evacuation alerts.",
    
    // DSS tab
    dssTitle: "Geotechnical Emergency Risk Assessment",
    dssDesc: "PSRS (Permafrost Stability Risk Score) multi-criteria index and EMERCOM response workflows",
    dssSliders: "Soil Simulation Inputs",
    dssDiagram: "Live Foundation Displacement Model",
    dssScore: "PSRS Index",
    dssLevel: "Geotechnical Threat Level",
    dssLow: "Low",
    dssMod: "Moderate",
    dssExt: "Extreme",
    dssRecs: "Operational Protocol Actions",
    
    sliderAlt: "Active Layer Thickness (ALT)",
    sliderT320: "Soil Temperature (3.2m)",
    sliderSnow: "Max Winter Snow Depth",
    sliderRos: "Rain-on-Snow Days (ROS)",
    
    diagramAir: "Atmosphere",
    diagramActive: "Thawed Layer (ALT): ",
    diagramFrozen: "Permafrost (Stable Ground)",
    diagramPile: "Concrete Foundation Pile",
    diagramNormal: "Normal",
    diagramStrain: "CRITICAL FOUNDATION SHIFT / COLLAPSE RISK!",
    
    // ALT Models tab
    altTitle: "Predicting Active Layer Thickness",
    altDesc: "Comparative evaluation of thermal Stefan physics and multi-variable empirical regressions",
    altParams: "Annual Climate Predictors",
    altModelComp: "Calculated ALT Output Comparison (cm)",
    altDdt: "Degree Days of Thawing (DDT)",
    altDdf: "Degree Days of Freezing (DDF)",
    altPrecip: "Summer Precipitation (precip_summer)",
    
    stefanClassic: "Classical Stefan Equation",
    stefanHybrid: "Snow-Insulated Hybrid Stefan",
    empRegression: "Multi-Variable Empirical Regression",
    modelDiffMeasured: "Error vs measured actuals: ",
    noMeasured: "No measured value for this specific state",
    
    // Notebook specific strings
    notebookTitle: "Interactive Jupyter Notebook",
    notebookRunAll: "Run All Cells",
    notebookRestart: "Restart Kernel",
    notebookDownload: "Download ipynb",
    notebookClose: "Close Notebook",
    notebookStatusReady: "Kernel: Python 3 (Ready)",
    notebookStatusBusy: "Kernel: Busy...",
    notebookInputHeader: "Interactive Cell Parameters",
    
    // River Tab
    riverTitle: "Lena River Flood Propagation Warning",
    riverDesc: "Dynamic hydraulic wave routing model using upstream gauges at Lensk and Olekminsk",
    riverParams: "Upstream River Gauges (cm)",
    riverForecast: "Downstream Gauge Forecast (cm)",
    riverLenskPeak: "Peak Peak Level at Lensk",
    riverOlekPeak: "Peak Peak Level at Olekminsk",
    riverYktPeak: "Predicted Peak Level at Yakutsk",
    riverTimeLag: "Expected wave arrival: 4.1 days",
    riverAlertNormal: "River level is within safe seasonal limits. No flood hazard.",
    riverAlertWarning: "WARNING! River is flooding plain areas. Dacha plots and low-lying roads flooded.",
    riverAlertDanger: "STATE OF EMERGENCY! Yakutsk protective dyke breached! Threat to residential sectors.",
    
    // Archive Tab
    archiveTitle: "Historical Measurement Database (2005-2024)",
    archiveDesc: "Click any row or chart point to instantly load that year's parameters into the active interactive simulators!",
    archiveLoadMsg: "Year {year} loaded successfully into all calculators!",
    archiveHeaderYear: "Year",
    archiveHeaderDdt: "DDT",
    archiveHeaderDdf: "DDF",
    archiveHeaderSnow: "Snow (cm)",
    archiveHeaderTemp: "T (3.2m, °C)",
    archiveHeaderAlt: "Fact ALT (cm)",
    archiveHeaderFlood: "Peak Ykt (cm)",
    archiveHeaderAnoms: "Anomalies & Signals",
    chartTitle: "Yakutsk Long-term Climate Trend Chart",
    legendDdt: "Degree Days of Thawing (DDT) [Left Axis]",
    legendAlt: "Active Layer Thickness (ALT, cm) [Right Axis]",
    
    // Soil Stability Tab
    soilTitle: "Thermal Soil Degradation & Foundation Shoring",
    soilDesc: "Extrapolating structural pile bearing capacity and temperature profiles up to year 2060",
    soilParams: "Time Forecast Controls",
    soilTimeline: "Target Forecast Year",
    soilTrendValue: "Projected Soil Temp (3.2m)",
    soilStatusSafe: "Stable foundation. Frozen ground is solid.",
    soilStatusDanger: "STRUCTURAL FAILURE DETECTED! Ground temperature above 0°C. Foundation friction is lost!",
    soilFailureTitle: "Estimated Year of Structural Failure",
    soilYearsLeft: "Years left until soil crosses 0°C:",
    
    tabGuide: "System Guide",
    guideTitle: "Walkthrough & Knowledge Base",
    guideDesc: "Step-by-step guidance, mathematical models, and permafrost degradation forecasting technologies",
    guideLaunchTour: "Start Interactive Tour",
    guideTheoryTitle: "Theoretical & Mathematical Foundations",
    guideTheoryDesc: "The system integrates classical physics equations, modern empirical regressions, and wave lag hydrodynamics.",
    
    theoryStefanTitle: "1. Physics Stefan Model (ALT)",
    theoryStefanBody: "The classical Stefan equation calculates Active Layer Thickness (ALT) based on thermal equilibrium. It links soil thawing to thawing degree days (DDT): ALT = sqrt((2 * λ * DDT) / (ρ * L)), where λ is thermal conductivity and ρ*L is latent heat. The hybrid version includes snow insulation which reduces winter cooling.",
    
    theoryDssTitle: "2. Geotechnical Risks & PSRS Index",
    theoryDssBody: "The multi-criteria PSRS index assesses structural foundation risks. Soil warming reduces the friction coefficient between permafrost and concrete. As ALT expands, the pile loses lateral anchoring, leading to severe structural failure.",
    
    theoryRiverTitle: "3. Lena River Flood Forecasting",
    theoryRiverBody: "The wave routing model calculates peak water levels at Yakutsk using upstream gauges at Lensk and Olekminsk: H_Ykt = α * H_Lensk + β * H_Olek + γ. The average lag time is 4.1 days, giving civil defense teams critical response time.",
    
    theorySoilTitle: "4. Pile Friction Outlook (up to 2060)",
    theorySoilBody: "Soil warming trend at 3.2m depth (0.046°C/year) in Yakutsk is used to extrapolate pile stability. When soil temperature reaches 0°C, the bearing capacity drops to zero, causing foundation collapses.",
    
    tourTitle: "Interactive Tour",
    tourPrev: "Back",
    tourNext: "Next",
    tourFinish: "Finish",
    tourIndicator: "Step {step} of 6",
    
    tourStepTitle_0: "Permafrost Monitoring",
    tourStepDesc_0: "Welcome to the DSS! This tab shows current climatological markers: Active Layer Thickness (ALT) and soil temperature. The right side features a conceptual animated concrete pile embedded in frozen soil.",
    
    tourStepTitle_1: "Risk Simulator & Pile Shear",
    tourStepDesc_1: "This panel calculates the PSRS index for emergency services. Move the ALT or temperature sliders: the pile foundation model will dynamically deform as it loses frictional bond with thawing soil!",
    
    tourStepTitle_2: "Active Layer Solvers",
    tourStepDesc_2: "Comparative evaluation of three math solvers for Active Layer Thickness (ALT): classical physical Stefan equation, snow-insulated hybrid Stefan, and calibrated empirical regression. Tip: Model titles in the comparison cards and in the mathematical reference list at the bottom are now clickable! Click on any underlined title to open its simulated interactive Jupyter Notebook.",
    
    tourStepTitle_3: "Lena River Flood Routing",
    tourStepDesc_3: "This module calculates river peak levels to issue timely flood evacuation alerts based on a linear wave propagation lag model of 4.1 days.",
    
    tourStepTitle_4: "Historical Database",
    tourStepDesc_4: "Click any row in the 20-year table or a point on the chart to instantly inject historical values into all active simulators for analysis!",
    
    tourStepTitle_5: "Soil Stability Outlook (2060)",
    tourStepDesc_5: "Extrapolating soil temperature warming trends. Calculates the exact year of foundation bearing failure and displays a structural breakdown countdown timer."
  }
};

const notebookData = {
  classic: {
    filename: "stefan_classical_calibration.ipynb",
    downloadUrl: "./notebooks/stefan_classical.ipynb",
    cells: [
      {
        type: "markdown",
        content_ru: "### 1. Математическое описание классического уравнения Стефана\nУравнение Стефана связывает глубину протаивания (ALT) с теплофизическими свойствами грунта и суммой градусо-суток таяния (DDT). В простейшем инженерном виде:\n\n$$ALT = E \\cdot \\sqrt{DDT}$$\n\nгде E — калибровочный коэффициент теплофизических свойств (для Якутска $E \\approx 4.3448$).",
        content_en: "### 1. Mathematical Description of the Classical Stefan Equation\nThe Stefan equation relates the thawing depth (ALT) to the thermophysical properties of the soil and the sum of degree-days of thawing (DDT). In its simplest engineering form:\n\n$$ALT = E \\cdot \\sqrt{DDT}$$\n\nwhere E is the calibration coefficient of thermophysical properties ($E \\approx 4.3448$ for Yakutsk)."
      },
      {
        type: "code",
        code: "import numpy as np\nimport matplotlib.pyplot as plt\nfrom scipy.optimize import curve_fit\n\nprint(\"Libraries successfully imported. / Библиотеки успешно импортированы.\")",
        exec_ru: "Libraries successfully imported. / Библиотеки успешно импортированы.\n[Kernel] Окружение готово к вычислениям.",
        exec_en: "Libraries successfully imported. / Библиотеки успешно импортированы.\n[Kernel] Environment is ready for computation."
      },
      {
        type: "code",
        code: (params) => `def predict_alt(ddt, E=${params.E.toFixed(4)}):
    return E * np.sqrt(ddt)

# Прогноз для текущего значения DDT = ${params.DDT}
alt_predicted = predict_alt(${params.DDT})
print(f"Predicted ALT = {alt_predicted:.2f} cm")`,
        exec_ru: (params) => `Predicted ALT = ${(params.E * Math.sqrt(params.DDT)).toFixed(2)} cm
[Console] Вычисление завершено для DDT = ${params.DDT} °C·сут.`,
        exec_en: (params) => `Predicted ALT = ${(params.E * Math.sqrt(params.DDT)).toFixed(2)} cm
[Console] Calculation complete for DDT = ${params.DDT} °C-days.`
      },
      {
        type: "interactive_code",
        code: (params) => `# Настройка интерактивных параметров внутри ячейки:
lambda_stefan = ${params.E.toFixed(4)}  # Коэффициент E
ddt_value = ${params.DDT}      # Параметр DDT

# Построение графика модели от DDT (от 1800 до 2500)
ddt_range = np.linspace(1800, 2500, 100)
alt_fitted = lambda_stefan * np.sqrt(ddt_range)

plt.figure(figsize=(8, 4))
plt.plot(ddt_range, alt_fitted, '-', color='#ef4444', label=f'Stefan Model (E = {lambda_stefan})')
plt.scatter([2150], [201.5], color='#22d3ee', s=80, label='Yakutsk baseline (201.5 cm)')
plt.xlabel('DDT (°C-days)')
plt.ylabel('ALT (cm)')
plt.legend()
plt.show()`,
        interactive_fields: [
          { name: "E", label_ru: "Коэффициент E", label_en: "E Coefficient", min: 3.5, max: 5.0, step: 0.05 },
          { name: "DDT", label_ru: "Параметр DDT (°C-сут)", label_en: "DDT Parameter", min: 1800, max: 2500, step: 10 }
        ],
        render_plot: (params) => {
          const ddtRange = [];
          for (let d = 1800; d <= 2500; d += 14) {
            ddtRange.push({ ddt: d, alt: params.E * Math.sqrt(d) });
          }
          const currentAlt = params.E * Math.sqrt(params.DDT);
          return { ddtRange, currentAlt, params };
        }
      }
    ]
  },
  hybrid: {
    filename: "stefan_hybrid_snow_insulation.ipynb",
    downloadUrl: "./notebooks/stefan_hybrid.ipynb",
    cells: [
      {
        type: "markdown",
        content_ru: "### 1. Математическая модель снегового гибрида Стефана\nЗимний снег защищает грунт от замерзания. Теплые зимние грунты оттаивают глубже летом. Мы вводим коэффициент $\\beta$ для учета влияния высоты снежного покрова ($H_{snow}$):\n\n$$ALT = E_{base} \\cdot \\sqrt{DDT} \\cdot (1.0 + \\beta \\cdot H_{snow})$$\n\nгде $E_{base} \\approx 4.1866$ и $\\beta \\approx 0.00155$ для района Центральной Якутии.",
        content_en: "### 1. Mathematical Formulation of the Hybrid Stefan Model\nWinter snow protects the ground from deep cooling. Consequently, warmer soils in winter experience deeper thaw in summer. We introduce a sensitivity modifier $\\beta$ for max snow depth ($H_{snow}$):\n\n$$ALT = E_{base} \\cdot \\sqrt{DDT} \\cdot (1.0 + \\beta \\cdot H_{snow})$$\n\nwhere $E_{base} \\approx 4.1866$ and $\\beta \\approx 0.00155$ in Central Yakutsk region."
      },
      {
        type: "code",
        code: "import numpy as np\nimport matplotlib.pyplot as plt\nfrom scipy.optimize import curve_fit\n\nprint(\"Libraries successfully imported. / Библиотеки импортированы.\")",
        exec_ru: "Libraries successfully imported. / Библиотеки импортированы.\n[Kernel] Загружено ядро scipy-optimize.",
        exec_en: "Libraries successfully imported. / Библиотеки импортированы.\n[Kernel] scipy-optimize kernel loaded."
      },
      {
        type: "code",
        code: (params) => `def predict_alt_hybrid(ddt, h_snow, E_base=${params.E_base.toFixed(4)}, beta=${params.beta.toFixed(5)}):
    return E_base * np.sqrt(ddt) * (1.0 + beta * h_snow)

# Расчет для DDT = ${params.DDT} и высоты снега = ${params.snow} см
alt_predicted = predict_alt_hybrid(${params.DDT}, ${params.snow})
print(f"Predicted Thaw Depth (ALT) = {alt_predicted:.2f} cm")`,
        exec_ru: (params) => `Predicted Thaw Depth (ALT) = ${(params.E_base * Math.sqrt(params.DDT) * (1.0 + params.beta * params.snow)).toFixed(2)} cm
[Console] Расчет завершен. Высота снежного покрова внесла корректировку в классическую глубину Стефана.`,
        exec_en: (params) => `Predicted Thaw Depth (ALT) = ${(params.E_base * Math.sqrt(params.DDT) * (1.0 + params.beta * params.snow)).toFixed(2)} cm
[Console] Calculation completed. Winter snow depth introduced significant correction to standard Stefan physics.`
      },
      {
        type: "interactive_code",
        code: (params) => `# Интерактивная ячейка визуализации влияния снега:\nE_base = ${params.E_base.toFixed(4)}\nbeta = ${params.beta.toFixed(5)}\nsnow_value = ${params.snow}\nddt_value = ${params.DDT}

# График зависимости ALT от высоты снега при фиксированном DDT
snow_range = np.linspace(10, 60, 100)
alt_vs_snow = E_base * np.sqrt(ddt_value) * (1.0 + beta * snow_range)

plt.figure(figsize=(8, 4))
plt.plot(snow_range, alt_vs_snow, '-', color='#22d3ee', label='Hybrid Stefan Curve')
plt.scatter([snow_value], [${(params.E_base * Math.sqrt(params.DDT) * (1.0 + params.beta * params.snow)).toFixed(1)}], color='#ef4444', s=80, label='Current Point')
plt.xlabel('Winter Snow Depth (cm)')
plt.ylabel('ALT Thaw Depth (cm)')
plt.legend()
plt.show()`,
        interactive_fields: [
          { name: "E_base", label_ru: "Базовый E", label_en: "Base E", min: 3.5, max: 4.5, step: 0.05 },
          { name: "beta", label_ru: "Коэффициент β (снег)", label_en: "Beta (snow)", min: 0.0005, max: 0.003, step: 0.0001 },
          { name: "DDT", label_ru: "Параметр DDT (°C-сут)", label_en: "DDT Parameter", min: 1800, max: 2500, step: 10 },
          { name: "snow", label_ru: "Снежный покров (см)", label_en: "Snow Cover (cm)", min: 10, max: 60, step: 1 }
        ],
        render_plot: (params) => {
          const snowRange = [];
          for (let s = 10; s <= 60; s += 1) {
            snowRange.push({ snow: s, alt: params.E_base * Math.sqrt(params.DDT) * (1.0 + params.beta * s) });
          }
          const currentAlt = params.E_base * Math.sqrt(params.DDT) * (1.0 + params.beta * params.snow);
          return { snowRange, currentAlt, params };
        }
      }
    ]
  },
  regression: {
    filename: "empirical_regression_calibration.ipynb",
    downloadUrl: "./notebooks/empirical_regression.ipynb",
    cells: [
      {
        type: "markdown",
        content_ru: "### Научная новизна и преимущества эмпирической регрессионной модели\n**Эмпирическая регрессионная модель** — это наша общая научно-исследовательская разработка, рожденная в процессе совместного анализа данных.\n\nОна была рассчитана и откалибрована на основе реальных **20-летних метеорологических и геокриологических наблюдений** по району Якутска (2005–2024 гг.), которые мы детально исследовали на этапе анализа данных.\n\n#### В чем её главная научная ценность и преимущество:\n\n1. **Ограничения классической физики:**\n* Классическая модель Стефана (физическая) опирается исключительно на сумму градусо-суток таяния ($DDT$). Она прекрасна в теории, но предполагает, что грунт однороден, а перенос тепла идет только за счет теплопроводности талой зоны.\n* Она «слепа» к осадкам, влажности и термокарстовым процессам (просадкам грунта).\n\n2. **Сила нашего подхода (Регрессия):**\n* Наша модель учитывает не только тепловой баланс ($DDT$), но и **высоту снежного покрова** (термический буфер зимы $H_{snow}$), а также **летние осадки** ($P_{summer}$ — дожди ускоряют перенос тепла вглубь за счет конвекции воды и испарительного охлаждения).\n* Мы математически вывели калибровочные коэффициенты для Центральной Якутии, что дало превосходный коэффициент детерминации $R^2 = 0.86$ (высочайшая точность для натурных геокриологических измерений!).\n* Она компенсирует локальные аномалии — например, сильные осадки или просадки грунта, которые классическое уравнение Стефана физически не способно предсказать.",
        content_en: "### Scientific Novelty and Advantages of the Empirical Regression Model\nThe **Empirical Regression Model** is our joint scientific research development, born in the process of collaborative data analysis.\n\nIt was calculated and calibrated based on real **20-year meteorological and geocryological observations** in the Yakutsk region (2005–2024), which we investigated in detail during the data analysis phase.\n\n#### Key Scientific Value and Advantages:\n\n1. **Limitations of Classical Physics:**\n* The classical Stefan model (purely physical) relies solely on the sum of degree-days of thawing ($DDT$). While beautiful in theory, it assumes that the soil is homogeneous and that heat transfer occurs exclusively through thermal conduction of the thawed zone.\n* It is blind to precipitation, soil moisture, and thermokarst processes (ground subsidence).\n\n2. **The Power of Our Approach (Regression):**\n* Our model incorporates not only the thermal balance ($DDT$), but also the **winter snow depth** (acting as a winter thermal buffer $H_{snow}$), and **summer precipitation** ($P_{summer}$ — rainfall accelerates heat transfer downwards due to water convection and evapotranspirative cooling).\n* We mathematically derived calibration coefficients for Central Yakutia, yielding an outstanding coefficient of determination of $R^2 = 0.86$ (exceptionally high accuracy for in-situ geocryological measurements!).\n* It successfully compensates for local anomalies — such as heavy precipitation or soil subsidence — which the classical Stefan equation is physically incapable of predicting."
      },
      {
        type: "markdown",
        content_ru: "### 1. Многофакторное линейное уравнение регрессии (ALT)\nДля учета сложной динамики (осадки, испарение, зимний холод DDF) мы откалибровали линейную регрессию по 20 годам наблюдений в Якутске:\n\n$$ALT = c_0 + c_1 \\cdot DDT + c_2 \\cdot DDF + c_3 \\cdot H_{snow} + c_4 \\cdot P_{summer}$$\n\nгде коэффициенты:\n* $c_0 = 197.99$ (свободный член)\n* $c_1 = 0.0096$ (положительное влияние DDT)\n* $c_2 = -0.0051$ (отрицательное влияние DDF)\n* $c_3 = 0.370$ (зимнее снеговое утепление)\n* $c_4 = -0.0045$ (охлаждающий эффект летних осадков в Якутске)",
        content_en: "### 1. Multi-Variable Linear Regression Model (ALT)\nTo incorporate complex dynamics (evapotranspiration, summer rain, winter cold intensity DDF), we calibrated a multiple linear regression model using 20 years of continuous weather station records in Yakutsk:\n\n$$ALT = c_0 + c_1 \\cdot DDT + c_2 \\cdot DDF + c_3 \\cdot H_{snow} + c_4 \\cdot P_{summer}$$\n\nwhere calibrated coefficients are:\n* $c_0 = 197.99$ (Intercept)\n* $c_1 = 0.0096$ (Positive effect of summer thermal heat DDT)\n* $c_2 = -0.0051$ (Negative effect of winter cold index DDF)\n* $c_3 = 0.370$ (Winter snow insulation factor)\n* $c_4 = -0.0045$ (Cooling/evaporation effect of summer precipitation)"
      },
      {
        type: "code",
        code: "import numpy as np\nimport matplotlib.pyplot as plt\nimport statsmodels.api as sm\n\nprint(\"Libraries successfully imported. / Аналитический модуль готов.\")",
        exec_ru: "Libraries successfully imported. / Аналитический модуль готов.\n[Kernel] Загружена библиотека statsmodels.OLS.",
        exec_en: "Libraries successfully imported. / Аналитический модуль готов.\n[Kernel] statsmodels.OLS engine initialized."
      },
      {
        type: "code",
        code: (params) => `def predict_regression(ddt, ddf, h_snow, p_summer):
    # Уравнение с откалиброванными коэффициентами:
    return (${params.c0.toFixed(2)} + ${params.c1.toFixed(4)} * ddt + ${params.c2.toFixed(4)} * ddf + 
            ${params.c3.toFixed(3)} * h_snow + ${params.c4.toFixed(4)} * p_summer)

alt_pred = predict_regression(${params.DDT}, ${params.DDF}, ${params.snow}, ${params.precip})
print(f"Predicted ALT = {alt_pred:.2f} cm")`,
        exec_ru: (params) => `Predicted ALT = ${(params.c0 + params.c1 * params.DDT + params.c2 * params.DDF + params.c3 * params.snow + params.c4 * params.precip).toFixed(2)} cm
[Console] Модель OLS выдала прогноз с высоким коэффициентом детерминации R² = 0.86.`,
        exec_en: (params) => `Predicted ALT = ${(params.c0 + params.c1 * params.DDT + params.c2 * params.DDF + params.c3 * params.snow + params.c4 * params.precip).toFixed(2)} cm
[Console] OLS prediction computed. High calibration fit coefficient R² = 0.86.`
      },
      {
        type: "interactive_code",
        code: (params) => `# Анализ чувствительности модели регрессии к DDT и осадкам:\nc0, c1, c2, c3, c4 = ${params.c0.toFixed(2)}, ${params.c1.toFixed(4)}, ${params.c2.toFixed(4)}, ${params.c3.toFixed(3)}, ${params.c4.toFixed(4)}
DDT_val, DDF_val, snow_val, precip_val = ${params.DDT}, ${params.DDF}, ${params.snow}, ${params.precip}

# Зависимость ALT от осадков (от 50 до 300 мм)
precip_range = np.linspace(50, 300, 100)
alt_vs_precip = c0 + c1 * DDT_val + c2 * DDF_val + c3 * snow_val + c4 * precip_range

plt.figure(figsize=(8, 4))
plt.plot(precip_range, alt_vs_precip, '-', color='#a855f7', linewidth=2.5, label='Regression ALT vs Precip')
plt.scatter([precip_val], [${(params.c0 + params.c1 * params.DDT + params.c2 * params.DDF + params.c3 * params.snow + params.c4 * params.precip).toFixed(1)}], color='#fbbf24', s=80, label='Current Point')
plt.xlabel('Summer Precipitation (mm)')
plt.ylabel('ALT (cm)')
plt.legend()
plt.show()`,
        interactive_fields: [
          { name: "c0", label_ru: "Свободный член c0", label_en: "Intercept c0", min: 180, max: 220, step: 1.0 },
          { name: "c1", label_ru: "Коэффициент c1 (DDT)", label_en: "Coef c1 (DDT)", min: 0.005, max: 0.015, step: 0.0005 },
          { name: "c2", label_ru: "Коэффициент c2 (DDF)", label_en: "Coef c2 (DDF)", min: -0.01, max: -0.001, step: 0.0005 },
          { name: "c3", label_ru: "Коэффициент c3 (Снег)", label_en: "Coef c3 (Snow)", min: 0.1, max: 0.6, step: 0.02 },
          { name: "c4", label_ru: "Коэффициент c4 (Осадки)", label_en: "Coef c4 (Precip)", min: -0.01, max: 0.001, step: 0.0005 },
          { name: "DDT", label_ru: "Параметр DDT (°C-сут)", label_en: "DDT Parameter", min: 1800, max: 2500, step: 10 },
          { name: "DDF", label_ru: "Параметр DDF (°C-сут)", label_en: "DDF Parameter", min: 4200, max: 5400, step: 20 },
          { name: "snow", label_ru: "Снежный покров (см)", label_en: "Snow Cover (cm)", min: 10, max: 60, step: 1 },
          { name: "precip", label_ru: "Летние осадки (мм)", label_en: "Summer Precip (mm)", min: 50, max: 300, step: 5 }
        ],
        render_plot: (params) => {
          const precipRange = [];
          for (let p = 50; p <= 300; p += 5) {
            precipRange.push({ precip: p, alt: params.c0 + params.c1 * params.DDT + params.c2 * params.DDF + params.c3 * params.snow + params.c4 * p });
          }
          const currentAlt = params.c0 + params.c1 * params.DDT + params.c2 * params.DDF + params.c3 * params.snow + params.c4 * params.precip;
          return { precipRange, currentAlt, params };
        }
      }
    ]
  }
};

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [lang, setLang] = useState('ru');
  const [theme, setTheme] = useState('light');
  const [toastMessage, setToastMessage] = useState('');
  const [selectedYear, setSelectedYear] = useState(null);
  const [tourActive, setTourActive] = useState(false);
  const [tourStep, setTourStep] = useState(0);

  // Interactive Jupyter Notebook Simulator State
  const [activeNotebook, setActiveNotebook] = useState(null); // 'classic' | 'hybrid' | 'regression' | null
  const [cellStatus, setCellStatus] = useState({}); // { [cellIdx]: { running, executed, count, output } }
  const [nbParams, setNbParams] = useState({}); // Local sliders for the active notebook
  const [executionCount, setExecutionCount] = useState(1);

  const openNotebook = (type) => {
    setActiveNotebook(type);
    setCellStatus({});
    setExecutionCount(1);
    
    // Initialize parameters based on active system controls
    const initParams = {};
    if (type === 'classic') {
      initParams.E = 4.3448;
      initParams.DDT = modelDdt;
    } else if (type === 'hybrid') {
      initParams.E_base = 4.1866;
      initParams.beta = 0.00155;
      initParams.DDT = modelDdt;
      initParams.snow = modelSnow;
    } else if (type === 'regression') {
      initParams.c0 = 197.99;
      initParams.c1 = 0.0096;
      initParams.c2 = -0.0051;
      initParams.c3 = 0.370;
      initParams.c4 = -0.0045;
      initParams.DDT = modelDdt;
      initParams.DDF = modelDdf;
      initParams.snow = modelSnow;
      initParams.precip = modelPrecip;
    }
    setNbParams(initParams);
  };

  const handleNbParamChange = (name, value) => {
    setNbParams(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRunCell = (index) => {
    if (activeNotebook === null) return;
    
    setCellStatus(prev => ({
      ...prev,
      [index]: {
        ...prev[index],
        running: true,
        executed: false
      }
    }));
    
    setTimeout(() => {
      setExecutionCount(c => {
        const nextCount = c + 1;
        setCellStatus(prev => {
          const cell = notebookData[activeNotebook].cells[index];
          let outputText = "";
          
          if (cell.type === 'code' || cell.type === 'interactive_code') {
            const execHandler = lang === 'ru' ? (cell.exec_ru || cell.exec) : (cell.exec_en || cell.exec);
            if (typeof execHandler === 'function') {
              outputText = execHandler(nbParams);
            } else {
              outputText = execHandler || "";
            }
          }
          
          return {
            ...prev,
            [index]: {
              running: false,
              executed: true,
              count: c,
              output: outputText
            }
          };
        });
        return nextCount;
      });
    }, 600);
  };

  const handleRunAll = () => {
    if (activeNotebook === null) return;
    const cells = notebookData[activeNotebook].cells;
    
    cells.forEach((cell, index) => {
      if (cell.type === 'code' || cell.type === 'interactive_code') {
        setTimeout(() => {
          handleRunCell(index);
        }, index * 250);
      }
    });
  };

  const handleRestartKernel = () => {
    setCellStatus({});
    setExecutionCount(1);
    const toastMsg = lang === 'ru' ? "Ядро Python 3 успешно перезапущено." : "Python 3 kernel restarted successfully.";
    setToastMessage(toastMsg);
    setTimeout(() => setToastMessage(''), 3000);
  };

  const formatMarkdown = (text) => {
    if (!text) return "";
    let html = text;
    
    // Replace block math equations $$...$$ with a beautiful styled div
    html = html.replace(/\$\$(.*?)\$\$/gs, '<div class="nb-math-block">$1</div>');
    
    // Replace inline math $...$ with styled span
    html = html.replace(/\$(.*?)\$/g, '<span class="nb-math-inline">$1</span>');
    
    // Replace bold **...**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Replace headers ###
    html = html.replace(/### (.*?)\n/g, '<h3 class="nb-header-3">$1</h3>');
    
    // Bullet lists starting with *
    html = html.replace(/^\*\s(.*)$/gm, '<li class="nb-list-item">$1</li>');
    
    // New lines
    html = html.replace(/\n/g, '<br />');
    
    // Clean up empty lines or duplicate breaks around block elements
    html = html.replace(/<h3 class="nb-header-3">(.*?)<\/h3><br \/>/g, '<h3 class="nb-header-3">$1</h3>');
    html = html.replace(/<div class="nb-math-block">(.*?)<\/div><br \/>/g, '<div class="nb-math-block">$1</div>');
    
    // Convert LaTeX math symbols to unicode characters for premium browser rendering
    html = html.replace(/\\cdot/g, ' · ');
    html = html.replace(/\\approx/g, ' ≈ ');
    html = html.replace(/\\sqrt{(.*?)}/g, '√$1');
    html = html.replace(/\\beta/g, 'β');
    html = html.replace(/\\lambda/g, 'λ');
    html = html.replace(/\\rho/g, 'ρ');
    html = html.replace(/c_0/g, 'c₀');
    html = html.replace(/c_1/g, 'c₁');
    html = html.replace(/c_2/g, 'c₂');
    html = html.replace(/c_3/g, 'c₃');
    html = html.replace(/c_4/g, 'c₄');
    html = html.replace(/H_{snow}/g, 'H_snow');
    html = html.replace(/P_{summer}/g, 'P_summer');
    
    return html;
  };

  const renderCellPlot = (cell, params) => {
    if (!cell.render_plot) return null;
    const data = cell.render_plot(params);
    
    const w = 600;
    const h = 220;
    const px = 55;
    const py = 35;
    
    if (activeNotebook === 'classic') {
      const { ddtRange, currentAlt } = data;
      const alts = ddtRange.map(d => d.alt);
      const minAlt = Math.min(...alts) - 3;
      const maxAlt = Math.max(...alts) + 3;
      
      const getX = (ddt) => px + ((ddt - 1800) / 700) * (w - 2 * px);
      const getY = (alt) => h - py - ((alt - minAlt) / (maxAlt - minAlt)) * (h - 2 * py);
      
      let pathD = "";
      ddtRange.forEach((pt, idx) => {
        const x = getX(pt.ddt);
        const y = getY(pt.alt);
        if (idx === 0) pathD = `M ${x} ${y}`;
        else pathD += ` L ${x} ${y}`;
      });
      
      const curX = getX(params.DDT);
      const curY = getY(currentAlt);
      
      return (
        <svg width="100%" height={h} viewBox={`0 0 ${w} ${h}`} className="notebook-svg-plot">
          <g>
            <line x1={px} y1={h - py} x2={w - px} y2={h - py} stroke="var(--panel-border)" strokeWidth="1.5" />
            <line x1={px} y1={py} x2={px} y2={h - py} stroke="var(--panel-border)" strokeWidth="1.5" />
            
            <text x={px} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">1800</text>
            <text x={px + (w - 2*px)/2} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">2150</text>
            <text x={w - px} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">2500</text>
            
            <text x={px - 8} y={h - py} fill="var(--text-muted)" fontSize="9" textAnchor="end">{minAlt.toFixed(0)}</text>
            <text x={px - 8} y={py} fill="var(--text-muted)" fontSize="9" textAnchor="end">{maxAlt.toFixed(0)}</text>
          </g>
          
          <text x={w / 2} y={h - 3} fill="var(--text-secondary)" fontSize="10" fontWeight="700" textAnchor="middle">
            {lang === 'ru' ? 'Градусо-сутки таяния DDT (°C-сут)' : 'Thawing Degree Days DDT (°C-days)'}
          </text>
          <text x={12} y={h / 2} fill="var(--text-secondary)" fontSize="10" fontWeight="700" textAnchor="middle" transform={`rotate(-90, 12, ${h/2})`}>
            ALT (cm)
          </text>
          
          <path d={pathD} fill="none" stroke="#ef4444" strokeWidth="2.5" />
          
          <circle cx={getX(2150)} cy={getY(201.5)} r="4" fill="#22d3ee" />
          <text x={getX(2150) + 6} y={getY(201.5) - 4} fill="#22d3ee" fontSize="9" fontWeight="700">
            {lang === 'ru' ? 'Якутск (201.5 см)' : 'Yakutsk (201.5 cm)'}
          </text>
          
          <circle cx={curX} cy={curY} r="6" fill="var(--accent)" stroke="#fff" strokeWidth="1.5" />
          <text x={curX + 8} y={curY - 6} fill="var(--accent)" fontSize="9" fontWeight="800">
            {lang === 'ru' ? `${currentAlt.toFixed(1)} см` : `${currentAlt.toFixed(1)} cm`}
          </text>
        </svg>
      );
    } else if (activeNotebook === 'hybrid') {
      const { snowRange, currentAlt } = data;
      const alts = snowRange.map(s => s.alt);
      const minAlt = Math.min(...alts) - 3;
      const maxAlt = Math.max(...alts) + 3;
      
      const getX = (snow) => px + ((snow - 10) / 50) * (w - 2 * px);
      const getY = (alt) => h - py - ((alt - minAlt) / (maxAlt - minAlt)) * (h - 2 * py);
      
      let pathD = "";
      snowRange.forEach((pt, idx) => {
        const x = getX(pt.snow);
        const y = getY(pt.alt);
        if (idx === 0) pathD = `M ${x} ${y}`;
        else pathD += ` L ${x} ${y}`;
      });
      
      const curX = getX(params.snow);
      const curY = getY(currentAlt);
      
      return (
        <svg width="100%" height={h} viewBox={`0 0 ${w} ${h}`} className="notebook-svg-plot">
          <g>
            <line x1={px} y1={h - py} x2={w - px} y2={h - py} stroke="var(--panel-border)" strokeWidth="1.5" />
            <line x1={px} y1={py} x2={px} y2={h - py} stroke="var(--panel-border)" strokeWidth="1.5" />
            
            <text x={px} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">10</text>
            <text x={px + (w - 2*px)/2} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">35</text>
            <text x={w - px} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">60</text>
            
            <text x={px - 8} y={h - py} fill="var(--text-muted)" fontSize="9" textAnchor="end">{minAlt.toFixed(0)}</text>
            <text x={px - 8} y={py} fill="var(--text-muted)" fontSize="9" textAnchor="end">{maxAlt.toFixed(0)}</text>
          </g>
          
          <text x={w / 2} y={h - 3} fill="var(--text-secondary)" fontSize="10" fontWeight="700" textAnchor="middle">
            {lang === 'ru' ? 'Высота снежного покрова (см)' : 'Winter Snow Depth (cm)'}
          </text>
          <text x={12} y={h / 2} fill="var(--text-secondary)" fontSize="10" fontWeight="700" textAnchor="middle" transform={`rotate(-90, 12, ${h/2})`}>
            ALT (cm)
          </text>
          
          <path d={pathD} fill="none" stroke="#22d3ee" strokeWidth="2.5" />
          
          <circle cx={curX} cy={curY} r="6" fill="var(--accent)" stroke="#fff" strokeWidth="1.5" />
          <text x={curX + 8} y={curY - 6} fill="var(--accent)" fontSize="9" fontWeight="800">
            {lang === 'ru' ? `${currentAlt.toFixed(1)} см` : `${currentAlt.toFixed(1)} cm`}
          </text>
        </svg>
      );
    } else if (activeNotebook === 'regression') {
      const { precipRange, currentAlt } = data;
      const alts = precipRange.map(p => p.alt);
      const minAlt = Math.min(...alts) - 3;
      const maxAlt = Math.max(...alts) + 3;
      
      const getX = (precip) => px + ((precip - 50) / 250) * (w - 2 * px);
      const getY = (alt) => h - py - ((alt - minAlt) / (maxAlt - minAlt)) * (h - 2 * py);
      
      let pathD = "";
      precipRange.forEach((pt, idx) => {
        const x = getX(pt.precip);
        const y = getY(pt.alt);
        if (idx === 0) pathD = `M ${x} ${y}`;
        else pathD += ` L ${x} ${y}`;
      });
      
      const curX = getX(params.precip);
      const curY = getY(currentAlt);
      
      return (
        <svg width="100%" height={h} viewBox={`0 0 ${w} ${h}`} className="notebook-svg-plot">
          <g>
            <line x1={px} y1={h - py} x2={w - px} y2={h - py} stroke="var(--panel-border)" strokeWidth="1.5" />
            <line x1={px} y1={py} x2={px} y2={h - py} stroke="var(--panel-border)" strokeWidth="1.5" />
            
            <text x={px} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">50</text>
            <text x={px + (w - 2*px)/2} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">175</text>
            <text x={w - px} y={h - 15} fill="var(--text-muted)" fontSize="9" textAnchor="middle">300</text>
            
            <text x={px - 8} y={h - py} fill="var(--text-muted)" fontSize="9" textAnchor="end">{minAlt.toFixed(0)}</text>
            <text x={px - 8} y={py} fill="var(--text-muted)" fontSize="9" textAnchor="end">{maxAlt.toFixed(0)}</text>
          </g>
          
          <text x={w / 2} y={h - 3} fill="var(--text-secondary)" fontSize="10" fontWeight="700" textAnchor="middle">
            {lang === 'ru' ? 'Летние осадки (мм)' : 'Summer Precipitation (mm)'}
          </text>
          <text x={12} y={h / 2} fill="var(--text-secondary)" fontSize="10" fontWeight="700" textAnchor="middle" transform={`rotate(-90, 12, ${h/2})`}>
            ALT (cm)
          </text>
          
          <path d={pathD} fill="none" stroke="#a855f7" strokeWidth="2.5" />
          
          <circle cx={curX} cy={curY} r="6" fill="#fbbf24" stroke="#fff" strokeWidth="1.5" />
          <text x={curX + 8} y={curY - 6} fill="#fbbf24" fontSize="9" fontWeight="800">
            {lang === 'ru' ? `${currentAlt.toFixed(1)} см` : `${currentAlt.toFixed(1)} cm`}
          </text>
        </svg>
      );
    }
    return null;
  };

  // Simulation State Variables (initialized to standard historical baselines)
  const [dssAlt, setDssAlt] = useState(206);
  const [dssT320, setDssT320] = useState(-0.35);
  const [dssSnow, setDssSnow] = useState(38);
  const [dssRos, setDssRos] = useState(1);

  const [modelDdt, setModelDdt] = useState(2150);
  const [modelDdf, setModelDdf] = useState(4800);
  const [modelSnow, setModelSnow] = useState(38);
  const [modelPrecip, setModelPrecip] = useState(150);

  const [riverLensk, setRiverLensk] = useState(950);
  const [riverOlek, setRiverOlek] = useState(850);

  const [soilYear, setSoilYear] = useState(2035);

  // Initialize mathematical modules
  const dssSystem = new DecisionSupportSystem();
  const stefanClassic = new StefanClassicModel();
  const stefanHybrid = new StefanHybridModel();
  const regressionModel = new EmpiricalRegressionModel();
  const thermalModel = new SoilThermalTrendModel();
  const hydroModel = new HydroPropagationModel();

  // Run evaluations
  const dssOutput = dssSystem.evaluateYear(dssAlt, dssT320, dssSnow, dssRos);
  
  const altClassicVal = stefanClassic.predict(modelDdt);
  const altHybridVal = stefanHybrid.predict(modelDdt, modelSnow);
  const altRegressVal = regressionModel.predict(modelDdt, modelDdf, modelSnow, modelPrecip);

  const riverPredictedLevel = hydroModel.predictPeakLevel(riverLensk, riverOlek);
  const riverWarning = hydroModel.evaluateWarning(riverPredictedLevel);

  const projectedSoilTemp = thermalModel.predict(soilYear);
  const soilFailureYear = Math.round(thermalModel.getFailureYear());
  const yearsUntilFailure = soilFailureYear - new Date().getFullYear();

  // Load a historical year's exact data into all simulators
  const loadHistoricalYear = (yearObj) => {
    setSelectedYear(yearObj.year);
    
    // Load into DSS
    setDssAlt(yearObj.alt_measured || Math.round(regressionModel.predict(yearObj.ddt, yearObj.ddf, yearObj.h_snow, yearObj.precip_summer)));
    if (yearObj.t320 !== null) setDssT320(Number(yearObj.t320.toFixed(2)));
    setDssSnow(yearObj.h_snow);
    setDssRos(yearObj.ros);

    // Load into ALT models
    setModelDdt(yearObj.ddt);
    setModelDdf(yearObj.ddf);
    setModelSnow(yearObj.h_snow);
    setModelPrecip(yearObj.precip_summer);

    // Load into flood model
    setRiverLensk(yearObj.lensk_peak);
    setRiverOlek(yearObj.olek_peak);

    // Show temporary toast message
    const msg = t[lang].archiveLoadMsg.replace('{year}', yearObj.year);
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 4000);
  };

  // Toggle theme class on body
  useEffect(() => {
    const bodyClass = document.body.classList;
    if (theme === 'light') {
      bodyClass.add('light-theme');
    } else {
      bodyClass.remove('light-theme');
    }
  }, [theme]);

  // Handle automatic tab switching during the interactive tour
  useEffect(() => {
    if (tourActive) {
      const tourTabs = ['overview', 'dss', 'alt_models', 'river', 'archive', 'soil_thermal'];
      setActiveTab(tourTabs[tourStep]);
    }
  }, [tourActive, tourStep]);

  // Disable main body scroll when Jupyter notebook modal is active
  useEffect(() => {
    if (activeNotebook) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [activeNotebook]);

  // Translate helper
  const translate = (key) => {
    return t[lang][key] || key;
  };

  // SVG Chart Dimensions & Programmatic coordinates
  const chartW = 850;
  const chartH = 260;
  const paddingX = 60;
  const paddingY = 30;

  // Scale calculations for DDT and ALT
  const minYear = 2005;
  const maxYear = 2024;
  const ddtMin = 1950;
  const ddtMax = 2400;
  const altMin = 190;
  const altMax = 225;

  const getChartCoords = (item) => {
    const x = paddingX + ((item.year - minYear) / (maxYear - minYear)) * (chartW - 2 * paddingX);
    const yDdt = chartH - paddingY - ((item.ddt - ddtMin) / (ddtMax - ddtMin)) * (chartH - 2 * paddingY);
    
    // Handle alt (if null, predict it)
    const activeAlt = item.alt_measured || regressionModel.predict(item.ddt, item.ddf, item.h_snow, item.precip_summer);
    const yAlt = chartH - paddingY - ((activeAlt - altMin) / (altMax - altMin)) * (chartH - 2 * paddingY);
    
    return { x, yDdt, yAlt };
  };

  // Generate SVG path string
  let ddtPath = '';
  let altPath = '';
  historicalData.forEach((item, index) => {
    const { x, yDdt, yAlt } = getChartCoords(item);
    if (index === 0) {
      ddtPath = `M ${x} ${yDdt}`;
      altPath = `M ${x} ${yAlt}`;
    } else {
      ddtPath += ` L ${x} ${yDdt}`;
      altPath += ` L ${x} ${yAlt}`;
    }
  });

  return (
    <div className="app-container">
      {/* 📂 Side Navigation Bar */}
      <aside className="sidebar">
        <div className="brand-section">
          <ShieldAlert className="brand-icon" size={32} />
          <div>
            <div className="brand-title">{translate('brandName')}</div>
            <div className="brand-subtitle">{translate('brandDesc')}</div>
          </div>
        </div>

        <nav className="nav-menu">
          <button
            className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <Activity className="nav-icon" />
            <span>{translate('tabOverview')}</span>
          </button>
          
          <button
            className={`nav-item ${activeTab === 'dss' ? 'active' : ''}`}
            onClick={() => setActiveTab('dss')}
          >
            <ShieldAlert className="nav-icon" />
            <span>{translate('tabDss')}</span>
          </button>

          <button
            className={`nav-item ${activeTab === 'alt_models' ? 'active' : ''}`}
            onClick={() => setActiveTab('alt_models')}
          >
            <Thermometer className="nav-icon" />
            <span>{translate('tabAlt')}</span>
          </button>

          <button
            className={`nav-item ${activeTab === 'river' ? 'active' : ''}`}
            onClick={() => setActiveTab('river')}
          >
            <Droplets className="nav-icon" />
            <span>{translate('tabRiver')}</span>
          </button>

          <button
            className={`nav-item ${activeTab === 'archive' ? 'active' : ''}`}
            onClick={() => setActiveTab('archive')}
          >
            <Database className="nav-icon" />
            <span>{translate('tabArchive')}</span>
          </button>

          <button
            className={`nav-item ${activeTab === 'soil_thermal' ? 'active' : ''}`}
            onClick={() => setActiveTab('soil_thermal')}
          >
            <TrendingUp className="nav-icon" />
            <span>{translate('tabSoil')}</span>
          </button>

          <button
            className={`nav-item ${activeTab === 'guide' ? 'active' : ''}`}
            onClick={() => setActiveTab('guide')}
            style={{ borderTop: '2px solid var(--panel-border)', marginTop: '8px', paddingTop: '14px' }}
          >
            <HelpCircle className="nav-icon" style={{ color: 'var(--accent-secondary)' }} />
            <span style={{ color: 'var(--accent-secondary)', fontWeight: '800' }}>{translate('tabGuide')}</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--mono)' }}>
            {translate('authorName')}
          </div>
        </div>
      </aside>

      {/* 💻 Main Workspace Area */}
      <main className="main-content">
        <header className="top-bar">
          <div className="top-bar-title">
            <h1>{translate('brandName')} — {translate('brandDesc')}</h1>
          </div>

          <div className="controls-group">
            {/* Language Switcher */}
            <button
              className="btn-round btn-lang"
              onClick={() => setLang(lang === 'ru' ? 'en' : 'ru')}
              title="Переключить язык / Switch Language"
            >
              <Globe size={16} />
              <span>{translate('langToggle')}</span>
            </button>

            {/* Theme Toggle */}
            <button
              className="btn-round"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              title="Переключить тему / Toggle Theme"
            >
              {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              <span>{theme === 'dark' ? translate('themeToggleLight') : translate('themeToggleDark')}</span>
            </button>
          </div>
        </header>

        {/* Global Warning Banner */}
        <div className="alert-strip">
          <AlertTriangle className="alert-strip-icon" size={20} />
          <div className="alert-strip-text">{translate('alertBanner')}</div>
        </div>

        {/* Toast loaded database alert */}
        {toastMessage && (
          <div 
            className="animate-fade-in" 
            style={{
              position: 'fixed',
              top: '85px',
              right: '30px',
              background: 'var(--accent-secondary)',
              color: '#070913',
              padding: '12px 24px',
              borderRadius: 'var(--radius-md)',
              fontWeight: '700',
              zIndex: 100,
              boxShadow: 'var(--shadow-glow-cyan)',
              fontFamily: 'var(--sans)',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}
          >
            <CheckCircle size={18} />
            <span>{toastMessage}</span>
          </div>
        )}

        <div className="view-container animate-fade-in">
          
          {/* TAB 1: OVERVIEW & MONITORING */}
          {activeTab === 'overview' && (
            <>
              <div className="view-header">
                <h2>{translate('overviewTitle')}</h2>
                <p>{translate('overviewDesc')}</p>
              </div>

              {/* KPI metrics row */}
              <div className="kpi-grid">
                <div className="kpi-card cyan">
                  <div className="kpi-label">{translate('kpiAvgAlt')}</div>
                  <div className="kpi-value">203.2 см</div>
                  <div className="kpi-desc">{translate('kpiAvgAltDesc')}</div>
                </div>

                <div className="kpi-card red">
                  <div className="kpi-label">{translate('kpiMaxTemp')}</div>
                  <div className="kpi-value">0.387 °С</div>
                  <div className="kpi-desc">{translate('kpiMaxTempDesc')}</div>
                </div>

                <div className="kpi-card cyan">
                  <div className="kpi-label">{translate('kpiMaxFlood')}</div>
                  <div className="kpi-value">1353 см</div>
                  <div className="kpi-desc">{translate('kpiMaxFloodDesc')}</div>
                </div>

                <div className="kpi-card green">
                  <div className="kpi-label">{translate('kpiRiskYear')}</div>
                  <div className="kpi-value">9 / 20 лет</div>
                  <div className="kpi-desc">{translate('kpiRiskYearDesc')}</div>
                </div>
              </div>

              {/* Description and visual introduction */}
              <div className="overview-intro-grid">
                <div className="glass-panel">
                  <h3 className="panel-title">
                    <Info size={18} style={{ color: 'var(--accent-primary)' }} />
                    {translate('introTitle')}
                  </h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', textAlign: 'left', fontSize: '15px', color: 'var(--text-secondary)' }}>
                    <p>{translate('introText1')}</p>
                    <p>{translate('introText2')}</p>
                    <ul className="bullet-list">
                      <li>
                        <span className="bullet-marker">✓</span>
                        <span>{translate('introBullet1')}</span>
                      </li>
                      <li>
                        <span className="bullet-marker">✓</span>
                        <span>{translate('introBullet2')}</span>
                      </li>
                      <li>
                        <span className="bullet-marker">✓</span>
                        <span>{translate('introBullet3')}</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <h3 className="panel-title">
                    <Activity size={18} style={{ color: 'var(--accent-secondary)' }} />
                    {lang === 'ru' ? "Схема мониторинга" : "Monitoring Concept"}
                  </h3>
                  
                  {/* Conceptual animated permafrost SVG */}
                  <div className="soil-diagram-container">
                    <svg viewBox="0 0 200 180" className="soil-svg" style={{ maxHeight: '220px' }}>
                      <defs>
                        <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#0a0f1d" />
                          <stop offset="100%" stopColor="#1e1b4b" />
                        </linearGradient>
                        <linearGradient id="soilGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#78350f" />
                          <stop offset="100%" stopColor="#451a03" />
                        </linearGradient>
                        <linearGradient id="permaGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#1e3a8a" />
                          <stop offset="100%" stopColor="#172554" />
                        </linearGradient>
                      </defs>

                      {/* Sky / Air */}
                      <rect x="0" y="0" width="200" height="40" fill="url(#skyGrad)" rx="4" />
                      <text x="10" y="18" fill="#a5f3fc" fontSize="8" fontWeight="bold">атмосфера / air</text>
                      
                      {/* Sun ray animation */}
                      <circle cx="170" cy="18" r="6" fill="#fbbf24" filter="drop-shadow(0 0 4px #f59e0b)" />
                      <line x1="170" y1="18" x2="170" y2="35" stroke="#fbbf24" strokeWidth="1" strokeDasharray="2 2" />
                      <line x1="170" y1="18" x2="155" y2="28" stroke="#fbbf24" strokeWidth="1" strokeDasharray="2 2" />

                      {/* Ground Thaw Active Layer */}
                      <rect x="0" y="40" width="200" height="45" fill="url(#soilGrad)" />
                      <path d="M 0 40 Q 50 42 100 40 T 200 40 L 200 85 L 0 85 Z" fill="#b45309" opacity="0.3" />
                      <text x="10" y="55" fill="#fef08a" fontSize="7" fontWeight="600">слой протаивания / active layer</text>
                      <text x="10" y="65" fill="#f59e0b" fontSize="6">оттайка (ALT) ~ 203 см</text>

                      {/* Permafrost Layer */}
                      <rect x="0" y="85" width="200" height="95" fill="url(#permaGrad)" rx="4" />
                      <text x="10" y="105" fill="#93c5fd" fontSize="8" fontWeight="bold">вечная мерзлота / permafrost</text>
                      <text x="10" y="115" fill="#60a5fa" fontSize="6">стабильная толща t &lt; 0°C</text>

                      {/* Conceptual Pile Foundation */}
                      <rect x="100" y="25" width="10" height="100" fill="#94a3b8" stroke="#cbd5e1" strokeWidth="1" />
                      <line x1="100" y1="40" x2="110" y2="40" stroke="#ef4444" strokeWidth="1.5" />
                      <line x1="100" y1="85" x2="110" y2="85" stroke="#3b82f6" strokeWidth="1.5" />

                      {/* Building Mockup */}
                      <rect x="85" y="5" width="40" height="20" fill="#334155" rx="2" stroke="#475569" />
                      <rect x="92" y="10" width="6" height="6" fill="#fef08a" opacity="0.8" />
                      <rect x="108" y="10" width="6" height="6" fill="#fef08a" opacity="0.8" />
                    </svg>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB 2: OPERATIONAL DSS (PSRS SCALE) */}
          {activeTab === 'dss' && (
            <>
              <div className="view-header">
                <h2>{translate('dssTitle')}</h2>
                <p>{translate('dssDesc')}</p>
              </div>

              <div className="split-layout">
                {/* Sliders Input Panel */}
                <div className="glass-panel form-group">
                  <h3 className="panel-title">
                    <Settings size={18} style={{ color: 'var(--accent-primary)' }} />
                    {translate('dssSliders')}
                  </h3>

                  {/* Slider ALT */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('sliderAlt')}</span>
                      <span className="slider-value">{dssAlt} см</span>
                    </div>
                    <input
                      type="range"
                      min="180"
                      max="240"
                      value={dssAlt}
                      onChange={(e) => {setDssAlt(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control"
                      style={{ '--val-pct': `${((dssAlt - 180) / (240 - 180)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>180 см</span>
                      <span>240 см</span>
                    </div>
                  </div>

                  {/* Slider T320 */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('sliderT320')}</span>
                      <span className="slider-value">{dssT320} °С</span>
                    </div>
                    <input
                      type="range"
                      min="-1.5"
                      max="0.5"
                      step="0.05"
                      value={dssT320}
                      onChange={(e) => {setDssT320(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control cyan"
                      style={{ '--val-pct': `${((dssT320 - (-1.5)) / (0.5 - (-1.5))) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>-1.5 °С</span>
                      <span>+0.5 °С</span>
                    </div>
                  </div>

                  {/* Slider Snow Depth */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('sliderSnow')}</span>
                      <span className="slider-value">{dssSnow} см</span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max="60"
                      value={dssSnow}
                      onChange={(e) => {setDssSnow(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control"
                      style={{ '--val-pct': `${((dssSnow - 10) / (60 - 10)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>10 см</span>
                      <span>60 см</span>
                    </div>
                  </div>

                  {/* Slider ROS Days */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('sliderRos')}</span>
                      <span className="slider-value">{dssRos} дней</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="5"
                      value={dssRos}
                      onChange={(e) => {setDssRos(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control cyan"
                      style={{ '--val-pct': `${((dssRos - 0) / (5 - 0)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>0 дней</span>
                      <span>5 дней</span>
                    </div>
                  </div>

                  {selectedYear && (
                    <div style={{ fontSize: '12px', color: 'var(--accent-secondary)', fontFamily: 'var(--mono)', textAlign: 'right' }}>
                      * {lang === 'ru' ? `Синхронизировано с ${selectedYear} годом` : `Synced with year ${selectedYear}`}
                    </div>
                  )}
                </div>

                {/* DSS Evaluation Output Panel */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <h3 className="panel-title">
                    <ShieldAlert size={18} style={{ color: 'var(--accent-secondary)' }} />
                    {lang === 'ru' ? "Анализ рисков и регламенты МЧС" : "EMERCOM Risk Assessment"}
                  </h3>

                  {/* Dynamic Gauge indicators */}
                  <div className={`dss-card ${dssOutput.color.toLowerCase()}`}>
                    
                    <div className="gauge-svg-container">
                      <svg width="180" height="180" viewBox="0 0 180 180">
                        {/* Semi-circular track */}
                        <path 
                          d="M 30 140 A 65 65 0 1 1 150 140" 
                          className="gauge-background" 
                        />
                        {/* Dynamic stroke filled length */}
                        <path 
                          d="M 30 140 A 65 65 0 1 1 150 140" 
                          className={`gauge-fill ${dssOutput.color.toLowerCase()}`}
                          strokeDasharray="300"
                          // score maps from 0 to 10 to dashoffset from 300 to 0 (approx 260 deg arc)
                          strokeDashoffset={300 - (dssOutput.score / 10) * 260}
                        />
                      </svg>
                      <div className="gauge-text">
                        <span className="gauge-score">{dssOutput.score}</span>
                        <span className="gauge-max">max 10.0</span>
                      </div>
                    </div>

                    <div className="risk-badge-row">
                      <span className={`risk-badge ${dssOutput.color.toLowerCase()}`}>
                        {translate('dssLevel')}: {dssOutput.level === 'LOW' ? translate('dssLow') : dssOutput.level === 'MODERATE' ? translate('dssMod') : translate('dssExt')}
                      </span>
                    </div>
                  </div>

                  {/* Operational recommendations */}
                  <div className="recommendations-title">
                    <CheckCircle size={16} />
                    {translate('dssRecs')}
                  </div>

                  <div className="checklist">
                    {(lang === 'ru' ? dssOutput.recommendations_ru : dssOutput.recommendations_en).map((rec, i) => (
                      <div key={i} className="checklist-item">
                        <AlertTriangle className={`checklist-icon ${dssOutput.color.toLowerCase()}`} size={16} />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Section 3: Live SVG ground thawing layers inside DSS */}
              <div className="glass-panel">
                <h3 className="panel-title">
                  <Activity size={18} style={{ color: 'var(--accent-secondary)' }} />
                  {translate('dssDiagram')}
                </h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', alignItems: 'center' }}>
                  <div className="soil-diagram-container" style={{ padding: '24px' }}>
                    <svg viewBox="0 0 350 200" className="soil-svg" style={{ maxWidth: '100%' }}>
                      <defs>
                        <linearGradient id="groundGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#78350f" />
                          <stop offset="100%" stopColor="#451a03" />
                        </linearGradient>
                        <linearGradient id="permaGrad2" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#1e3a8a" />
                          <stop offset="100%" stopColor="#172554" />
                        </linearGradient>
                      </defs>

                      {/* Surface ground grass */}
                      <rect x="0" y="38" width="350" height="4" fill="#15803d" />
                      
                      {/* Thawed Layer (dynamically adjusts height based on slider dssAlt) */}
                      {/* dssAlt maps from 180 to 240, scale it to height 35 to 80 px */}
                      <rect 
                        x="0" 
                        y="42" 
                        width="350" 
                        height={40 + ((dssAlt - 180) / (240 - 180)) * 40} 
                        fill="url(#groundGrad)" 
                        style={{ transition: 'height 0.4s' }}
                      />
                      
                      {/* Measured text layer overlay */}
                      <text x="10" y="55" className="soil-label-text" fill="#fef08a">
                        {translate('diagramActive')} {dssAlt} см
                      </text>

                      {/* Permafrost Layer */}
                      <rect 
                        x="0" 
                        y={42 + 40 + ((dssAlt - 180) / (240 - 180)) * 40} 
                        width="350" 
                        height={200 - (42 + 40 + ((dssAlt - 180) / (240 - 180)) * 40)} 
                        fill="url(#permaGrad2)" 
                        style={{ transition: 'y 0.4s, height 0.4s' }}
                      />
                      
                      <text 
                        x="10" 
                        y={42 + 40 + ((dssAlt - 180) / (240 - 180)) * 40 + 20} 
                        className="soil-label-text" 
                        fill="#93c5fd"
                        style={{ transition: 'y 0.4s' }}
                      >
                        {translate('diagramFrozen')} (T грунта: {dssT320}°C)
                      </text>

                      {/* Concrete Pile */}
                      {/* If ALT is high (e.g. >215), the pile starts showing red stress arrows because stable anchorage is reduced! */}
                      <g transform="translate(180, 10)">
                        {/* Pile body: styled with premium contrast and active hover transitions */}
                        <rect 
                          x="-10" 
                          y="10" 
                          width="20" 
                          height="130" 
                          fill="#94a3b8" 
                          stroke={dssAlt > 215 ? "#ef4444" : "#475569"} 
                          strokeWidth="2" 
                          style={{ transition: 'stroke 0.4s, fill 0.4s' }}
                        />
                        
                        {/* Anchor marks in stable permafrost: highly visible and contrasty neon green anchor lines */}
                        <line x1="-16" y1="115" x2="16" y2="115" stroke="#10b981" strokeWidth="3" />
                        <line x1="-16" y1="128" x2="16" y2="128" stroke="#10b981" strokeWidth="3" />
                        
                        {/* If thawed height is deep (pile penetration into stable frost is < 50px) */}
                        {dssAlt > 215 ? (
                          <>
                            {/* Critical strain animation: thicker bold neon red warning vectors */}
                            <path 
                              d="M-28,60 L-14,64 M-28,80 L-14,84 M28,60 L14,64 M28,80 L14,84" 
                              stroke="#ef4444" 
                              strokeWidth="3" 
                              strokeLinecap="round"
                            />
                            <text 
                              x="-90" 
                              y="52" 
                              fill="#fca5a5" 
                              fontSize="10" 
                              fontWeight="900" 
                              className="animate-pulse-glow"
                              style={{ textShadow: '0px 1px 3px rgba(0, 0, 0, 0.95)' }}
                            >
                              {lang === 'ru' ? "Сдвиговые напряжения!" : "Shear Stresses!"}
                            </text>
                          </>
                        ) : null}
                      </g>

                      {/* Foundation slab / building: perfectly centered, wider, and contrasty */}
                      {dssAlt > 215 ? (
                        /* Alarm/deformed state: red glowing container */
                        <g>
                          <rect 
                            x="105" 
                            y="4" 
                            width="150" 
                            height="18" 
                            fill="#450a0a" 
                            rx="3" 
                            stroke="#ef4444" 
                            strokeWidth="2.5"
                            style={{ filter: 'drop-shadow(0 0 4px rgba(239, 68, 68, 0.5))', transition: 'all 0.4s' }}
                          />
                          <text 
                            x="180" 
                            y="16.5" 
                            textAnchor="middle" 
                            fill="#fecaca" 
                            fontSize="8" 
                            fontWeight="900"
                            style={{ letterSpacing: '0.3px', transition: 'all 0.4s', textShadow: '0px 1px 1px rgba(0, 0, 0, 0.8)' }}
                          >
                            {lang === 'ru' ? "СВАЯ ДЕФОРМИРОВАНА" : "PILE DEFORMED"}
                          </text>
                        </g>
                      ) : (
                        /* Stable state: premium slate/cyan container */
                        <g>
                          <rect 
                            x="105" 
                            y="4" 
                            width="150" 
                            height="18" 
                            fill="#1e293b" 
                            rx="3" 
                            stroke="#10b981" 
                            strokeWidth="2"
                            style={{ transition: 'all 0.4s' }}
                          />
                          <text 
                            x="180" 
                            y="16.5" 
                            textAnchor="middle" 
                            fill="#34d399" 
                            fontSize="8" 
                            fontWeight="800"
                            style={{ letterSpacing: '0.3px', transition: 'all 0.4s', textShadow: '0px 1px 1px rgba(0, 0, 0, 0.8)' }}
                          >
                            {lang === 'ru' ? "ФУНДАМЕНТ СТАБИЛЕН" : "FOUNDATION STABLE"}
                          </text>
                        </g>
                      )}
                    </svg>
                  </div>

                  <div style={{ textAlign: 'left' }}>
                    <h4 style={{ color: 'var(--text-primary)', margin: '0 0 10px' }}>
                      {lang === 'ru' ? "Геотехнический анализ модели свайного основания" : "Geotechnical Foundation Analysis"}
                    </h4>
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {lang === 'ru' ? (
                        <>
                          Железобетонные сваи в Якутске заглубляются в вечную мерзлоту и опираются на силы смерзания. При возрастании <strong>активного слоя (ALT) &gt; 215 см</strong> и потеплении грунта свыше <strong>-0.4 °С</strong> сцепление резко ослабевает. 
                          <br /><br />
                          Наша математическая модель фиксирует эти сдвиги. В симуляторе Вы можете наглядно увидеть, как увеличение талого слоя обнажает сваю, подвергая фундамент риску выпучивания и деформации.
                        </>
                      ) : (
                        <>
                          Standard reinforced concrete piles in Yakutsk rely on permafrost adhesion. When <strong>ALT grows &gt; 215 cm</strong> and soil warms above <strong>-0.4 °C</strong>, vertical load-bearing friction drops.
                          <br /><br />
                          The simulator models this shear stress: as the thawed soil expands, the pile loses stable anchoring, raising the building collapse warning.
                        </>
                      )}
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB 3: ALT PREDICTIVE MODELS */}
          {activeTab === 'alt_models' && (
            <>
              <div className="view-header">
                <h2>{translate('altTitle')}</h2>
                <p>{translate('altDesc')}</p>
              </div>

              <div className="split-layout">
                {/* Predictors configuration */}
                <div className="glass-panel form-group">
                  <h3 className="panel-title">
                    <Settings size={18} style={{ color: 'var(--accent-primary)' }} />
                    {translate('altParams')}
                  </h3>

                  {/* DDT Slider */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('altDdt')}</span>
                      <span className="slider-value">{modelDdt} °C·сут</span>
                    </div>
                    <input
                      type="range"
                      min="1950"
                      max="2400"
                      value={modelDdt}
                      onChange={(e) => {setModelDdt(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control"
                      style={{ '--val-pct': `${((modelDdt - 1950) / (2400 - 1950)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>1950</span>
                      <span>2400</span>
                    </div>
                  </div>

                  {/* DDF Slider */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('altDdf')}</span>
                      <span className="slider-value">{modelDdf} °C·сут</span>
                    </div>
                    <input
                      type="range"
                      min="4200"
                      max="5400"
                      value={modelDdf}
                      onChange={(e) => {setModelDdf(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control cyan"
                      style={{ '--val-pct': `${((modelDdf - 4200) / (5400 - 4200)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>4200</span>
                      <span>5400</span>
                    </div>
                  </div>

                  {/* Snow Depth Slider */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('sliderSnow')}</span>
                      <span className="slider-value">{modelSnow} см</span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max="60"
                      value={modelSnow}
                      onChange={(e) => {setModelSnow(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control"
                      style={{ '--val-pct': `${((modelSnow - 10) / (60 - 10)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>10 см</span>
                      <span>60 см</span>
                    </div>
                  </div>

                  {/* Summer Precipitation Slider */}
                  <div className="slider-container">
                    <div className="slider-header">
                      <span className="slider-label">{translate('altPrecip')}</span>
                      <span className="slider-value">{modelPrecip} мм</span>
                    </div>
                    <input
                      type="range"
                      min="50"
                      max="300"
                      value={modelPrecip}
                      onChange={(e) => {setModelPrecip(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control cyan"
                      style={{ '--val-pct': `${((modelPrecip - 50) / (300 - 50)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>50 мм</span>
                      <span>300 мм</span>
                    </div>
                  </div>
                </div>

                {/* Model outputs comparison */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <h3 className="panel-title">
                    <Thermometer size={18} style={{ color: 'var(--accent-secondary)' }} />
                    {translate('altModelComp')}
                  </h3>

                  <div className="comparison-grid">
                    {/* Classical Stefan */}
                    <div className="comparison-card">
                      <button 
                        className="comparison-model-link"
                        onClick={() => openNotebook('classic')}
                        title={lang === 'ru' ? "Открыть Jupyter-ноутбук" : "Open Jupyter Notebook"}
                      >
                        <span>{translate('stefanClassic')}</span>
                        <BookOpen size={14} className="notebook-link-icon" />
                      </button>
                      <div className="comparison-model-val">{altClassicVal.toFixed(1)} см</div>
                      <div className="comparison-model-diff" style={{ color: 'var(--text-muted)' }}>
                        Stefan Physics
                      </div>
                    </div>

                    {/* Hybrid Stefan */}
                    <div className="comparison-card">
                      <button 
                        className="comparison-model-link"
                        onClick={() => openNotebook('hybrid')}
                        title={lang === 'ru' ? "Открыть Jupyter-ноутбук" : "Open Jupyter Notebook"}
                      >
                        <span>{translate('stefanHybrid')}</span>
                        <BookOpen size={14} className="notebook-link-icon" />
                      </button>
                      <div className="comparison-model-val">{altHybridVal.toFixed(1)} см</div>
                      <div className="comparison-model-diff" style={{ color: 'var(--accent-secondary)' }}>
                        Snow Factor added
                      </div>
                    </div>

                    {/* Empirical Regression */}
                    <div className="comparison-card highlighted">
                      <button 
                        className="comparison-model-link"
                        onClick={() => openNotebook('regression')}
                        title={lang === 'ru' ? "Открыть Jupyter-ноутбук" : "Open Jupyter Notebook"}
                      >
                        <span>{translate('empRegression')}</span>
                        <BookOpen size={14} className="notebook-link-icon" />
                      </button>
                      <div className="comparison-model-val">{altRegressVal.toFixed(1)} см</div>
                      <div className="comparison-model-diff" style={{ color: 'var(--accent-primary)' }}>
                        {lang === 'ru' ? "Оптимальная калибровка" : "Fully Calibrated"}
                      </div>
                    </div>
                  </div>

                  {/* Physics details */}
                  <div style={{ textAlign: 'left', background: 'rgba(0, 0, 0, 0.2)', padding: '16px', borderRadius: 'var(--radius-md)', fontSize: '13.5px', color: 'var(--text-secondary)' }}>
                    <h4 style={{ color: 'var(--text-primary)', margin: '0 0 8px' }}>
                      {lang === 'ru' ? "Математическая справка по моделям" : "Mathematical Reference"}
                    </h4>
                    <p style={{ margin: '0 0 10px' }}>
                      {lang === 'ru' ? (
                        <>
                          1. <button className="reference-model-link" onClick={() => openNotebook('classic')} title="Открыть Jupyter-ноутбук">Модель Стефана</button>: Решает классическое одномерное уравнение фазового перехода. ALT = 4.34 * √DDT. Включает только термический фактор.
                          <br /><br />
                          2. <button className="reference-model-link" onClick={() => openNotebook('hybrid')} title="Открыть Jupyter-ноутбук">Гибридная модель Стефана</button>: Учитывает теплоизоляционный эффект зимнего снега, который препятствует промерзанию грунта.
                          <br /><br />
                          3. <button className="reference-model-link" onClick={() => openNotebook('regression')} title="Открыть Jupyter-ноутбук">Эмпирическая регрессионная модель</button>: Откалибрована по 20-летнему ряду метеонаблюдений Якутска. Включает испарение, осадки и просадки грунта. Коэффициент детерминации R² = 0.86.
                        </>
                      ) : (
                        <>
                          1. <button className="reference-model-link" onClick={() => openNotebook('classic')} title="Open Jupyter Notebook">Classic Stefan Equation</button>: Solves 1D heat flow phase boundary transition. ALT = 4.34 * √DDT. Focuses strictly on surface heat input.
                          <br /><br />
                          2. <button className="reference-model-link" onClick={() => openNotebook('hybrid')} title="Open Jupyter Notebook">Hybrid Stefan Model</button>: Adds corrective parameter for insulated winter snow layer which restricts cold infiltration.
                          <br /><br />
                          3. <button className="reference-model-link" onClick={() => openNotebook('regression')} title="Open Jupyter Notebook">Empirical Regression Model</button>: Calibrated using Yakutsk meteorology historical records (2005-2024). Account for summer rains, evaporation, and long-term consolidation. R² = 0.86.
                        </>
                      )}
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB 4: LENA RIVER HYDROLOGY */}
          {activeTab === 'river' && (
            <>
              <div className="view-header">
                <h2>{translate('riverTitle')}</h2>
                <p>{translate('riverDesc')}</p>
              </div>

              <div className="split-layout">
                {/* Inputs */}
                <div className="glass-panel form-group">
                  <h3 className="panel-title">
                    <Droplets size={18} style={{ color: 'var(--accent-primary)' }} />
                    {translate('riverParams')}
                  </h3>

                  {/* Lensk peak input */}
                  <div className="input-container">
                    <label className="input-label">{translate('riverLenskPeak')} (см)</label>
                    <input
                      type="number"
                      min="400"
                      max="1600"
                      value={riverLensk}
                      onChange={(e) => {setRiverLensk(Number(e.target.value)); setSelectedYear(null);}}
                      className="text-input"
                    />
                    <input
                      type="range"
                      min="400"
                      max="1600"
                      value={riverLensk}
                      onChange={(e) => {setRiverLensk(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control"
                      style={{ '--val-pct': `${((riverLensk - 400) / (1600 - 400)) * 100}%` }}
                    />
                  </div>

                  {/* Olekminsk peak input */}
                  <div className="input-container">
                    <label className="input-label">{translate('riverOlekPeak')} (см)</label>
                    <input
                      type="number"
                      min="400"
                      max="1300"
                      value={riverOlek}
                      onChange={(e) => {setRiverOlek(Number(e.target.value)); setSelectedYear(null);}}
                      className="text-input"
                    />
                    <input
                      type="range"
                      min="400"
                      max="1300"
                      value={riverOlek}
                      onChange={(e) => {setRiverOlek(Number(e.target.value)); setSelectedYear(null);}}
                      className="slider-control cyan"
                      style={{ '--val-pct': `${((riverOlek - 400) / (1300 - 400)) * 100}%` }}
                    />
                  </div>
                </div>

                {/* Outputs & warnings */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <h3 className="panel-title">
                    <ShieldAlert size={18} style={{ color: 'var(--accent-secondary)' }} />
                    {translate('riverForecast')}
                  </h3>

                  {/* Forecast Display card */}
                  <div className="countdown-box" style={{ padding: '24px', borderLeft: `4px solid var(--color-${riverWarning.status === 'CRITICAL' ? 'extreme' : riverWarning.status === 'WARNING' ? 'moderate' : 'low'})` }}>
                    <span className="countdown-title">{translate('riverYktPeak')}</span>
                    <span className="countdown-year" style={{ color: `var(--color-${riverWarning.status === 'CRITICAL' ? 'extreme' : riverWarning.status === 'WARNING' ? 'moderate' : 'low'})` }}>
                      {Math.round(riverPredictedLevel)} см
                    </span>
                    <span className="countdown-desc" style={{ fontFamily: 'var(--mono)', fontSize: '11px', marginTop: '6px' }}>
                      {translate('riverTimeLag')}
                    </span>
                  </div>

                  {/* Warning message card */}
                  <div className={`checklist-item`} style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '16px' }}>
                    <AlertTriangle 
                      className={`checklist-icon`} 
                      style={{ color: `var(--color-${riverWarning.status === 'CRITICAL' ? 'extreme' : riverWarning.status === 'WARNING' ? 'moderate' : 'low'})` }} 
                      size={24} 
                    />
                    <div>
                      <h4 style={{ margin: '0 0 4px', color: 'var(--text-primary)' }}>
                        {riverWarning.status === 'CRITICAL' ? "CRITICAL ALERT" : riverWarning.status === 'WARNING' ? "WARNING ALERT" : "NORMAL STATUS"}
                      </h4>
                      <p style={{ fontSize: '13px', margin: 0, color: 'var(--text-secondary)' }}>
                        {lang === 'ru' ? riverWarning.msg_ru : riverWarning.msg_en}
                      </p>
                    </div>
                  </div>

                  {/* Technical description of water propagation on Lena */}
                  <div style={{ textAlign: 'left', fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {lang === 'ru' ? (
                      <>
                        * Модель использует линейно-динамическую аппроксимацию распространения паводковой волны по длине реки Лена. 
                        Прогноз строится на основе пиков в верховьях (Ленск, Олёкминск) с весовыми коэффициентами влияния притоков: 38% и 42% соответственно.
                      </>
                    ) : (
                      <>
                        * The model applies a dynamic wave routing routing approximation along the Lena River. 
                        The forecast is computed using peak level indicators at upstream stations (Lensk, Olekminsk) with weights of 38% and 42%.
                      </>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB 5: HISTORICAL DATABASE EXPLORER & CHART */}
          {activeTab === 'archive' && (
            <>
              <div className="view-header">
                <h2>{translate('archiveTitle')}</h2>
                <p>{translate('archiveDesc')}</p>
              </div>

              {/* Programmatic Interactive SVG Chart */}
              <div className="glass-panel">
                <h3 className="panel-title">
                  <TrendingUp size={18} style={{ color: 'var(--accent-primary)' }} />
                  {translate('chartTitle')}
                </h3>
                
                <div className="chart-container">
                  <svg width="100%" height={chartH} viewBox={`0 0 ${chartW} ${chartH}`} style={{ minWidth: '700px' }}>
                    {/* Gridlines */}
                    {[0, 1, 2, 3, 4].map((i) => {
                      const y = paddingY + (i / 4) * (chartH - 2 * paddingY);
                      const ddtVal = ddtMax - (i / 4) * (ddtMax - ddtMin);
                      const altVal = altMax - (i / 4) * (altMax - altMin);
                      return (
                        <g key={i}>
                          <line x1={paddingX} y1={y} x2={chartW - paddingX} y2={y} className="chart-grid-line" />
                          {/* Left Axis labels (DDT) */}
                          <text x={paddingX - 10} y={y + 4} textAnchor="end" className="chart-grid-text">
                            {Math.round(ddtVal)}
                          </text>
                          {/* Right Axis labels (ALT) */}
                          <text x={chartW - paddingX + 10} y={y + 4} textAnchor="start" className="chart-grid-text">
                            {altVal.toFixed(0)}
                          </text>
                        </g>
                      );
                    })}

                    {/* Timeline X Axis Text */}
                    {historicalData.map((item, idx) => {
                      const { x } = getChartCoords(item);
                      return (
                        <text key={idx} x={x} y={chartH - 8} textAnchor="middle" className="chart-grid-text" style={{ fontSize: '10px' }}>
                          {item.year}
                        </text>
                      );
                    })}

                    {/* Y Axis Borders */}
                    <line x1={paddingX} y1={paddingY} x2={paddingX} y2={chartH - paddingY} className="chart-axis-line" />
                    <line x1={chartW - paddingX} y1={paddingY} x2={chartW - paddingX} y2={chartH - paddingY} className="chart-axis-line" />

                    {/* Trend Line DDT */}
                    <path d={ddtPath} className="chart-line primary" />

                    {/* Trend Line ALT */}
                    <path d={altPath} className="chart-line secondary" />

                    {/* Interactive dots */}
                    {historicalData.map((item, idx) => {
                      const { x, yDdt, yAlt } = getChartCoords(item);
                      const isActive = selectedYear === item.year;
                      return (
                        <g key={idx}>
                          {/* DDT point */}
                          <circle
                            cx={x}
                            cy={yDdt}
                            r={isActive ? 7 : 4}
                            className={`chart-dot primary ${isActive ? 'active' : ''}`}
                            onClick={() => loadHistoricalYear(item)}
                          />
                          {/* ALT point */}
                          <circle
                            cx={x}
                            cy={yAlt}
                            r={isActive ? 7 : 4}
                            className={`chart-dot secondary ${isActive ? 'active' : ''}`}
                            onClick={() => loadHistoricalYear(item)}
                          />
                        </g>
                      );
                    })}
                  </svg>

                  <div className="chart-legend">
                    <div className="legend-item">
                      <span className="legend-color purple"></span>
                      <span>{translate('legendDdt')}</span>
                    </div>
                    <div className="legend-item">
                      <span className="legend-color cyan"></span>
                      <span>{translate('legendAlt')}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Table list */}
              <div className="glass-panel table-panel">
                <table className="archive-table">
                  <thead>
                    <tr>
                      <th>{translate('archiveHeaderYear')}</th>
                      <th>{translate('archiveHeaderDdt')}</th>
                      <th>{translate('archiveHeaderDdf')}</th>
                      <th>{translate('archiveHeaderSnow')}</th>
                      <th>{translate('archiveHeaderTemp')}</th>
                      <th>{translate('archiveHeaderAlt')}</th>
                      <th>{translate('archiveHeaderFlood')}</th>
                      <th>{translate('archiveHeaderAnoms')}</th>
                      <th style={{ width: '40px' }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {historicalData.map((item) => {
                      const isActive = selectedYear === item.year;
                      return (
                        <tr 
                          key={item.year}
                          className={isActive ? 'active' : ''}
                          onClick={() => loadHistoricalYear(item)}
                        >
                          <td style={{ fontWeight: 'bold', color: 'var(--text-primary)' }}>{item.year}</td>
                          <td>{item.ddt.toFixed(0)}</td>
                          <td>{item.ddf.toFixed(0)}</td>
                          <td>{item.h_snow}</td>
                          <td>{item.t320 !== null ? `${item.t320.toFixed(2)} °С` : '—'}</td>
                          <td style={{ color: 'var(--accent-secondary)', fontWeight: 'bold' }}>
                            {item.alt_measured !== null ? `${item.alt_measured} см` : '—'}
                          </td>
                          <td>{item.ykt_peak_measured !== null ? `${item.ykt_peak_measured} см` : '—'}</td>
                          <td style={{ fontFamily: 'var(--sans)', fontSize: '12px' }}>
                            {item.anomalies.map((an, i) => (
                              <span 
                                key={i} 
                                className={`anomaly-badge ${an.severity === 'экстремальная' ? 'extreme' : ''}`}
                              >
                                {an.signals}
                              </span>
                            ))}
                            {item.anomalies.length === 0 ? '—' : ''}
                          </td>
                          <td>
                            <ArrowRight size={14} style={{ opacity: isActive ? 1 : 0.2 }} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* TAB 6: SOIL THERMAL STABILITY & TIMELINE */}
          {activeTab === 'soil_thermal' && (
            <>
              <div className="view-header">
                <h2>{translate('soilTitle')}</h2>
                <p>{translate('soilDesc')}</p>
              </div>

              <div className="split-layout">
                {/* Timeline controls */}
                <div className="glass-panel form-group">
                  <h3 className="panel-title">
                    <Calendar size={18} style={{ color: 'var(--accent-primary)' }} />
                    {translate('soilParams')}
                  </h3>

                  {/* Year slider */}
                  <div className="slider-container" style={{ padding: '20px 14px' }}>
                    <div className="slider-header">
                      <span className="slider-label">{translate('soilTimeline')}</span>
                      <span className="slider-value" style={{ fontSize: '20px', color: 'var(--accent-primary)' }}>
                        {soilYear} год
                      </span>
                    </div>
                    <input
                      type="range"
                      min="2025"
                      max="2060"
                      value={soilYear}
                      onChange={(e) => setSoilYear(Number(e.target.value))}
                      className="slider-control"
                      style={{ '--val-pct': `${((soilYear - 2025) / (2060 - 2025)) * 100}%` }}
                    />
                    <div className="slider-limits">
                      <span>2025 год</span>
                      <span>2060 год</span>
                    </div>
                  </div>
                </div>

                {/* Extrapolation outputs */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <h3 className="panel-title">
                    <TrendingUp size={18} style={{ color: 'var(--accent-secondary)' }} />
                    {lang === 'ru' ? "Анализ деградации мерзлотной опоры" : "Thermodynamic Bearing Projection"}
                  </h3>

                  {/* Temp projection */}
                  <div className="countdown-box">
                    <span className="countdown-title">{translate('soilTrendValue')}</span>
                    <span className="countdown-year" style={{ color: projectedSoilTemp >= 0 ? 'var(--color-extreme)' : 'var(--accent-secondary)' }}>
                      {projectedSoilTemp.toFixed(3)} °C
                    </span>
                  </div>

                  {/* Countdown timer */}
                  <div className="countdown-box" style={{ background: 'rgba(0, 0, 0, 0.4)' }}>
                    <span className="countdown-title">{translate('soilFailureTitle')}</span>
                    <span className="countdown-year" style={{ color: 'var(--color-extreme)', fontSize: '42px' }}>
                      {soilFailureYear} г.
                    </span>
                    <span className="countdown-desc">
                      {yearsUntilFailure > 0 ? (
                        <>
                          {translate('soilYearsLeft')} <strong style={{ color: 'var(--color-extreme)', fontSize: '18px', fontFamily: 'var(--mono)' }}>{yearsUntilFailure}</strong> {lang === 'ru' ? "лет" : "years"}
                        </>
                      ) : (
                        <span style={{ color: 'var(--color-extreme)', fontWeight: 'bold' }}>
                          {lang === 'ru' ? "Аварийный сдвиг уже произошел!" : "Foundation integrity has failed!"}
                        </span>
                      )}
                    </span>
                  </div>

                  {/* Security Alert strip */}
                  <div className="checklist-item" style={{ background: projectedSoilTemp >= 0 ? 'var(--color-extreme-glow)' : 'rgba(16, 185, 129, 0.05)', borderColor: projectedSoilTemp >= 0 ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.2)' }}>
                    <AlertTriangle className="checklist-icon" style={{ color: projectedSoilTemp >= 0 ? 'var(--color-extreme)' : 'var(--color-low)' }} size={20} />
                    <span style={{ color: projectedSoilTemp >= 0 ? 'var(--color-extreme)' : 'var(--color-low)', fontWeight: '700' }}>
                      {projectedSoilTemp >= 0 ? translate('soilStatusDanger') : translate('soilStatusSafe')}
                    </span>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* TAB 7: INTERACTIVE SYSTEM GUIDE & BASE OF KNOWLEDGE */}
          {activeTab === 'guide' && (
            <>
              <div className="view-header">
                <h2>{translate('guideTitle')}</h2>
                <p>{translate('guideDesc')}</p>
              </div>

              <div className="split-layout">
                {/* Launch Tour Banner Card */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', gap: '24px', padding: '40px 24px', border: '3px solid var(--accent-secondary)', background: 'var(--accent-secondary-glow)', backdropFilter: 'blur(20px)' }}>
                  <HelpCircle size={64} style={{ color: 'var(--accent-secondary)', filter: 'drop-shadow(0 0 16px var(--accent-secondary))' }} />
                  <div>
                    <h3 style={{ fontSize: '24px', fontWeight: '800', margin: '0 0 12px', color: 'var(--text-primary)' }}>
                      {lang === 'ru' ? "Интерактивный путеводитель" : "Interactive Guided Tour"}
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '1.5', maxWidth: '380px', margin: '0 auto' }}>
                      {lang === 'ru' 
                        ? "Запустите пошаговое обучение работе с системой! Вы увидите каждую вкладку в действии, познакомитесь с математическими формулами и поймете, как физика вечной мерзлоты влияет на регламенты МЧС."
                        : "Start step-by-step guidance! You will see each tab in action, explore mathematical models, and understand how permafrost degradation dictates emergency protocols."}
                    </p>
                  </div>

                  <button
                    className="btn-round"
                    onClick={() => { setTourActive(true); setTourStep(0); }}
                    style={{ background: 'var(--accent-secondary)', borderColor: 'var(--text-primary)', color: '#070913', padding: '16px 32px', fontSize: '16px', fontWeight: '800', borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-glow-cyan)', width: 'auto' }}
                  >
                    <span>{translate('guideLaunchTour')}</span>
                  </button>
                </div>

                {/* Theory & Math Base Cards */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div className="glass-panel" style={{ padding: '20px' }}>
                    <h3 className="panel-title" style={{ fontSize: '16px', margin: '0 0 12px', borderBottom: 'none', paddingBottom: '0' }}>
                      <TrendingUp size={16} style={{ color: 'var(--accent-primary)' }} />
                      {translate('guideTheoryTitle')}
                    </h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '13px', margin: '0' }}>
                      {translate('guideTheoryDesc')}
                    </p>
                  </div>

                  <div className="theory-card-stack" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {/* Card 1 */}
                    <div className="input-container" style={{ gap: '6px' }}>
                      <span className="input-label" style={{ color: 'var(--accent-primary)', fontSize: '14px' }}>{translate('theoryStefanTitle')}</span>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0', lineHeight: '1.4', textAlign: 'left' }}>{translate('theoryStefanBody')}</p>
                    </div>

                    {/* Card 2 */}
                    <div className="input-container" style={{ gap: '6px' }}>
                      <span className="input-label" style={{ color: 'var(--accent-secondary)', fontSize: '14px' }}>{translate('theoryDssTitle')}</span>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0', lineHeight: '1.4', textAlign: 'left' }}>{translate('theoryDssBody')}</p>
                    </div>

                    {/* Card 3 */}
                    <div className="input-container" style={{ gap: '6px' }}>
                      <span className="input-label" style={{ color: 'var(--color-low)', fontSize: '14px' }}>{translate('theoryRiverTitle')}</span>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0', lineHeight: '1.4', textAlign: 'left' }}>{translate('theoryRiverBody')}</p>
                    </div>

                    {/* Card 4 */}
                    <div className="input-container" style={{ gap: '6px' }}>
                      <span className="input-label" style={{ color: 'var(--color-extreme)', fontSize: '14px' }}>{translate('theorySoilTitle')}</span>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0', lineHeight: '1.4', textAlign: 'left' }}>{translate('theorySoilBody')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

        </div>

        {/* 🔮 Guided Interactive Tour Overlay Panel */}
        {tourActive && (
          <div 
            className="tour-overlay-card animate-fade-in"
            style={{
              position: 'fixed',
              bottom: '30px',
              right: '30px',
              width: '420px',
              background: 'var(--ctrl-bg)',
              border: '3px solid var(--accent-secondary)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-glow-cyan), 0 20px 40px rgba(0,0,0,0.6)',
              padding: '24px',
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              backdropFilter: 'blur(20px)'
            }}
          >
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid var(--panel-border)', paddingBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <HelpCircle size={20} style={{ color: 'var(--accent-secondary)' }} />
                <span style={{ fontWeight: '800', fontSize: '15px', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {translate('tourTitle')}
                </span>
              </div>
              <span style={{ fontFamily: 'var(--mono)', fontSize: '12px', fontWeight: '800', color: 'var(--accent-secondary)' }}>
                {translate('tourIndicator').replace('{step}', tourStep + 1)}
              </span>
            </div>

            {/* Step content */}
            <div style={{ textAlign: 'left' }}>
              <h4 style={{ fontSize: '17px', fontWeight: '800', color: 'var(--text-primary)', margin: '0 0 8px' }}>
                {translate(`tourStepTitle_${tourStep}`)}
              </h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13.5px', lineHeight: '1.4', margin: '0' }}>
                {translate(`tourStepDesc_${tourStep}`)}
              </p>
            </div>

            {/* Navigation Controls */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
              <button
                className="btn-round"
                onClick={() => setTourActive(false)}
                style={{ padding: '6px 12px', fontSize: '12px', background: 'transparent', borderColor: 'var(--text-muted)', color: 'var(--text-muted)' }}
              >
                {translate('tourFinish')}
              </button>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  className="btn-round"
                  onClick={() => setTourStep(prev => Math.max(0, prev - 1))}
                  disabled={tourStep === 0}
                  style={{ padding: '6px 14px', fontSize: '12px', opacity: tourStep === 0 ? 0.35 : 1, cursor: tourStep === 0 ? 'not-allowed' : 'pointer' }}
                >
                  {translate('tourPrev')}
                </button>

                <button
                  className="btn-round"
                  onClick={() => {
                    if (tourStep === 5) {
                      setTourActive(false);
                    } else {
                      setTourStep(prev => prev + 1);
                    }
                  }}
                  style={{
                    padding: '6px 16px',
                    fontSize: '12px',
                    background: 'var(--accent-secondary)',
                    borderColor: 'var(--text-primary)',
                    color: '#070913',
                    boxShadow: '0 0 10px rgba(34, 211, 238, 0.3)'
                  }}
                >
                  {tourStep === 5 ? translate('tourFinish') : translate('tourNext')}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* 📓 Interactive Jupyter Notebook Modal Overlay */}
      {activeNotebook && (
        <div className="jupyter-modal-overlay">
          <div className="jupyter-modal animate-scale-up">
            
            {/* Notebook Window Header */}
            <div className="jupyter-modal-header">
              <div className="jupyter-header-left">
                <FileCode className="jupyter-header-icon" size={18} />
                <span className="jupyter-filename">
                  {notebookData[activeNotebook].filename}
                </span>
                <span className="jupyter-kernel-indicator">
                  <span className="kernel-dot pulse"></span>
                  {Object.values(cellStatus).some(c => c && c.running) ? translate('notebookStatusBusy') : translate('notebookStatusReady')}
                </span>
              </div>
              
              <div className="jupyter-header-right">
                <button 
                  className="btn-nb-toolbar" 
                  onClick={handleRunAll}
                  disabled={Object.values(cellStatus).some(c => c && c.running)}
                  title={translate('notebookRunAll')}
                >
                  <Play size={13} fill="currentColor" />
                  <span>{translate('notebookRunAll')}</span>
                </button>
                
                <button 
                  className="btn-nb-toolbar" 
                  onClick={handleRestartKernel}
                  title={translate('notebookRestart')}
                >
                  <RefreshCw size={13} />
                  <span>{translate('notebookRestart')}</span>
                </button>
                
                <a 
                  href={notebookData[activeNotebook].downloadUrl} 
                  download 
                  className="btn-nb-toolbar btn-download-nb"
                  title={translate('notebookDownload')}
                >
                  <Download size={13} />
                  <span>{translate('notebookDownload')}</span>
                </a>
                
                <button 
                  className="btn-nb-close" 
                  onClick={() => setActiveNotebook(null)}
                  title={translate('notebookClose')}
                >
                  <X size={20} />
                </button>
              </div>
            </div>
            
            {/* Notebook Window Body */}
            <div className="jupyter-modal-body">
              {notebookData[activeNotebook].cells.map((cell, idx) => {
                const status = cellStatus[idx] || { running: false, executed: false, count: null, output: "" };
                
                return (
                  <div key={idx} className={`jupyter-cell ${cell.type}`}>
                    
                    {/* Left execution prompt gutter */}
                    <div className="cell-gutter">
                      {cell.type !== 'markdown' && (
                        <div className="execution-indicator">
                          {status.running ? (
                            <RefreshCw size={14} className="spin-indicator" />
                          ) : status.executed ? (
                            `[In ${status.count}]`
                          ) : (
                            '[In ]'
                          )}
                        </div>
                      )}
                      
                      {(cell.type === 'code' || cell.type === 'interactive_code') && (
                        <button 
                          className="cell-run-btn"
                          onClick={() => handleRunCell(idx)}
                          disabled={status.running}
                          title={lang === 'ru' ? 'Запустить ячейку' : 'Run Cell'}
                        >
                          <Play size={11} fill="currentColor" />
                        </button>
                      )}
                    </div>
                    
                    {/* Main cell content area */}
                    <div className="cell-content">
                      {/* Markdown Cell */}
                      {cell.type === 'markdown' && (
                        <div 
                          className="markdown-rendered"
                          dangerouslySetInnerHTML={{ 
                            __html: lang === 'ru' 
                              ? formatMarkdown(cell.content_ru) 
                              : formatMarkdown(cell.content_en) 
                          }}
                        />
                      )}
                      
                      {/* Standard Code Cell */}
                      {cell.type === 'code' && (
                        <div className="code-editor-box">
                          <pre className="code-editor-pre">
                            <code>
                              {typeof cell.code === 'function' ? cell.code(nbParams) : cell.code}
                            </code>
                          </pre>
                        </div>
                      )}
                      
                      {/* Interactive Code Cell */}
                      {cell.type === 'interactive_code' && (
                        <div className="code-editor-box interactive">
                          {/* Code pre box */}
                          <pre className="code-editor-pre">
                            <code>
                              {typeof cell.code === 'function' ? cell.code(nbParams) : cell.code}
                            </code>
                          </pre>
                          
                          {/* Interactive Parameter Control Controls */}
                          <div className="notebook-interactive-controls">
                            <div className="controls-header">
                              <Settings size={14} />
                              <span>{translate('notebookInputHeader')}</span>
                            </div>
                            
                            <div className="nb-sliders-grid">
                              {cell.interactive_fields.map((field) => {
                                const fieldVal = nbParams[field.name] !== undefined ? nbParams[field.name] : field.min;
                                return (
                                  <div key={field.name} className="nb-slider-row">
                                    <label className="nb-slider-label">
                                      <span>{lang === 'ru' ? field.label_ru : field.label_en}:</span>
                                      <strong className="nb-slider-value">{fieldVal.toFixed(field.step < 0.01 ? 5 : field.step < 0.1 ? 4 : field.step < 1 ? 2 : 0)}</strong>
                                    </label>
                                    <input 
                                      type="range"
                                      min={field.min}
                                      max={field.max}
                                      step={field.step}
                                      value={fieldVal}
                                      onChange={(e) => handleNbParamChange(field.name, Number(e.target.value))}
                                      className="nb-slider-input"
                                    />
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Cell execution output */}
                      {status.executed && (
                        <div className="cell-output-box animate-fade-in">
                          {status.output && (
                            <pre className="cell-stdout">
                              {status.output}
                            </pre>
                          )}
                          
                          {/* Plot SVG (only for interactive field cell) */}
                          {cell.render_plot && (
                            <div className="notebook-chart-container">
                              {renderCellPlot(cell, nbParams)}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {status.running && (
                        <div className="cell-running-overlay">
                          <span className="running-dot"></span>
                          <span className="running-dot"></span>
                          <span className="running-dot"></span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
