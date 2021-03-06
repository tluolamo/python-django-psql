from __future__ import absolute_import, unicode_literals

import csv
import os
from collections import defaultdict
from io import StringIO

from celery import shared_task
from django.apps import apps

from ..settings import BASE_DIR


@shared_task
def load_data(file):
    """This will take a filepath from the base of the project to process into
    the DB. It should look something like upload/somefile"""
    from .models import Member

    member_fields = [str(f).split(".")[2] for f in Member._meta.get_fields()]
    member_fields.remove("id")
    file = os.path.join(BASE_DIR, file)

    with open(file, "rb") as csv_file:
        csvf = StringIO(csv_file.read().decode())
        bulk_mgr = BulkCreateManager(chunk_size=1000)
        for row in csv.DictReader(csvf, delimiter=","):
            for k in [*row]:
                if k not in member_fields:
                    del row[k]

            bulk_mgr.add(Member(**row))
        bulk_mgr.done()
    os.remove(file)


class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(
            self._create_queues[model_key], ignore_conflicts=True
        )
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))
