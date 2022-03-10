"""
Fichier principal de lancement de l'application
"""
from os import O_TRUNC
from flask import Flask, render_template, request, flash, send_file, jsonify
from bson.json_util import dumps
import pandas as pd
import os.path
from pymongo import MongoClient
import pymongo
from werkzeug.datastructures import RequestCacheControl


# load file
classes = []
data = []
file = []
liste_classe_DB = []
assets_path = ''

# connexion base de Données
CLIENT = MongoClient('mongodb://mongo-db.labellisation.datalab.cloud.maif.local:27017')
DB = CLIENT.labellisation

app = Flask(__name__)

# accept csv format
ALLOWED_EXTENSIONS = ["csv"]
def allowed_file(filename):
   return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# load home page
@app.route('/')
def creation_session():
 return render_template('1_creation_session.html')


# button return home
@app.route('/home', methods=['GET'])
def return_home():
   return render_template('1_creation_session.html')


@app.route('/dataset-loader', methods=['POST'])
def dataset_loader():
   global classes
   # Création dictionnaire de fichier à inserer en base
   label_session = {
      "_id": None,
      "name": "Session 1",
      "type": 1,
      "assetsPath": "/data_tech/shares/" + request.form.get("path_folder"),
      "listeClasse": [],
      "dataset": []
   }
   # check if the post request has the file part
   if 'datafile' not in request.files:
      return "No file"
   file = request.files['datafile']
   # if user does not select file, browser also
   # submit an empty part without filename
   if file.filename == '':
      return "No filename"
   if file and allowed_file(file.filename):
      data = pd.read_csv(file, encoding='utf8', error_bad_lines=False, delimiter=',')
      tableau = data.to_html(index=False, classes=['responsive-table', 'striped'])
   # récupère l'id le plus grand et implémentation
   try:
      id = DB.session.find_one(sort=[("_id", pymongo.DESCENDING)]).get('_id') + 1
      label_session['_id'] = id
      print("id_1", id)
   except Exception as e:
      print(e)
      return render_template('1_creation_session.html')
   # Implémentation des classes uniques
   classes = list(set(list(data['predict1'].unique()) + list(data['predict2'].unique())))
   label_session['listeClasse'] = classes
   # Création du fichier type
   temp_file = data.to_dict(orient='records')
   i=0
   for item in temp_file:
      item['id'] = i
      item['prediction'] = [{'classe' : item['predict1'], 'proba' : item['proba1']}, 
                        {'classe' : item['predict2'], 'proba' : item['proba2']}]
      item['label'] = {'answer' : {'status' : 'accept', 
                       'class' : None}, 
                     'seen' : False}
      i+=1
   for i in temp_file:
      i.pop('predict1')
      i.pop('proba1')
      i.pop('predict2')
      i.pop('proba2')
   label_session['dataset'] = temp_file
   # Ecriture dans la base
   DB.session.insert(label_session)
   # Vérifier l'insertion
   try:
      DB.session.find_one("_id")
      return render_template('2_class_manager.html', tableau=tableau, classes=classes, id_session=id)
   except Exception as e:
      print(e)
      return render_template('1_creation_session.html', classes=classes)


# Display and edit list of class
@app.route('/add-class', methods=['POST'])
def add_class():
   global classes
   classe = request.form.get("classe")
   id = int(request.form.get("id"))
         # Ajouter a la base de données, et non dans la variable "classe" et supprimer cette variable globale
         # 1_ Lecture en base pour l'id de la session courante
         # 2_ Récupérer la liste des classes
   # for x in DB.session.find({'_id': id}):
   x = next(DB.session.find({'_id': id}))
   liste_classe_DB = x['listeClasse']
   print('liste_classe_DB', liste_classe_DB)
   if classe not in liste_classe_DB:
      liste_classe_DB.append(classe)
      #DB.session.insert_one({ 'listeClasse': classe }) 
      DB.session.find_one_and_update({
                                    '_id': id,
                                 }, {
                                    '$set':{'listeClasse': liste_classe_DB}
                                 })
      print('liste_classe_DB new', liste_classe_DB)
      classes = liste_classe_DB
   # 3_ Vérifier si elle n'existe pas, et l'insérer
   return {"status": "OK"}
   

