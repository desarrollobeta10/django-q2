import os
import sys

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from django_q.cluster import Cluster
from django_q.conf import logger


class Command(BaseCommand):
    # Translators: help text for qcluster management command
    help = _("Starts a Django Q Cluster.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--run-once",
            action="store_true",
            dest="run_once",
            default=False,
            help="Run once and then stop.",
        )
        parser.add_argument(
            "-n",
            "--name",
            dest="cluster_name",
            default=None,
            help="Set alternative cluster name instead of the name in Q_CLUSTER settings (for multi-queue setup). "
            "On Linux you should set name through `Q_CLUSTER_NAME=cluster_name python manage.py qcluster` instead.",
        )

    def handle(self, *args, **options):
        # Set alternative cluster_name before creating the cluster (cluster_name is broker's queue_name, too)
        cluster_name = options.get("cluster_name")
        if cluster_name:
            os.environ["Q_CLUSTER_NAME"] = cluster_name

        q = Cluster()
        q.start()
        if options.get("run_once", False):
            q.stop()
            return
        q.sentinel.join()
        stop_requested = q.stop_event is None or q.stop_event.is_set()
        if q.sentinel.exitcode != 0 or not stop_requested:
            logger.critical(
                _("Sentinel stopped unexpectedly with exit code %(code)s")
                % {"code": q.sentinel.exitcode}
            )
            sys.exit(1)
