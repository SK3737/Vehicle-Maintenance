from fastapi import FastAPI, Path, HTTPException,Query
# HTTPException is a built-in exception in FastAPIused to return custom HTTP error responses when something goes wrong in your API
# Path is a function used to define path parameters in your API endpoints, allowing you to capture dynamic values from the URL.
#Query parameters are optional key-value pairs appended to the end of a URL, used to pass additional data to the server in a HTTP request.They are typically employed for operations like filtering, sorting,searching, and pagination in API endpoints. The ? symbol is used to indicate the start of query parameters in a URL, and multiple parameters are separated by the & symbol. For example, in the URL http://example.com/api/items?category=books&sort=asc, category and sort are query parameters with values books and asc respectively.
import json
app = FastAPI()


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

@app.get("/")
def hello():
    return {'message': 'Patient System Management API'}

@app.get("/about")
def about():
    return{'message': 'A fully functional API to manage your patient records'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description = 'ID of the patient in the DB', example = 'P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code = 404, detail='Patient not found')

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description = 'Sort on the basis of height, weight or bmi'), order: str = Query('asc', description = 'Sorting order, either asc or desc')):
    data = load_data()
    if sort_by not in ['height', 'weight', 'bmi']:
        raise HTTPException(status_code = 400, detail='Invalid sort parameter')
    return sorted(data.values(), key=lambda x: x[sort_by], reverse=(order == 'desc'))