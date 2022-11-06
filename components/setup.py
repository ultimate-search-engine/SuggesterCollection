from components.management import Management
from components.modelating import Modelator
from datetime import datetime
import time
import schedule


class SetUpper:
    elastic = Management()
    modelator = Modelator()

    def __init__(self):
        self.__full_setup()
        schedule.every().monday.at("00:00").do(self.__full_setup)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def __full_setup(self):
        print('Full setup started!')
        self.elastic.clean()
        self.elastic.initial_import()
        print(f'Dump imported - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        self.modelator.initial_setup()
        print(f'Model created - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        self.elastic.delete_index('texts')
        self.elastic.delete_index('sites')
        print('Full setup finished!')
        print(self.elastic.show_index('words_pairs'))
        return True
