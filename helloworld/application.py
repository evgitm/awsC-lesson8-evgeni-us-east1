#!flask/bin/python
import json
import requests
from flask import Flask, Response, request
from helloworld.flaskrun import flaskrun
from flask_cors import CORS
import boto3
from datetime import datetime

application = Flask(__name__)

#כfor CORS support (requirements update  + app import CORS required)
CORS(application, resources={r"/*": {"origins": "*"}}) 


@application.route('/', methods=['GET'])
def get():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)

@application.route('/', methods=['POST'])
def post():
    return Response(json.dumps({'Output': 'Hello World'}), mimetype='application/json', status=200)
    



currency_rate = {
    'usd' : 3.3,
    'pound' : 4.5,
    'euro' : 4.8
}


@application.route('/calc/currency/<string:currency>', methods=['GET'])
def post_currency(currency):
    res = currency_rate.get(currency, 0.00) 
    return Response(json.dumps({currency: res}), mimetype='application/json', status=200)
#curl http://localhost:8000/calc/currency/usd


@application.route('/calc/bit', methods=['GET'])
def post_currency_bit():
    return Response(json.dumps(get_bitcoin_index()), mimetype='application/json', status=200)


def get_bitcoin_index():
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    response = requests.get(url).json()['bpi']['USD']
    return response
#curl http://localhost:8000/calc/bit



# return generic data
@application.route('/get_generic', methods=['GET'])
def get_generic_data():
    return Response(json.dumps(generic_data), mimetype='application/json', status=200)

#generic data
generic_data = [
    {
    "id":1,
    "title": "wtf",
    "body": "good will"
    },
    {
    "id":2,
    "title": "wtf2",
    "body": "good will2"
    }
   ]
   
 #curl http://localhost:8000/get_generic
 
######### Lecture 6  ########

# TASK 01 - Return result of Multiplication of 2 numbers
@application.route('/v1/multiply', methods=['GET', 'POST'])
def get_mult_res():
    first_num = request.args.get('first_num')
    second_num = request.args.get('second_num')
    res = float(first_num) * float(second_num) 
    return Response(json.dumps({'multiplication result': res}), mimetype='application/json', status=200)  
# curl -i http://"localhost:5000/v1/multiply?first_num=12.1&second_num=12"
    
    
# Lecture 6 - Homework - return price of 10 bitcoines
@application.route('/v1/bit_mult', methods=['GET', 'POST'])
def get_bit_mult_res():
    bit_quantity = request.args.get('bit_quantity')
    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    bitcoin_rate = requests.get(url).json()['bpi']['USD']['rate_float']
    res = float(bit_quantity) * float(bitcoin_rate) 
    return Response(json.dumps({'Price in USD of 10 Bit-coins is': res}), mimetype='application/json', status=200)
# curl -i http://"localhost:5000/v1/bit_mult?bit_quantity=10"
    
     


######### Lecture 7 DynamoDB  ########

@application.route('/get_forms', methods=['GET'])
def get_frm():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # replace table scan
    resp = table.scan()
    print(str(resp))
    return Response(json.dumps(str(resp['Items'])), mimetype='application/json', status=200)


@application.route('/set_form/<frm_id>', methods=['POST'])
def set_doc(frm_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # get post data  
    data = request.data
    # convert the json to dictionary
    data_dict = json.loads(data)
    # retreive the parameters
    form_body = data_dict.get('form_body','default')
    form_title = data_dict.get('form_title','defualt')
    form_type = data_dict.get('form_type','defualt')

    
    item={
    'form_id': frm_id,
    'form_body': form_body,
    'form_title': form_title,
    'form_type': form_type 

     }
    table.put_item(Item=item)
    return Response(json.dumps(item), mimetype='application/json', status=200)
# curl -i -X POST -d'{"form_title":"form title1", "form_body":"where is it?", "form_type":"finance"}' -H "Content-Type: application/json" http://localhost:8000/set_form/frm4


# Lecture 7 - Homework - DynamoDB delete record by id and sort attr

@application.route('/delete_record', methods=['GET', 'POST'])
def delete_doc():
    frm_id = request.args.get('frm_id')
    form_type = request.args.get('form_type')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    # get post data  
    response = table.delete_item(
        Key={
            'form_id': frm_id,
            'form_type': form_type,
        }
    )
        
    return response
#curl -i http://"localhost:8000/delete_record?frm_id=frm4&form_type=finance"


# Lecture 7 - Homework - DynamoDB get record by id and sort attr

@application.route('/get_form_record', methods=['GET'])
def get_frm_rec():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('forms')
    frm_id = request.args.get('frm_id')
    form_type = request.args.get('form_type')
    # replace table scan
    resp = table.get_item(Key={
            'form_id': frm_id,
            'form_type': form_type,
    })
    return Response(json.dumps(str(resp)), mimetype='application/json', status=200)
#curl -i http://"localhost:8000/get_form_record?frm_id=frm4&form_type=finance"
#return resp is enough


######### Homework Lecture 8 S3  ########

@application.route('/create_txt', methods=['GET'])
def create_txt():
    s3 = boto3.resource('s3', region_name='us-east-1')
    date_time = datetime.now()
    dt_string = date_time.strftime("%d-%m-%Y %H-%M-%S")
    filename = "%s.txt" % dt_string

    print("Today's date:", filename)
    object = s3.Object('aws-lesson8-s3-upload-bucket', filename)
    resp = object.put(Body="")
    return Response(json.dumps(str(resp)), mimetype='application/json', status=200)
    #curl http://localhost:8000/create_txt



######### Homework Lecture 9 Image Rekognition  ########
# curl localhost:8000/analyze/aws-lesson9-rekognition-s3-upload/man.jpg    
@application.route('/analyze/<bucket>/<image>', methods=['GET'])
def analyze(bucket='aws-lesson9-rekognition-s3-upload', image='person.jpg'):
    return detect_labels(bucket, image)
def detect_labels(bucket, key, max_labels=3, min_confidence=90, region="us-east-1"):
    rekognition = boto3.client("rekognition", region)
    s3 = boto3.resource('s3', region_name = 'us-east-1')
    
    image = s3.Object(bucket, key) # Get an Image from S3
    img_data = image.get()['Body'].read() # Read the image
    
    response = rekognition.detect_labels(
        Image={
            'Bytes': img_data
        },
        MaxLabels=max_labels,
		MinConfidence=min_confidence,
    )
    return json.dumps(response['Labels'])


    
if __name__ == '__main__':
    flaskrun(application)

