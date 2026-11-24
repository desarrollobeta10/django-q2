import uuid
from multiprocessing import Event
from unittest import mock

import pytest
from django.core.management import call_command
from django.db import DatabaseError

from django_q import utils
from django_q.cluster import Sentinel
from django_q.scheduler import scheduler

KILLED = DatabaseError("DPY-4011: the database or network closed the connection")


class KilledConnection:
    alias = "default"

    def __init__(self):
        self.connection = object()

    def _discard_and_raise(self):
        self.connection = None
        raise KILLED

    def close(self):
        self._discard_and_raise()

    def close_if_unusable_or_obsolete(self):
        self._discard_and_raise()


@pytest.fixture
def killed_connection():
    conn = KilledConnection()
    with mock.patch("django.db.connections.all", return_value=[conn]):
        yield conn


@pytest.mark.parametrize("only_old", [True, False])
def test_close_django_connections_discards_killed_connection(killed_connection, only_old):
    with mock.patch("django_q.utils.logger") as logger:
        utils.close_django_connections(only_old=only_old)

    assert killed_connection.connection is None
    logger.warning.assert_called_once()


def test_reincarnate_survives_killed_connection(killed_connection):
    sentinel = Sentinel(Event(), Event(), uuid.uuid4(), broker=mock.MagicMock(), start=False)
    dead_pusher = mock.MagicMock()
    sentinel.pusher = dead_pusher
    sentinel.monitor = mock.MagicMock()

    with mock.patch.object(Sentinel, "spawn_pusher", return_value="new pusher") as spawn:
        sentinel.reincarnate(dead_pusher)

    spawn.assert_called_once()
    assert sentinel.pusher == "new pusher"


def test_spawn_cluster_survives_killed_connection(killed_connection):
    sentinel = Sentinel(Event(), Event(), uuid.uuid4(), broker=mock.MagicMock(), start=False)

    with mock.patch.object(Sentinel, "spawn_worker"), mock.patch.object(
        Sentinel, "spawn_monitor"
    ), mock.patch.object(Sentinel, "spawn_pusher", return_value="pusher"):
        sentinel.spawn_cluster()

    assert sentinel.pusher == "pusher"


@pytest.mark.django_db
def test_scheduler_survives_killed_connection(killed_connection):
    scheduler(broker=mock.MagicMock())


@pytest.mark.django_db(transaction=True)
def test_orm_broker_survives_killed_connection(killed_connection):
    from django_q.brokers.orm import ORM

    ORM.get_connection()


def _fake_cluster(exitcode, stop_requested):
    cluster = mock.MagicMock()
    cluster.sentinel.exitcode = exitcode

    def start():
        cluster.stop_event = Event()
        if stop_requested:
            cluster.stop_event.set()

    cluster.start.side_effect = start
    return cluster


def test_qcluster_exits_with_error_when_sentinel_dies():
    cluster = _fake_cluster(exitcode=1, stop_requested=False)
    with mock.patch("django_q.management.commands.qcluster.Cluster", return_value=cluster):
        with pytest.raises(SystemExit) as exc:
            call_command("qcluster")

    assert exc.value.code == 1
    cluster.sentinel.join.assert_called_once()


def test_qcluster_exits_with_error_when_sentinel_ends_without_stop():
    cluster = _fake_cluster(exitcode=0, stop_requested=False)
    with mock.patch("django_q.management.commands.qcluster.Cluster", return_value=cluster):
        with pytest.raises(SystemExit) as exc:
            call_command("qcluster")

    assert exc.value.code == 1


def test_qcluster_exits_cleanly_after_requested_stop():
    cluster = _fake_cluster(exitcode=0, stop_requested=True)
    with mock.patch("django_q.management.commands.qcluster.Cluster", return_value=cluster):
        call_command("qcluster")

    cluster.sentinel.join.assert_called_once()


def test_qcluster_run_once_does_not_wait_for_sentinel():
    cluster = _fake_cluster(exitcode=0, stop_requested=False)
    with mock.patch("django_q.management.commands.qcluster.Cluster", return_value=cluster):
        call_command("qcluster", "--run-once")

    cluster.stop.assert_called_once()
    cluster.sentinel.join.assert_not_called()
