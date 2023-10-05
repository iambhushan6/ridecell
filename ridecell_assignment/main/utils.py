from typing import Optional
from rest_framework.response import Response



def success_response(status: int, data: Optional[dict] = None, *args, **kwargs):
        final_data = data or {}
        assert isinstance(final_data, dict)
        response = {
            "status_code": status,
            "status": "success",
            "data": final_data,
        }
        return Response(data=response, status=status)

def error_response(status: int, data: Optional[dict] = None, errors: list = [], *args, **kwargs):
    final_data = data or {}
    assert isinstance(final_data, dict)
    response = {
        "status_code": status,
        "status": "failure",
        "data": final_data,
        "errors": [e.value.get_dict_representation() for e in errors],
    }
    return Response(data=response, status=status)