from sqlalchemy import create_engine, select, MetaData, and_, update
import os
import pandas as pd


class Database:
    TABLENAME = 'POP30310'

    def __init__(self,
                 server=os.environ['GP_HOST'],
                 database=os.environ['GP_DB'],
                 driver='ODBC Driver 17 for SQL Server'):
        self.server = server
        self.database = database
        self.driver = driver
        conn_string = (f"mssql+pyodbc://{os.environ['GP_USER']}:{os.environ['GP_PASS']}"
                       f"@{self.server}/{self.database}?driver={self.driver}")
        self.engine = create_engine(conn_string)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine, only=[self.TABLENAME])
        self.table = self.metadata.tables[self.TABLENAME]

    def get_bbd(self, receipt, item=None):
        query = select(self.table.c.POPRCTNM,
                       self.table.c.ITEMNMBR,
                       self.table.c.BOLPRONUMBER,
                       self.table.c.DEX_ROW_ID).filter(self.table.c.POPRCTNM.contains(f'{receipt}'))
        if item:
            query = query.filter(self.table.c.ITEMNMBR.contains(f'{item}'))
        df = pd.read_sql(query, self.engine)
        return df

    def change_bbd(self, new_bbd, dex_id : int):
        query = update(self.table).where(self.table.c.DEX_ROW_ID == dex_id).values(BOLPRONUMBER=new_bbd)
        with self.engine.begin() as conn:
            conn.execute(query)


db = Database()

if __name__ == "__main__":
    print(db.get_bbd('RCT070342', 'MOZZS'))
