
def get_public_questions(dashboard_ids, combined_questions):
    condition = f'''dashboard_id in {dashboard_ids}''';
    if len(dashboard_ids)==1:
        dashboard_id = dashboard_ids[0]
        condition = f'''dashboard_id={dashboard_id}'''
    if len(combined_questions)>0:
        condition = condition+ f'''  or card_id in {combined_questions}'''

    return f'''select card_id from public.report_dashboardcard where {condition} order by card_id;'''
