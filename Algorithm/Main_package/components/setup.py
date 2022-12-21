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
        self.__full_setup()
        schedule.every().monday.at("00:00").do(self.__full_setup)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def __full_setup(self):
        print('Full setup started!')
        self.elastic.clean()
        # amount = self.elastic.initial_import(MAX_FIELDS)
        amount = self.elastic.initial_import(2)
        print(f'HTML data (amount: {amount}) imported - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        new_name = self.modelator.initial_setup(amount)
        # new_name = self.modelator.initial_setup(1)
        print(f'Model created - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        self.modelator.helper.delete_indices(self.elastic,
                                             [constants.CLEAN_TEXTS, constants.SOURCE_TEXTS, constants.WORDS_PAIRS])
        self.modelator.helper.create_alias(self.elastic, constants.WORDS_PAIRS, new_name)
        print('Full setup finished!')
        print(self.elastic.show_index(constants.WORDS_PAIRS))
        return True


if __name__ == '__main__':
    SetUpper()
