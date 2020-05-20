from flask import Flask, redirect, render_template, request, url_for
import jobs
import rq

app = Flask(__name__)
jobs.rq.init_app(app)


# For sake of simplicty, we keep track of the jobs we've launched
# in memory. This will only work as long there is only one python
# process (web server context) and it must not get restarted.
# In advanced use cases you want to keep track of jobs by their ids
# and utilize sessions and redis.
joblist = []


@app.route('/')
def index():
    l = []
    # work on copy of joblist,
    for job in list(joblist):
        # task may be expired, refresh() will fail
        try:
            job.refresh()
        except rq.exceptions.NoSuchJobError:
            joblist.remove(job)
            continue

        l.append({
            'id': job.get_id(),
            'state': job.get_status(),
            'progress': job.meta.get('progress'),
            'result': job.result
            })

    return render_template('index.html', joblist=l)


@app.route('/enqueuejob', methods=['GET', 'POST'])
def enqueuejob():
    job = jobs.approximate_pi.queue(int(request.form['num_iterations']))
    joblist.append(job)
    return redirect('/')


@app.route('/deletejob', methods=['GET', 'POST'])
def deletejob():
    if request.args.get('jobid'):
        job = rq.job.Job.fetch(request.args.get('jobid'), connection=jobs.rq.connection)
        job.delete()
    return redirect('/')