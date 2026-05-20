import os
import pandas as pd
import numpy as np

class HydroPropagationModel:
    """
    Model for analyzing and forecasting river peak levels and travel times along the Lena River.
    Supports dynamic fitting on historical data and provides pre-calibrated default values:
      - Travel Lags: Lensk -> Yakutsk: 4.4 days, Olekminsk -> Yakutsk: 3.9 days, Yakutsk -> Zhigansk: 3.8 days
      - Peak Thresholds for Yakutsk: Warning = 700 cm, Critical = 850 cm
    """
    def __init__(self, data_dir=None):
        self.data_dir = data_dir
        # Pre-calibrated lags (in days)
        self.default_lags = {
            'lensk_yakutsk': 4.4,
            'olekminsk_yakutsk': 3.9,
            'yakutsk_zhigansk': 3.8
        }
        # Pre-calibrated regression coefficients: H_ykt = a0 + a1 * H_lensk + a2 * H_olek
        self.coef_a0 = -120.0
        self.coef_a1 = 0.38
        self.coef_a2 = 0.42
        
        self.is_fitted = False
        
        if data_dir and os.path.exists(data_dir):
            try:
                self.fit_from_data(data_dir)
            except Exception as e:
                # Silently fallback to defaults if data path parse fails
                pass

    def _extract_spring_peaks(self, filepath):
        """
        Extract annual spring flood peak level and date (May-June) from a hydro CSV file.
        The file has Date;Value format.
        """
        df = pd.read_csv(filepath, sep=';', parse_dates=['Date'])
        df.columns = ['Date', 'Value']
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna()
        
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        
        df_spring = df[df['Month'].isin([5, 6])]
        
        peaks = []
        for yr, group in df_spring.groupby('Year'):
            if len(group) > 15:
                idx_max = group['Value'].idxmax()
                row_max = group.loc[idx_max]
                peaks.append({
                    'year': int(yr),
                    'peak_date': row_max['Date'],
                    'peak_value': float(row_max['Value'])
                })
        return pd.DataFrame(peaks)

    def fit_from_data(self, data_dir):
        """
        Dynamically load hydro logs from a directory and fit travel lags and peak level regressions.
        :param data_dir: absolute path to directory containing lena-*.csv files.
        """
        lensk_path = os.path.join(data_dir, "lena-lensk.csv")
        olek_path = os.path.join(data_dir, "lena-olekminsk.csv")
        ykt_path = os.path.join(data_dir, "lena-yakutsk.csv")
        zhig_path = os.path.join(data_dir, "lena-zhigansk.csv")
        
        if not (os.path.exists(lensk_path) and os.path.exists(olek_path) and os.path.exists(ykt_path)):
            return
            
        df_lensk = self._extract_spring_peaks(lensk_path)
        df_olek = self._extract_spring_peaks(olek_path)
        df_ykt = self._extract_spring_peaks(ykt_path)
        
        # Fit peak level regression: H_ykt = a0 + a1 * H_lensk + a2 * H_olek
        df_m = pd.merge(df_ykt, df_lensk, on='year', suffixes=('_ykt', '_lensk'))
        df_m = pd.merge(df_m, df_olek, on='year')
        df_m.rename(columns={'peak_value': 'peak_value_olek', 'peak_date': 'peak_date_olek'}, inplace=True)
        
        if len(df_m) >= 5:
            # Multi-variable OLS regression using numpy
            y = df_m['peak_value_ykt'].values
            x1 = df_m['peak_value_lensk'].values
            x2 = df_m['peak_value_olek'].values
            
            A = np.column_stack([np.ones(len(y)), x1, x2])
            w, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
            
            self.coef_a0 = w[0]
            self.coef_a1 = w[1]
            self.coef_a2 = w[2]
            
            # Re-estimate lags
            lags_lensk = (df_m['peak_date_ykt'] - df_m['peak_date_lensk']).dt.days
            lags_olek = (df_m['peak_date_ykt'] - df_m['peak_date_olek']).dt.days
            
            self.default_lags['lensk_yakutsk'] = float(np.mean(lags_lensk))
            self.default_lags['olekminsk_yakutsk'] = float(np.mean(lags_olek))
            
            if os.path.exists(zhig_path):
                df_zhig = self._extract_spring_peaks(zhig_path)
                df_mz = pd.merge(df_ykt, df_zhig, on='year', suffixes=('_ykt', '_zhig'))
                if not df_mz.empty:
                    lags_zhig = (df_mz['peak_date_zhig'] - df_mz['peak_date_ykt']).dt.days
                    self.default_lags['yakutsk_zhigansk'] = float(np.mean(lags_zhig))
            
            self.is_fitted = True

    def predict_peak_level(self, h_lensk, h_olek):
        """
        Forecast the spring peak level in Yakutsk in cm.
        :param h_lensk: Lensk peak level in cm (float)
        :param h_olek: Olekminsk peak level in cm (float)
        """
        return self.coef_a0 + self.coef_a1 * h_lensk + self.coef_a2 * h_olek

    def predict_peak_date(self, base_date, origin='lensk'):
        """
        Forecast peak arrival date in Yakutsk from an upstream peak date.
        :param base_date: datetime object or Timestamp of the upstream peak
        :param origin: 'lensk' or 'olekminsk'
        """
        lag_days = self.default_lags['lensk_yakutsk'] if origin == 'lensk' else self.default_lags['olekminsk_yakutsk']
        return base_date + pd.Timedelta(days=round(lag_days))

    def predict_downstream_date(self, yakutsk_date):
        """
        Forecast peak arrival date in Zhigansk from the Yakutsk peak date.
        :param yakutsk_date: datetime object or Timestamp of the Yakutsk peak
        """
        lag_days = self.default_lags['yakutsk_zhigansk']
        return yakutsk_date + pd.Timedelta(days=round(lag_days))

    def evaluate_warning(self, level):
        """
        Return warnings based on the Yakutsk peak level.
        """
        if level >= 850:
            return "CRITICAL", "Угроза масштабных затоплений, разрушения береговой линии и дамб (Порог 850 см пройден!)"
        elif level >= 700:
            return "WARNING", "Выход воды на пойму, подтопление дачных участков и пониженных участков дорог (Порог 700 см пройден)"
        return "NORMAL", "Уровень воды в пределах нормы"