# Function delete class
@app.route('/delete-class', methods=['POST'])
def remove_classe():
   global classes
   #1_ récupérer la liste des classes
   #2_ La retirer de la liste python
   #3_ Override la liste avec la classe en moins
   #classes.remove(id_class)
   classe_id = request.form.get("classe_id")
   session_id = int(request.form.get("session_id"))
   print(session_id, classe_id)
   try:
      x = next(DB.session.find({'_id': session_id}))
      liste_classe_DB = x['listeClasse']
      print('liste_classe_avant_supp', liste_classe_DB)
      if classe_id in liste_classe_DB:
         liste_classe_DB.remove(classe_id)
         DB.session.find_one_and_update({
                                       '_id': session_id,
                                    }, {
                                       '$set':{'listeClasse': liste_classe_DB}
                                    })
         print('liste_classe_apres_supp', liste_classe_DB)
   except Exception as e:
      print(e)
      return {"status": "OK"}, 400
   return {"status": "OK"}
   


# Display button for each class
@app.route('/session/<int:session_id>', methods=['GET'])
def session(session_id):
   # Récupère le path où sont stockés les images
   for x in DB.session.find({'_id': session_id}):
      assets_path = (x['assetsPath'])
   result = DB.session.find_one({"_id": int(session_id)})
   if result:
      classes = result.get('listeClasse')
      id = result.get('_id')
      type = result.get('type')
      name = result.get('name')
      if classes and id and type and name:
         return render_template('session.html', classes=classes, id_session=id, type=type, name=name, assets_path=assets_path)
      else:
         return {"SESSION":"INCORRECTE"}


@app.route('/data', methods=['GET'])
def get_data():
   session_id = request.args['session_id']
   # result = DB.session.find_one_and_update({"supervisor.session": area,
   #                                        'supervisor.seen': False,
   #                                        'supervisor.answer.status': None,
   #                                     }, {
   #                                              '$set':{'supervisor.seen': True}
   #                                        })
   # 1_ Récupérer le premier element du dataset pour la session donnée non labelisé
   result = DB.session.find_one({'_id': session_id,
                                 'data.label.seen': False})
   if result is None:
      return jsonify({}), 204
   return dumps(result)


@app.route('/reporting', methods=['GET'])
def reporting():
   # Instanciation
   mycol = DB["session"]
   ma_liste = []
   y = 0
   z = 0
   avancement = 0
   # Récupère l'id de session le plus grand (pour l'instant)
   id = DB.session.find_one(sort=[("_id", pymongo.DESCENDING)]).get('_id')
   # Récupère la liste de classe de cette session
   for x in mycol.find({'_id': id}):
      liste_classe = (x['listeClasse'])
   # Compter nombre d'images dans cette session
   for x in mycol.find({'_id': id}):
      nb_element = (len(x['dataset']))
   # Chargement du dataset dans la variable ma_liste
   for x in mycol.find({'_id': id}):
      ma_liste = (x['dataset'])
   # Nombre d'images labellisé pour mesurer l'avancement
   for item in ma_liste:
      if (item['label']['seen']) == False:
         y+=1
   element_non_lab = y
   # Nombre d'images non-labellisé pour mesurer ce qu'il reste à faire
   for item in ma_liste:
      if (item['label']['seen']) == True:
         z+=1
   element_lab = z
   # Avancement
   avancement = str(element_lab / nb_element) + "%"
   return render_template('reporting.html', id=id, liste_classe=liste_classe, nb_element=nb_element, element_non_lab=element_non_lab, element_lab=element_lab, avancement=avancement)


# Run app
if __name__ == '__main__':
   app.run(debug=True, host="0.0.0.0", port=9876)