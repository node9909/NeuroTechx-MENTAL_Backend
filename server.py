from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
# from graphing import *
from pprint import pprint
# from bci_workshop_tools import *
# from DeepEEG import getState
from subprocess import Popen, PIPE, STDOUT, call, check_call
import json, time, sys
# import user
import os

app = Flask(__name__)
person_name = ""
first_recording = True
attentive = 0
time_interval = ""
counter = 0
CORS(app)
@app.route('/')
def hello():
    return "Welcome to the local server"

@app.route('/login', methods=['POST'])
def login():
    temp = request.get_json()
    # TODO: create a file 
    global person_name 
    person_name = temp['name']
    return jsonify({"name" : person_name})

@app.route('/start', methods=['POST'])
def start(sub_sample_duration=0):
    temp = request.get_json()
    attentive_state = temp['attentive']
    # attentive_state will be true / false / focus
    duration_value = "15" # for the demo it is for training
    if attentive_state is "focus":
        duration_value = sub_sample_duration
    # attentive_state will be true / false 
    if attentive_state is "true":
        attentive_state = "attentive"
    elif attentive_state is "false":
        attentive_state = ""

    # fileName = 'data/'
    # if "true" in attentive_state:
    #     fileName = os.join(fileName,'attentive/%s'%person_name)
    # elif "false" in attentive_state:
    #     fileName = os.join(fileName,'inattentive/%s'%person_name)
    # elif "focus" in attentive_state:
    #     fileName = os.join(fileName,'%s/'%person_name)
    
    

    global person_name
    dummy = "-p /dev/tty.usbserial-DB00J8RE --add abhi person " + person_name +" " +attentive_state + " duration " + duration_value
   
    # dummy = "-p /dev/tty.usbserial-DB00J8RE --add abhi person Jake window_size 1 recording_session_number 12 attentive"
    # args_list = dummy.split(" ")
    # p = Popen(["python", "user.py"] + args_list, stdin=PIPE, stdout=PIPE)
    # time.sleep(20)
    # pid = p.pid
    call(["./start.sh", dummy])
    # out, err = p.communicate(input=b'/start')
    
    global counter 
    pprint("counter is " + str(counter))
    counter +=1

    # p = Popen(["./start.sh"])
    '''
    temp = "python user.py -p /dev/tty.usbserial-DB00J8RE --add abhi person Jake window_size 1 recording_session_number 12 attentive"
    p = Popen(temp.split(" "))
    board = user.giveBoard()
    '''
    # rc = p.poll()
    return "Initializing"

@app.route('/triggerTraining')
def triggerTraining():
    call(["python","DeepEEG.py"])
    return "Done running"

@app.route('/startFocus', methods=['POST'])
def startFocus():
    '''
    loop to call /start
      if elapsed time less than duration time 
      call start , "focus"
      if first_recording
        callEEG
        first_recording =  False 
      '''
    global first_recording
    temp = request.get_json()
    focus_duration = temp['focus_duration'] # 30 seconds for the demo
    sub_sample_duration = 5 
    time_elapsed = 0
    while(time_elapsed<focus_duration):
        time_elapsed += sub_sample_duration
        redirect(url_for('start'), code=307)
        if first_recording:
            callEEG(sub_sample_duration, focus_duration)
            first_recording = False
    return ""

@app.route('/endFocus')
def endFocus():
    return ""

@app.route('/data', methods=['POST'])
def data():
    x = request.form['sample_number']
    ys = request.form['channel_values']
    delay = request.form['delay']
    li = []
    for y in ys:
        li.append({"x" : x, 'y' : y})
    process(8, li, delay)
    return ""

@app.route('/lineGraphData')
def lineGraphData():
    temp = { "data": [{ "label": "apples", "data": [12, 19, 3, 17, 6, 3, 7,1,1,1], "backgroundColor": "rgba(153,255,51,0.4)" }, { "label": "oranges", "data": [2, 29, 5, 5, 2, 3, 10,2,2,2], "backgroundColor": "rgba(400,153,0,0.4)" }, { "label": "banana", "data": [12, 19, 3, 17, 6, 3, 7,3,3,3], "backgroundColor": "rgba(153,255,51,0.4)" }, { "label": "pineapple", "data": [12, 19, 3, 17, 6, 3, 7,4,4,4], "backgroundColor": "rgba(500,255,51,0.4)" }, { "label": "hello", "data": [12, 19, 3, 17, 6, 3, 7,5,5,5], "backgroundColor": "rgba(153,255,51,0.4)" }] }
    return jsonify(temp)

@app.route('/punchCard')
def punchCard():
    # temp = {"session_start_time" : "Monday", "values": "0.3,0.1,0.2,0.7,0.4,0.6,0.33,0.9,0.8,0.1"}
    # with open(person_name+)
    temp = {"result" : "true"}
    return jsonify(temp)

@app.route('/end')
def end():

    return "Stop executed"

@app.route('/polling')
def testjson():
    # attentive has a 0 or 1 
    return jsonify({"result" : attentive })

@app.route('/registerPerson', methods=['POST'])
def registerPerson():
    temp = request.get_json()
    global time_interval
    time_interval = temp['time_interval']
    return jsonify({"name" : person_name, "time_interval" : time_interval})

def callEEG(sub_sample_duration, focus_duration):
    # person_full_name, time_interval between samples
    global person_name
    getState(person_name, sub_sample_duration, focus_duration)
    return "done"

@app.route('/readFile')
def test():
    
    history = []
    global person_name
    with open("./data/"+person_name+"/History.txt") as f:
        for line in f:
            lst = line.split("|")
            timestamp = lst[0]
            time_interval = lst[1]
            brainStates = list(lst[2])
            history.append({"timestamp" : timestamp, "time_interval" : time_interval, "brainStates" : brainStates[:-1]})
    with open("./data/"+ person_name+"/"+person_name+".json",'w') as outfile:
        json.dump({"result":history}, outfile)
    return "done"

@app.route('/pieChart')
def pieChart():
    # return percentage of attentive and inattentive
    return jsonify({"attentive" : 10, "inattentive" : 90})
    
if __name__ == "__main__":
    app.run(debug=True, threaded=True)