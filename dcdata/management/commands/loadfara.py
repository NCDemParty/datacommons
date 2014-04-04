# -*- coding: utf-8 -*-


from dcdata.fara.models import ClientRegistrant, Contact, Contribution, \
    Disbursement, Payment
from dcdata.loading import Loader, LoaderEmitter
from dcdata.processor import chain_filters, load_data, Every, progress_tick
from dcdata.utils.dryrub import CSVFieldVerifier, VerifiedCSVSource
from dcdata.utils.sql import parse_int, parse_date, parse_decimal
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.fields import CharField
from optparse import make_option
from saucebrush.filters import FieldRemover, FieldAdder, Filter, FieldModifier,\
    FieldRenamer, FieldCopier
from saucebrush.emitters import DebugEmitter
import os
import sys
import traceback
import csv
from datetime import datetime


REPORT_FREQUENCY = 1000

class FARACSVDialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    escapechar = None
    doublequote = False
    skipinitialspace = False
    lineterminator = '\n'
    quoting = 0

def parse_fara_date(date_str):
    try:
        parse_date(date_str[0:10])
    except ValueError:
        if (date_str in ('None','None*')) or (not date_str):
            return None
        else:
            raise



def parse_fara_asterisk(date_str):
    return date_str[-1] == '*'


class UnicodeFilter(Filter):
    def __init__(self, method='replace'):
        self._method = method

    def process_record(self, record):
        for (key, value) in record.items():
            if isinstance(value, str):
                record[key] = value.decode('utf8', self._method).encode('utf8')
        return record


class StringLengthFilter(Filter):
    def __init__(self, model):
        self.model = model

    def process_record(self, record):
        for field in self.model._meta.fields:
            if isinstance(field, CharField) and field.name in record and record[field.name]:
                record[field.name] = record[field.name].strip()[:field.max_length]
        return record


class FARALoader(Loader):

    def __init__(self, *args, **kwargs):
        super(FARALoader, self).__init__(*args, **kwargs)

    def get_instance(self, record):
        registrant_id = record['registrant_id']
        # try:
        #             return Contribution.objects.get(transaction_namespace=namespace, transaction_id=key)
        #         except Contribution.DoesNotExist:
        #             return Contribution(transaction_namespace=namespace, transaction_id=key)
        return self.model(registrant_id=registrant_id)

    def resolve(self, record, obj):
        """ how should an existing record be updated?
        """
        self.copy_fields(record, obj)


class FARAClientRegistrantLoader(FARALoader):

    model = ClientRegistrant


def load_client_registrant(csvpath, *args, **options):
    loader = FARAClientRegistrantLoader(
        source='DOJ',
        description='load from denormalized CSVs',
        imported_by="loadfara.py (%s)" % os.getenv('LOGNAME', 'unknown'),
    )

    client_registrant_record_processor = chain_filters(
                        CSVFieldVerifier(),
                        #DebugEmitter(),
                        FieldRemover('id'),
                        FieldRemover('import_reference'),
                        FieldAdder('import_reference', loader.import_session),
                        FieldModifier(('client_id', 'registrant_id', 'location_id'), parse_int),
                        UnicodeFilter(),
                        StringLengthFilter(ClientRegistrant))

    output_func = chain_filters(
        LoaderEmitter(loader),
        Every(REPORT_FREQUENCY, progress_tick),
    )

    input_iterator = VerifiedCSVSource(open(os.path.abspath(csvpath)),
                                       fieldnames=ClientRegistrant.FIELDNAMES,
                                       skiprows=1)

    load_data(input_iterator, client_registrant_record_processor, output_func)


class FARAContactLoader(FARALoader):

    model = Contact


def load_contact(csvpath, *args, **options):
    loader = FARAContactLoader(
        source='DOJ',
        description='load from denormalized CSVs',
        imported_by="loadfara.py (%s)" % os.getenv('LOGNAME', 'unknown'),
    )

    contact_record_processor = chain_filters(
                        CSVFieldVerifier(),
                        FieldRemover('id'),
                        FieldRemover('import_reference'),
                        FieldAdder('import_reference', loader.import_session),
                        FieldCopier({'date_asterisk':'date'}),
                        FieldModifier('date', parse_fara_date),
                        FieldModifier('date_asterisk', parse_fara_asterisk),
                        FieldModifier(('document_id', 'record_id', 'recipient_id', 'client_id', 'registrant_id', 'location_id'), parse_int),
                        UnicodeFilter(),
                        StringLengthFilter(Contact))

    output_func = chain_filters(
        LoaderEmitter(loader),
        Every(REPORT_FREQUENCY, progress_tick),
    )

    input_iterator = VerifiedCSVSource(open(os.path.abspath(csvpath)),
                                       fieldnames=Contact.FIELDNAMES,
                                       skiprows=1)

    load_data(input_iterator, contact_record_processor, output_func)


class FARAContributionLoader(FARALoader):

    model = Contribution


