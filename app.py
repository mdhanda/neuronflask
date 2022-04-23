from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin

from neuron.neuron import Neuron
from utilities.utils import Utils

app = Flask(__name__)

logger = Utils.ilogger()
logger.info("Neuron, Start logging...")


@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    if request.method == 'GET':

        #with Neuron() as bot:
            #bot.load_page(const.BASE_URL)
            #bot.scroll_to_bottom()
            #bot.load_all_items()
            #bot.save_to_csv()
            # bot.save_to_mongo()

        try:
            coursesCursor = Utils.iclient().find()
            courses = list(coursesCursor)
            return render_template('index.html', courses=courses)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')


@app.route('/coursedetails', methods=['GET'])  # route to display the home page
@cross_origin()
def coursePage():
    if request.method == 'GET':
        courseURL = request.args.get('query')

        with Neuron() as bot:
            bot.load_page(courseURL)
            bot.scroll_to_bottom()
            bot.load_course_detail()
            objectives = bot.objectives
            requirements = bot.requirements
            curriculam = bot.curriculam
            features = bot.features

        try:
            return render_template('detail.html', objectives=objectives,
                                   requirements=requirements, curriculam=curriculam,
                                   features=features)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')


logger.info("Neuron, Finish logging!!")

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
