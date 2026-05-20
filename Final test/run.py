import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

import config
from src.analyzer import OrderAnalyzer

def main():
    print('+' * 50)
    print('ЗАПУСК АНАЛИЗАТОРА ЗАКАЗОВ')
    print('+' * 50)

    analyzer = OrderAnalyzer(config)
    processed, errors = analyzer.process_all_files()

    if analyzer.results:
        print('\nРЕЗУЛЬТАТЫ ПО ФАЙЛАМ:')
        for r in analyzer.results:
            print(f"{r['filename']}: {r["orders_count"]} заказов, выручка: {r['revenue']:.2f}")

if __name__ == '__main__':
    main()


