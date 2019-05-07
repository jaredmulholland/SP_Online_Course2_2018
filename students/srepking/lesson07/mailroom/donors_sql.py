import logging
from peewee import *
from create_mr_tables import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import create_mr_tables as new_database
#database = SqliteDatabase(None)
#d.database.init(file_name)
#database = SqliteDatabase('mailroom.db')
#database.connect()
#database.execute_sql('PRAGMA foreign_keys = ON;') # needed for sqlite only






class Group:
    """This Class will be used to query the database and return the results
    of the required queries."""

    def __init__(self, filename):
        new_database.database.init(filename)

    def search(self, search_for):
        database.connect()
        logger.info('Connected to database')
        database.execute_sql('PRAGMA foreign_keys = ON;')
        try:
            with database.transaction():
                logger.info(f'Searching through donors for {search_for}.')
                query = Donor.get_or_none(Donor.donor_name == search_for)  # Select all donors
        except Exception as e:
            logger.info(f'Error searching for donors.')
            logger.info(e)
            logger.info('Failed to execute donor search.')
        finally:
            logger.info('database closes')
            database.close()
        return query


    def print_donors(self):
        # This prints the list of donors
        database.connect()
        logger.info('Connected to database')
        database.execute_sql('PRAGMA foreign_keys = ON;')
        try:
            with database.transaction():
                logger.info('Trying print all the donors.')
                query = Donor.select()  #  Select all donors
                for donor in query:
                    print(donor.donor_name)

        except Exception as e:
            logger.info(f'Error printing donors.')
            logger.info(e)
            logger.info('Failed to print a list of donors.')
        finally:
            logger.info('database closes')
            database.close()

    def summary(self):
        """Create a new dictionary with Total, number of donations,
        and average donation amount"""

        donors_f = {some_name: [donor_obj.sum_donations(),
                                donor_obj.number_donations(),
                                donor_obj.avg_donations()]
                    for some_name, donor_obj in self._donor_raw.items()}
        return donors_f

    @staticmethod
    def column_name_width(donor_summary):
        name_list = list(donor_summary.keys())  # creates a list of keys
        name_wi = 11  # Establish minimum column width
        for i in name_list:
            if len(i) > name_wi:
                name_wi = (len(i))  # width of name column
        return name_wi

    @staticmethod
    def column_total_width(donor_summary):
        tot_wi = 12
        for name, summary in donor_summary.items():
            if len(str(summary[0])) > tot_wi:
                # width of total column
                tot_wi = (len(str(summary[0]))) + 3
                # width of number of donations column
        return tot_wi

    @staticmethod
    def column_average_width(donor_summary):
        ave_wi = 12
        for name, summary in donor_summary.items():
            if len(str(summary[2])) > ave_wi:
                # width of total column
                ave_wi = (len(str(summary[2]))) + 3
                # width of number of donations column
        return ave_wi

    @staticmethod
    def column_number_width(donor_summary):
        num_wi = 12
        for name, summary in donor_summary.items():
            if len(str(summary[1])) > num_wi:
                # width of total column
                num_wi = (len(str(summary[1]))) + 3
                # width of number of donations column
        return num_wi

    @staticmethod
    def sort_list(donor_summary):
        list_sorted = sorted(donor_summary,
                             key=donor_summary.__getitem__, reverse=True)
        return list_sorted

    def report(self):
        """Return a report on all the donors"""
        donor_summary = self.summary()
        name_wi = Group.column_name_width(donor_summary)
        tot_wi = Group.column_total_width(donor_summary)
        num_wi = Group.column_number_width(donor_summary)
        ave_wi = Group.column_average_width(donor_summary)

        list_sorted = Group.sort_list(donor_summary)

        rows = ['\n''A summary of your donors donations:',
                f"{'Donor Name':{name_wi}}| {'Total Given':^{tot_wi}}| "
                f"{'Num Gifts':^{num_wi}}| {'Average Gift':^{ave_wi}}",
                f"{'-':-^{(name_wi+tot_wi+ave_wi+num_wi+8)}}"]

        for key in list_sorted:
            temp = donor_summary[key]
            rows.append(f"{key:{name_wi}}${temp[0]:{tot_wi}.2f}"
                        f"{temp[1]:^{num_wi}}   "
                        f"${temp[2]:>{ave_wi}.2f}")

        return '\n'.join(rows)

    def letters(self):
        for donor, donor_obj in self._donor_raw.items():
            letter = f'Dear {donor}, thank you so much for your ' \
                     f'last contribution of ${donor_obj.last_donation():.2f}! ' \
                     f'You have contributed a total of $' \
                     f'{donor_obj.sum_donations():.2f}, ' \
                     f'and we appreciate your support!'
            # Write the letter to a destination
            with open(donor + '.txt', 'w') as to_file:
                to_file.write(letter)


class Individual:
    """Creates Class Individual, except instead of returning an instance
    of a class, we will now create a table 'Individual' in an SQL database
    with the following properties 'name', 'donation', '"""
    def __init__(self, filename):
        new_database.database.init(filename)
        #self.database = new_database.database
        #self.filename = filename

    @staticmethod
    def add_donation(person, contribution):
        #database = SqliteDatabase(self.filename)
        database.connect()
        logger.info('Connected to database')
        database.execute_sql('PRAGMA foreign_keys = ON;')

        try:
            with database.transaction():
                logger.info('Trying to add new donor.')
                new_donor = new_database.Donor.get_or_create(donor_name=person)
                #new_donor.save()
                logger.info(f'Success adding donor {person}.')

            with database.transaction():
                logger.info('Trying to add new donation.')
                new_donation = new_database.Donations.create(
                        donor_name=person,
                        donation=contribution)
                new_donation.save()
                logger.info(f'Database added a donation of '
                            f'{contribution} by {person}.')

                #query = Donations.select()
            #for donation in query:
                    #logger.info(f'{donation.donor_name} donated {donation.donation}')

        except Exception as e:
            logger.info(f'Error creating = {person}')
            logger.info(e)
            logger.info('Failed to add new donor.')
        finally:

            logger.info('database closes')
            database.close()

    def number_donations(self):
        return int(len(self.donations))

    def sum_donations(self):
        return sum(self.donations)

    def avg_donations(self):
        return self.sum_donations() / \
               self.number_donations()

    def last_donation(self):
        return self.donations[-1]

    @staticmethod
    def thank_you(person, contribution):
        """Add a donation to a donors records and print a report."""
        return ('Thank you so much for the generous gift of ${0:.2f}, {1}!'
                .format(contribution, person))


#database.create_tables([Donor, Donations])
#database.close()

