from __future__ import division
import json
from flask import render_template, flash, redirect, session, url_for, request, g, Blueprint
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm
from models import user_results, task_run, research_results, task, app_results
from math import sqrt

blueprint = Blueprint('app', __name__)

indexAux = 1

@app.before_request
def before_request():
    g.user = current_user
    
@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
def index():
    applications = g.user.applications_participating().all()
    if len(applications)<1:
        return render_template('not_app.html'), 401
    elif len(applications)==1:
        #Get the results for a task
        app_name = applications[0].get_name()
        return redirect(url_for('filterResults', app_name=app_name))
    return render_template("index.html",
        title = 'Ibercivis',
        applications = applications)
          
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():

    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

@lm.user_loader
def load_user(id):
    return user_results.query.get(int(id))
    
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    
    user = user_results.query.filter_by(email = resp.email).first()
    
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = user_results(nickname = nickname, email = resp.email)
        db.session.add(user)
        db.session.commit()
                
    remember_me = False    
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)

    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
    
@app.route('/resultsApp', methods = ['GET', 'POST'])
@login_required
def resultsApp():
    app_name = request.form['app_select']
    return redirect(url_for('filterResults', app_name=app_name))

@app.route('/filterResults/<app_name>', methods = ['GET', 'POST'])
@login_required
def filterResults(app_name):
    user = g.user
    #Get the results for a task
    #results = task_run.query.join(app_results, (app_results.id == task_run.app_id)).filter(app_results.name == app_param)
    results_filtered = []
    results = task.query.join(app_results, (app_results.id == task.app_id)).filter(app_results.name == app_name)
    
    #Check the list is not empty
    try:
        app_id = int(results[0].get_app_id())
    except: 
        return render_template('not_app.html'), 401
        
    #Check the user has actually access to that application
    applicationsParticipating = user.applications_participating()
    permission = False
    for appPart in applicationsParticipating:
        if int(results[0].get_app_id()) == int(appPart.get_id()):
            permission = True
            break
    if permission == False:
        render_template('permissionDenied.html'), 402
    
    #Filter the results obtained according to the application at hand
    if int(results[0].get_app_id()) == 421:
        #Cell Images Application
        for result in results:
            auxJson = json.loads(result.info)
            taskName = -1
            try: taskName = auxJson["link"]
            except: pass
            if taskName != -1:
                taskName = taskName[taskName.rfind("/")+1:]
                taskName = taskName[:taskName.rfind("-")]
                found = False
                for result_aux in results_filtered:
                    if result_aux[0]==taskName:
                        found = True
                        break
                if found == False:
                    results_filtered.append([taskName, result.get_id()])
    elif int(results[0].get_app_id()) == 418:
        #Semantics Map Application
        for result in results:
            auxJson = json.loads(result.info)
            taskName = -1
            try: 
                taskName = auxJson["startWord"] + "-" + auxJson["endWord"]
            except: pass
            if taskName != -1:
                results_filtered.append([taskName, result.get_id()])
    return render_template("results_page.html",
            title = 'Ibercivis',
            app_name = app_name,
            results = results_filtered,
            results_length = len(results_filtered))

@app.route('/taskResultsApp/<app_name>/<task_id>/<task_name>', methods = ['GET', 'POST'])
@login_required
def taskResultsApp(app_name, task_id, task_name):
    user = g.user
    
    #Get the task_runs for that task_id
    if app_name == "Cells Images":
        taskResults = task_run.query.filter(task_run.info.like("%"+task_name+"%"))
    else:
        taskResults = task_run.query.filter(task_run.task_id == task_id)
    
    #Check the list is not empty
    try:
        app_id = int(taskResults[0].get_app_id())
    except: 
        return render_template('not_app.html'), 401
    
    #Check the user has actually access to that application
    applicationsParticipating = user.applications_participating()
    permission = False
    for appPart in applicationsParticipating:
        if app_id == int(appPart.get_id()):
            permission = True
            break
    if permission == False:
        render_template('permissionDenied.html'), 402
    
    if app_id == 421:
        #Cell Images Application
        r = input_for_graph_cells (taskResults)
        return render_template("graphs_page.html",
            title = 'Ibercivis',
            app_name = app_name,
            app_id = app_id,
            task_name = task_name,
            dataAverageAlive = r["dataAverageAlive"],
            dataDeviationAlive = r["dataDeviationAlive"],
            dataAverageDead = r["dataAverageDead"],
            dataDeviationDead = r["dataDeviationDead"],
            dataAverageDontKnow = r["dataAverageDontKnow"],
            dataDeviationDontKnow = r["dataDeviationDontKnow"],
            dataAverageElongated = r["dataAverageElongated"],
            dataDeviationElongated = r["dataDeviationElongated"],
            dataAverageRounded = r["dataAverageRounded"],
            dataDeviationRounded = r["dataDeviationRounded"],
            dataAverageStar = r["dataAverageStar"],
            dataDeviationStar = r["dataDeviationStar"],
            dataAverageRelease = r["dataAverageRelease"],
            dataDeviationRelease = r["dataDeviationRelease"],
            dataAverageClustered = r["dataAverageClustered"],
            dataDeviationClustered = r["dataDeviationClustered"],
            dataAverageScattered = r["dataAverageScattered"],
            dataDeviationScattered = r["dataDeviationScattered"],
            dataAverageDistributionDontKnow = r["dataAverageDistributionDontKnow"],
            dataDeviationDistributionDontKnow = r["dataDeviationDistributionDontKnow"],
            remarks = r["remarks"],
            results_length = 49)

    elif app_id == 418:
        #Semantics Map Application
        statistics_semantics_dump = input_for_statistics_semantics (taskResults, task_name)
        return render_template("graphs_page.html",
            title = 'Ibercivis',
            app_name = app_name,
            app_id=app_id,
            task_name = task_name,
            statistics_semantics_dump = statistics_semantics_dump)

