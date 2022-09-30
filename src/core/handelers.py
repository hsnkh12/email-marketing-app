from django.shortcuts import render_to_response

def handler404(request, exception, template_name="httpres/404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response


def handler500(request, exception, template_name="httpres/500.html"):
    response = render_to_response(template_name)
    response.status_code = 500
    return response