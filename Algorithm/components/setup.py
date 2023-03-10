from decouple import config
from components.management import Management
from components.modelating import Modelator
import components.features.constants as constants
from datetime import datetime
import time
import schedule
MAX_FIELDS = int(config('LIMIT'))


class SetUpper:
    elastic = Management()
    modelator = Modelator()

    def __init__(self):
        self.__setup()
        schedule.every().monday.at("00:00").do(self.__setup)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def __setup(self):
        print('Full setup started!')
        self.__run()
        print('Full setup finished!')
        print(self.elastic.show_index(constants.WORDS_PAIRS))
        return True

    def __run(self):
        amount = self.__import_data()  # 1. Import data
        new_name = self.__run_model(amount)  # 2. Run model
        self.__clean_elastic(new_name)  # 3. Clean elastic

    def __import_data(self):
        self.elastic.clean()
        amount = self.elastic.initial_import(MAX_FIELDS)
        print(f'HTML data (amount: {amount}) imported - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        return amount

    def __run_model(self, amount: int):
        new_name = self.modelator.initial_setup(amount)
        print(f'Model created - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        return new_name

    def __clean_elastic(self, name: str):
        self.modelator.helper.delete_indices(self.elastic,
                                             [constants.CLEAN_TEXTS, constants.WORDS_PAIRS])
        self.modelator.helper.create_alias(self.elastic, constants.WORDS_PAIRS, name)
        pass


if __name__ == '__main__':
    SetUpper()
