def region_context(request):
    """
    Provides region-specific variables to all templates.
    """
    # Check session for 'region', default to 'NG'
    current_region = request.session.get('region', 'NG')

    return {
        'is_nigeria': current_region == 'NG',
        'current_region': current_region,
    }


def global_settings(request):
    return {
        "demo_button_popup": True,  # example variable for your base.html
    }