
def get_public_questions(dashboard_ids):
    condition = f'''in {dashboard_ids}''';
    if len(dashboard_ids)==1:
        dashboard_id = dashboard_ids[0]
        condition = f'''={dashboard_id}'''
    return f'''select card_id from public.report_dashboardcard where dashboard_id {condition} order by card_id;'''