@blueprint.route('/<int:task_id>/results<task_id>.json')
@login_required
def export_task(app_name, task_id):
    #Return a file with all the TaskRuns for task_id of the application app_name
    taskResults = db.session.query(task_run).filter(task_run.task_id == task_id)

    results = [tr.dictize() for tr in taskResults]
    return Response(json.dumps(results), mimetype='application/json')

def input_for_graph_cells (taskResults):

    #Create the necessary structures
    r = {"dataAverageAlive": [], "dataAverageDead": [], "dataAverageDontKnow" : [], "dataDeviationAlive": [], "dataDeviationDead" : [], "dataDeviationDontKnow" : [], "dataAverageElongated" : [], "dataDeviationElongated" : [], "dataAverageRounded" : [], "dataDeviationRounded" : [], "dataAverageStar" : [], "dataDeviationStar" : [], "dataAverageRelease" : [], "dataDeviationRelease" : [], "dataAverageClustered" : [], "dataDeviationClustered" : [], "dataAverageScattered" : [], "dataDeviationScattered" : [], "dataAverageDistributionDontKnow" : [], "dataDeviationDistributionDontKnow" : [], "remarks" : []}
    taskResultsList = []
    filterResults = []
    indexAux = 1
    
    #Go through the task_runs to get results out of the JSON and embed them in a list
    for result in taskResults:
        #Get and decode the JSON field
        auxJson = json.loads(result.info)
        taskName = -1
        try: taskName = auxJson["task"]
        except: pass
        taskName = taskName[taskName.rfind("/")+1:]
        taskName = taskName[taskName.rfind("-")+1:]
        try: 
            cellsAlive = int(auxJson["cells_alive"])
        except: 
            cellsAlive = 0
        try: 
            cellsDead = int(auxJson["cells_dead"])
        except: 
            cellsDead = 0
        try: 
            cellsDontKnow = int(auxJson["cells_dont_know"])
        except: 
            cellsDontKnow = 0
        try: 
            cellsElongated = int(auxJson["cellular_shape_elongated"])
        except: 
            cellsElongated = 0
        try: 
            cellsRounded = int(auxJson["cellular_shape_rounded"])
        except: 
            cellsRounded = 0
        try: 
            cellsStar = int(auxJson["mitocohondria_distribution_notsure"])
        except: 
            cellsStar = 0
        try: 
            cellsRelease = int(auxJson["release_yes"])
        except: 
            cellsRelease = 0
        try: 
            cellsGrouped = int(auxJson["mitocohondria_grouped"])
        except: 
            cellsGrouped = 0
        try: 
            cellsScattered = int(auxJson["mitocohondria_scattered"])
        except: 
            cellsScattered = 0
        try: 
            cellsDistributionDontKnow = int(auxJson["mitocohondria_distribution_notsure"])
        except: 
            cellsDistributionDontKnow = 0
        try:
            remark = auxJson["remarks"]
            if remark!= "":
                remark = "Time "+taskName+": "+remark
                r["remarks"].append(remark)
        except:
            remark = ""
            
        taskResultsList.append([int(taskName), cellsAlive, cellsDead, cellsDontKnow, cellsElongated, cellsRounded, cellsStar, cellsRelease, cellsGrouped, cellsScattered, cellsDistributionDontKnow])
    
    global indexAux        
    for j in range(1,50):
        indexAux = j
        filterResults.append(reduce(add, filter(f, taskResultsList),[0,0,0,0,0,0,0,0,0,0,0,0]))

    finalResults = map(average,filterResults)
    
    for i in finalResults:
        r["dataAverageAlive"].append(i[1])
        r["dataAverageDead"].append(i[2])
        r["dataAverageDontKnow"].append(i[3])
        r["dataAverageElongated"].append(i[4])
        r["dataAverageRounded"].append(i[5])
        r["dataAverageStar"].append(i[6])
        r["dataAverageRelease"].append(i[7])
        r["dataAverageClustered"].append(i[8])
        r["dataAverageScattered"].append(i[9])
        r["dataAverageDistributionDontKnow"].append(i[10])
            
    filterResultsDeviation = []
    
    for j in range(1,50):
        indexAux = j
        auxTaskResultsListFiltered = filter(f, taskResultsList)
        auxFinalResultsFiltered = filter(f, finalResults)
        out = [indexAux,0,0,0,0,0,0,0,0,0,0,0]
        if auxFinalResultsFiltered != []:
            for taskResultItem in auxTaskResultsListFiltered:
                out[len(out)-1] = out[len(out)-1] + 1
                for i in range(1,len(taskResultItem)):
                    out[i]=out[i]+(taskResultItem[i]-auxFinalResultsFiltered[0][i])**2
        filterResultsDeviation.append(out)

    finalResultsDeviation = map(standardDeviation,filterResultsDeviation)
    
    for i in finalResultsDeviation:
        r["dataDeviationAlive"].append(i[1])
        r["dataDeviationDead"].append(i[2])
        r["dataDeviationDontKnow"].append(i[3])
        r["dataDeviationElongated"].append(i[4])
        r["dataDeviationRounded"].append(i[5])
        r["dataDeviationStar"].append(i[6])
        r["dataDeviationRelease"].append(i[7])
        r["dataDeviationClustered"].append(i[8])
        r["dataDeviationScattered"].append(i[9])
        r["dataDeviationDistributionDontKnow"].append(i[10])
        
    return r
    
