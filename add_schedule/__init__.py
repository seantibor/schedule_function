import logging

import azure.functions as func


def main(req: func.HttpRequest, inputblob: func.InputStream,
         outputblob: func.Out[func.InputStream]) -> func.HttpResponse:
    logging.info('Python add_schedules trigger function processed %s', inputblob.name)

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
