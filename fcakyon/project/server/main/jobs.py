# project/server/main/tasks.py


from rq.decorators import job
from rq import get_current_job
from server.main.rq_helpers import redis_connection
import time


# the timeout parameter specifies how long a job may take
# to execute before it is aborted and regardes as failed
# the result_ttl parameter specifies how long (in seconds)
# successful jobs and their results are kept.
# for more detail: https://python-rq.org/docs/jobs/
@job('default', connection=redis_connection, timeout=90, result_ttl=7*24*60*60)
def wait(num_iterations):
    """
    wait for num_iterations seconds
    """
    # get a reference to the job we are currently in
    # to send back status reports
    self_job = get_current_job()

    # define job
    for i in range(1, num_iterations + 1):  # start from 1 to get round numbers in the progress information
        time.sleep(1)
        self_job.meta['progress'] = {
            'num_iterations': num_iterations,
            'iteration': i,
            'percent': i / num_iterations * 100
        }
        # save meta information to queue
        self_job.save_meta()

    # return job result (can be accesed as job.result)
    return num_iterations
