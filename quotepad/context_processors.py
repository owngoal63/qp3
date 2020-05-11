# To be used to pass static variables to templates

def static_vars(request):
    return {
        'YH_SS_INTEGRATION': True,
    }