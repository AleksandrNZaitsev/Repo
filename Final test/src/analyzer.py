import pandas as pd
import logging
from pathlib import Path

class OrderAnalyzer:
    def __init__(self, config):
        self.config = config
        self.results = []
        self.setup_logging()

    def setup_logging(self):
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
            return df
        except Exception as e:
            self.logger.error(f'Ошибка загрузки файла: {e}. Путь к файлу: "{filepath}"')
            return None

    def filter_delivered(self, df):
        return df[df[self.config.STATUS_COLUMN] == self.config.DELIVERED_STATUS].copy()

    def calculate_metrics(self, df):
        if df.empty:
            return {'revenue' : 0, 'avf_order_value': 0, 'orders_count': 0}

        return{
            'revenue': df['total_amount'].sum(),
            'avg_order_valie':df ['total_amount'].mean(),
            'order_counts': len(df)}

    def process_file(self, filepath):
        df = self.load_file(filepath)
        if df is None:
            return None

        delivered_df = self.filter_delivered(df)
        metrics = self.calculate_metrics(delivered_df)
        metrics['filepath']= filepath.name
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
        result_df.to_csv(output_path / self.config.PUTPUT_FILE, index=False)





