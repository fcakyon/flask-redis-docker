# project/server/main/views.py


from server.main.rq_helpers import queue, get_all_jobs
from server.main import jobs
from flask import render_template, Blueprint, jsonify, request, current_app, redirect

main_blueprint = Blueprint("main", __name__, template_folder='templates')


# endpoint for monitoring all job status
@main_blueprint.route("/", methods=["GET"])
def home():
    joblist = get_all_jobs()

    l = []
    # work on copy of joblist
    for job in list(joblist):
        l.append({
            'id': job.get_id(),
            'state': job.get_status(),
            'progress': job.meta.get('progress'),
            'result': job.result
            })

    return render_template('index.html', joblist=l)


# endpoint for adding job
@main_blueprint.route("/add_wait_job/<num_iterations>", methods=["GET"])
def run_wait_job_get(num_iterations):
    num_iterations = int(num_iterations)
    job = jobs.wait.delay(num_iterations)
    response_object = {
        "status": "success",
        "data": {
            "job_id": job.get_id()
        }
    }
    status_code = 200
    return redirect('/')


# endpoint for deleting a job
@main_blueprint.route('/delete_job/<job_id>', methods=["GET"])
def deletejob(job_id):
    # get job from connected redis queue
    job = queue.fetch_job(job_id)
    # delete job
    job.delete()
    # redirect to job list page
    return redirect('/')


# endpoint for getting a job
@main_blueprint.route("/jobs/<job_id>", methods=["GET"])
def get_status(job_id):
    # get job from connected redis queue
    job = queue.fetch_job(job_id)
    # process returned job and prepare response
    if job:
        response_object = {
            "status": "success",
            "data": {
                "job_id": job.get_id(),
                "job_status": job.get_status(),
                "job_result": job.result,
            },
        }
        status_code = 200
    else:
        response_object = {"message": "job not found"}
        status_code = 500
    return jsonify(response_object), status_code
