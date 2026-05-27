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
    print(f"\n{'=' * 50}")
    print(f"Обработано успешно: {processed}")
    print(f"Обработано с ошибками: {errors}")
        # Вывод результатов на экран и в файл results.txt
    if analyzer.results:
        print('\nРЕЗУЛЬТАТЫ ПО ФАЙЛАМ:')
        for r in analyzer.results:
            if all(k in r for k in ['filename', 'orders_count','revenue']):
                print(f"  {r['filename']:20} | Заказов: {r['orders_count']:6} | Выручка: {r['revenue']:12.2f} | Средний чек: {r['avg_order_value']:8.2f}")
            else:
                print(f"Неполные данные в результате: {r}")
    else:
        print("\n Нет результатов для отображения")

    print("="*50)

if __name__ == '__main__':
    main()