def f(x): 
    global indexAux
    return x[0] == indexAux

def add(x,y):  
    out = [y[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, x[len(x)-1]+1]
    for i in range(1,len(y)):
	    out[i]=x[i]+y[i]
    return out

def average(x):
    total = x[len(x)-1]
    if total == 0:
        return [x[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        return [x[0], float(x[1]/total), float(x[2]/total), float(x[3]/total), float(x[4]/total), float(x[5]/total), float(x[6]/total), float(x[7]/total), float(x[8]/total), float(x[9]/total), float(x[10]/total)]

def standardDeviation(x):
    total = x[len(x)-1]
    if total == 0:
        return [x[0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        return [x[0], sqrt(float(x[1]/total)), sqrt(float(x[2]/total)), sqrt(float(x[3]/total)), sqrt(float(x[4]/total)), sqrt(float(x[5]/total)), sqrt(float(x[6]/total)), sqrt(float(x[7]/total)), sqrt(float(x[8]/total)), sqrt(float(x[9]/total)), sqrt(float(x[10]/total))]

def input_for_statistics_semantics (taskResults, task_name):

    #results_dump contain the dump of the results
    results_dump = "Task "+task_name+"\n"
    i = 1
    
    #Go through the task_runs to get results out of the JSON and embed them in a list
    for result in taskResults:
        results_dump = results_dump+"\nReplica "+str(i)+":\n\n"
        i = i + 1
        
        #Get and decode the JSON field
        auxJson = json.loads(result.info)
        
        pathArray = auxJson.split("~")
        
        #Spaces per cell = 15
        time = " Time  |       0       |"
        path = " Path  |"
        for itemPathArray in pathArray:
            aux = -1
            try:
                aux = int(itemPathArray)
            except:
                #It is not a number
                aux = -1
            if aux == -1:
                if (itemPathArray == "NaN"):
                    time = time + "      NaN      |"
                else:
                    whiteSpaces = int((15-len(itemPathArray))/2)
                    for j in range(whiteSpaces):
                        path = path + " "
                    path = path + itemPathArray
                    for j in range(whiteSpaces):
                        path = path + " "
                    if (((15-len(itemPathArray))/2)%2) != 0:
                        path = path + " "
                    path = path + "|"
            else:
                if aux > 9:
                    time = time + "      "+str(aux)+"       |"
                else:
                    time = time + "       "+str(aux)+"       |"
        
        results_dump = results_dump + time + "\n" + path + "\n\n"
        
    return results_dump

