from database.create_stock_tables import create_stock_info_table
from service.insert_stock_info import insert_or_update_stock_info

def run_init():
    print(" 初始化開始...\n")

    print(" 建立資料表...")
    create_stock_info_table()

    print(" 同步上市/上櫃公司資料...")
    insert_or_update_stock_info()

    print("\n 所有初始化程序完成！")

if __name__ == "__main__":
    run_init()
