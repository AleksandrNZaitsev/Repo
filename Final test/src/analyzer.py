import pandas as pd
import logging
from pathlib import Path

class OrderAnalyzer:
    def __init__(self, config):
        self.config = config
        self.results = []

        log_path = Path(self.config.LOG_DIR) / "errors.log"
        log_path.parent.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_path,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def load_file(self, filepath):
        try:
            df = pd.read_csv(filepath)
            if df.empty:
                raise ValueError(f'Файл {filepath} пустой')
            if len(df.columns) == 1:
                first_col = df.columns[0]
                if'"' in first_col or ',' in first_col:
                    raise ValueError("Первая строка содержит разделители, найдена только одна колонка: '{first_col[:50}'")
            if 'total_amount' not in df.columns:
                raise ValueError(f"Нет колонки 'total_amount' в файле {filepath}")
            df['total_amount'] = pd.to_numeric(df['total_amount'], errors = 'coerce')
            return df
        except Exception as e:
            self.logger.error(f'Ошибка загрузки файла: {e}. Путь к файлу: "{filepath}"')
            return None

    def find_status_column(self, df):
        possible_names = ['status', 'Status', 'order_status', 'OrderStatus', 'state', 'order_state', 'STATUS']
        for col in possible_names:
            if col in df.columns:
                print(f"Найдена колонка статуса: '{col}'")
                return col

        print(f"Доступные колонки: {list(df.columns)}")
        raise ValueError(f'Не найдена колонка со статусом. Искали {possible_names}')


    def filter_delivered(self, df):
        status_col = self.find_status_column(df)

        delivered_mask = df[status_col].astype(str).str.lower() == self.config.DELIVERED_STATUS.lower()
        delivered = df[delivered_mask].copy()

        print(f'Всего заказов: {len (df)}, "доставленных": {len(delivered)}')
        return delivered

    def calculate_metrics(self, df):
        if df.empty:
            return {'revenue' : 0, 'avg_order_value': 0, 'orders_count': 0}

        clean_df = df.dropna(subset=['total_amount'])

        return{
            'revenue': clean_df['total_amount'].sum(),
            'avg_order_value':clean_df ['total_amount'].mean(),
            'orders_count': len(df)}

    def process_file(self, filepath):
        df = self.load_file(filepath)
        if df is None:
            return None

        delivered_df = self.filter_delivered(df)
        metrics = self.calculate_metrics(delivered_df)
        metrics['filename']= filepath.name
        return metrics

    def process_all_files(self):
        data_dir = Path(self.config.INPUT_DIR)
        csv_files = list(data_dir.glob("*.csv"))

        print(f"Найдено CSV файлов:{len(csv_files)}")

        processed = 0
        errors = 0

        for csv_file in csv_files:
            result = self.process_file(csv_file)
            if result is None:
                errors +=1
            else:
                self.results.append(result)
                processed+= 1

        self.save_results()

        print(f'\nОбработано успешно: {processed}')
        print(f'\nОбработано с ошибками: {errors}')

        return processed, errors

    def save_results(self):
        if not self.results:
            print(f'Нет результатов для сохранения')
            return

        result_df = pd.DataFrame(self.results)
        output_path = Path(self.config.OUTPUT_DIR)
        output_path.mkdir(exist_ok= True)
        result_df.to_csv(output_path / self.config.OUTPUT_FILE, index=False)