def load_contribution(csvpath, *args, **options):
    loader = FARAContributionLoader(
        source='DOJ',
        description='load from denormalized CSVs',
        imported_by="loadfara.py (%s)" % os.getenv('LOGNAME', 'unknown'),
    )

    contribution_record_processor = chain_filters(
                        CSVFieldVerifier(),
                        FieldRemover('id'),
                        FieldRemover('import_reference'),
                        FieldAdder('import_reference', loader.import_session),
                        FieldCopier({'date_asterisk':'date'}),
                        FieldModifier('date', parse_fara_date),
                        FieldModifier('date_asterisk', parse_fara_asterisk),
                        FieldModifier('amount', parse_decimal),
                        FieldModifier(('document_id', 'recipient_id', 'registrant_id', 'record_id'), parse_int),
                        UnicodeFilter(),
                        StringLengthFilter(Contribution))

    output_func = chain_filters(
        LoaderEmitter(loader),
        Every(REPORT_FREQUENCY, progress_tick),
    )

    input_iterator = VerifiedCSVSource(open(os.path.abspath(csvpath)),
                                       fieldnames=Contribution.FIELDNAMES,
                                       skiprows=1, )

    load_data(input_iterator, contribution_record_processor, output_func)

class FARADisbursementLoader(FARALoader):

    model = Disbursement


def load_disbursement(csvpath, *args, **options):
    loader = FARADisbursementLoader(
        source='DOJ',
        description='load from denormalized CSVs',
        imported_by="loadfara.py (%s)" % os.getenv('LOGNAME', 'unknown'),
    )

    disbursement_record_processor = chain_filters(
                        CSVFieldVerifier(),
                        FieldRemover('id'),
                        FieldRemover('import_reference'),
                        FieldAdder('import_reference', loader.import_session),
                        FieldCopier({'date_asterisk':'date'}),
                        FieldModifier('date', parse_fara_date),
                        FieldModifier('date_asterisk', parse_fara_asterisk),
                        FieldModifier('amount', parse_decimal),
                        FieldModifier(('document_id', 'client_id', 'registrant_id', 'record_id','location_id', 'subcontractor_id'), parse_int),
                        UnicodeFilter(),
                        StringLengthFilter(Disbursement))

    output_func = chain_filters(
        LoaderEmitter(loader),
        Every(REPORT_FREQUENCY, progress_tick),
    )

    input_iterator = VerifiedCSVSource(open(os.path.abspath(csvpath)),
                                       fieldnames=Disbursement.FIELDNAMES,
                                       skiprows=1)

    load_data(input_iterator, disbursement_record_processor, output_func)


class FARAPaymentLoader(FARALoader):

    model = Payment


def load_payment(csvpath, *args, **options):
    loader = FARAPaymentLoader(
        source='DOJ',
        description='load from denormalized CSVs',
        imported_by="loadfara.py (%s)" % os.getenv('LOGNAME', 'unknown'),
    )

    payment_record_processor = chain_filters(
                        CSVFieldVerifier(),
                        FieldRemover('id'),
                        FieldRemover('import_reference'),
                        FieldAdder('import_reference', loader.import_session),
                        FieldCopier({'date_asterisk':'date'}),
                        FieldModifier('date', parse_fara_date),
                        FieldModifier('date_asterisk', parse_fara_asterisk),
                        FieldModifier('amount', parse_decimal),
                        FieldModifier(('document_id', 'client_id', 'registrant_id', 'record_id','location_id', 'subcontractor_id'), parse_int),
                        UnicodeFilter(),
                        StringLengthFilter(Payment))

    output_func = chain_filters(
        LoaderEmitter(loader),
        Every(REPORT_FREQUENCY, progress_tick),
    )

    input_iterator = VerifiedCSVSource(open(os.path.abspath(csvpath)),
                                       fieldnames=Payment.FIELDNAMES,
                                       skiprows=1)

    load_data(input_iterator, payment_record_processor, output_func)


class LoadFARA(BaseCommand):

    help = "load FARA data from csv"
    args = ""

    requires_model_validation = False

    @transaction.commit_manually
    #@transaction.commit_on_success
    def handle(self, fara_dir, *args, **options):
        if os.path.exists(fara_dir):
            FARA_DIR = fara_dir
        else:
            transaction.rollback()
            raise Exception('No directory at {d}'.format(d=fara_dir))

        try:
            sys.stdout.write("%s: processing client_registrant \n" % (datetime.now(),))
            load_client_registrant(os.path.join(FARA_DIR,'client_registrant.csv'), *args, **options)
            transaction.commit()

            sys.stdout.write("%s: processing contacts \n" % (datetime.now(),))
            load_contact(os.path.join(FARA_DIR,'contacts.csv'), *args, **options)
            transaction.commit()

            sys.stdout.write("%s: processing contributions \n" % (datetime.now(),))
            load_contribution(os.path.join(FARA_DIR,'contributions.csv'), *args, **options)
            transaction.commit()

            sys.stdout.write("%s: processing disbursements \n" % (datetime.now(),))
            load_disbursement(os.path.join(FARA_DIR,'disbursements.csv'), *args, **options)
            transaction.commit()

            sys.stdout.write("%s: processing payments \n" % (datetime.now(),))
            load_payment(os.path.join(FARA_DIR,'payments.csv'), *args, **options)
            transaction.commit()
        except KeyboardInterrupt:
            traceback.print_exception(*sys.exc_info())
            transaction.rollback()
            raise
        except:
            traceback.print_exception(*sys.exc_info())
            transaction.rollback()
            raise
        finally:
            sys.stdout.flush()
            sys.stderr.flush()


Command = LoadFARA