import logging
import uuid
import json
import time
from contextlib import contextmanager
from tests_integration.lib.pipelines import pipeline
from tests_integration.lib.exceptions import KDIsNotSane
from tests_integration.lib.load_testing_utils import check_sanity

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

STATISTIC_FAKE_PODS_COUNT = 1000
STATISTIC_COLLECTION_PERIOD = 60
SANITY_CHECK_TIMEOUT = 2


INFLUXDB_URL = "http://127.0.0.1:8086"


def influxdb_query(cluster, q):
    cmd = ('curl -sG --fail {0}  --data-urlencode "q={1}"'
           ' --data-urlencode "db=k8s"').format(
        INFLUXDB_URL + '/query', q)
    _, result_raw, _ = cluster.ssh_exec("master", cmd)
    return result_raw


def collect_statistic_data(pod):
    """ Do some work on PA and get statistic produced
    by this period
    """
    # Collect data
    query = "select * from /.*/ where time > now() - {0:.0f}s and time <= now()".format(
        STATISTIC_COLLECTION_PERIOD
    )
    result_raw = influxdb_query(pod.cluster, query)
    result = json.loads(result_raw)['results'][0]['series']
    data = []
    for rec in result:
        values = dict((k, v) for k, v in
                      zip(rec['columns'], rec['values'][0]) if v is not None)
        data.append({
            "name": rec['name'],
            "timestamp": values.pop('time'),
            "value": values.pop('value'),
            "data": values
        })
    return data


@contextmanager
def loglevel(level):
    logger = logging.getLogger()
    original_loglevel = logger.getEffectiveLevel()
    logging.getLogger().setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(original_loglevel)


def write_statistic_data(cluster, pod_id, data):
    records = []
    for rec in data:
        rec['data']['pod_id'] = pod_id
        raw_data = ','.join('{0}={1}'.format(k, v.replace(",", "\\,"))
                            for k, v in rec['data'].items())
        records.append('{0},{1} value={2} {3}'.format(
            rec['name'], raw_data, rec['value'], int(time.time())))
    url = "{0}/write?db=k8s".format(INFLUXDB_URL)
    cmd = "curl --fail -is -XPOST '{0}' --data-binary '{1}'".format(
        url, '\n'.join(records))
    with loglevel(logging.INFO):
        _, result_raw, _ = cluster.ssh_exec("master", cmd)


def influx_fake_pod():
    """ TODO: It should create some initial data for pod.
    Or may be not.
    """
    return str(uuid.uuid4())


def check_recovery(cluster, pods):
    """ Wait until KD back from overload.
    """
    time.sleep(3)  # Get some rest after overload.
    # We will wait for a one minute.
    wait_time = 60
    wait_stop = time.time() + wait_time
    while wait_stop > time.time():
        try:
            check_sanity(cluster, pods)
            LOG.info("KD is up now. It took "
                     "{}s to recover.".format(wait_time - time.time()))
            # KD is sane so we can go further
            return
        except KDIsNotSane:
            pass
    raise KDIsNotSane("Kuberdock does not return from down in 60 seconds.")


@pipeline("stress_testing")
def test_statistic_stress(cluster):
    LOG.debug("Create wordpress PA")
    description = ("Each iteration is an amount of statistics generated by "
                   "POST request to {} different wordpress pods.").format(
                       STATISTIC_FAKE_PODS_COUNT)
    pod = cluster.pods.create_pa('wordpress.yaml', wait_ports=True,
                                 wait_for_status='running',
                                 healthcheck=True)
    LOG.debug("Do some load on wordpress")
    pod.gen_workload(STATISTIC_COLLECTION_PERIOD)
    LOG.debug("Collect statistic for later usage")
    statistic = collect_statistic_data(pod)
    fake_pods = [influx_fake_pod() for i in range(STATISTIC_FAKE_PODS_COUNT)]
    check_sanity(cluster, [pod, ])

    # Maximum duration of stress test is 1 hour
    wait_time = 60 * 60
    wait_stop = time.time() + wait_time
    iterations = 0

    try:
        while time.time() < wait_stop:
            LOG.debug("Generating statiscs for {0} pods.".format(
                STATISTIC_FAKE_PODS_COUNT))
            for fake in fake_pods:
                write_statistic_data(pod.cluster, fake, statistic)
            LOG.debug("Checking cluster API sanity")
            check_sanity(cluster, [pod, ])
            iterations += 1
    except KDIsNotSane:
        LOG.info("It took {0} iterations to degrade performance. {1}".format(
            iterations, description))
        check_recovery(cluster, [pod, ])
        LOG.debug("KD is up now.")
    LOG.info("{0} iterations passed sucessfully. {1} "
             "KD API (including statistics) response have been under 2 seconds"
             " all this time.".format(iterations, description))
