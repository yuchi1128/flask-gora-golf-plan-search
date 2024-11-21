from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Rakuten API settings
RAKUTEN_API_BASE = "https://app.rakuten.co.jp/services/api/Gora/GoraPlanSearch/20170623"
APP_ID = "1026721626828506177"

# Area code definitions
AREA_CODES = {
    "北海道,東北": "101", 
    "関東": "102",
    "北陸": "103",
    "中部": "104",
    "近畿": "105",
    "中国": "106",
    "四国": "107",
    "九州,沖縄": "108"
}

@app.template_filter('number_format')
def number_format_filter(value):
    return "{:,}".format(value)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        play_date = request.form['play_date']
        area_code = request.form['area_code']

        params = {
            'format': 'json',
            'applicationId': APP_ID,
            'playDate': play_date,
            'areaCode': area_code,
            'planLunch': '1',
            'sort': 'evaluation'
        }

        try:
            response = requests.get(RAKUTEN_API_BASE, params=params)
            data = response.json()
            golf_plans = []

            if 'Items' in data:
                for item in data['Items']:
                    course = item['Item']
                    
                    course_info = {
                        'name': course['golfCourseName'],
                        'rating': course.get('evaluation', 'なし'),
                        'prefecture': course['prefecture'],
                        'imageUrl': course['golfCourseImageUrl'],
                        'caption': course.get('golfCourseCaption', ''),
                        'highway': course.get('highway', ''),
                        'ic': course.get('ic', ''),
                        'plans': []
                    }

                    if 'planInfo' in course:
                        for plan in course['planInfo']:
                            plan_details = plan['plan']
                            plan_info = {
                                'name': plan_details['planName'],
                                'price': plan_details['price'],
                                'round': plan_details['round'],
                                'lunch': '昼食付' if plan_details['lunch'] == 1 else '昼食なし',
                                'reserveUrl': plan_details['callInfo']['reservePageUrlPC'],
                                'stock_status': plan_details['callInfo']['stockStatus'],
                                'stock_count': plan_details['callInfo'].get('stockCount', 0)
                            }
                            course_info['plans'].append(plan_info)

                    golf_plans.append(course_info)

            return render_template('index.html', 
                                golf_plans=golf_plans,
                                areas=AREA_CODES,
                                selected_date=play_date,
                                selected_area=area_code)

        except Exception as e:
            return render_template('index.html', 
                                error=f"エラーが発生しました: {str(e)}",
                                areas=AREA_CODES)

    tomorrow = datetime.now() + timedelta(days=1)
    default_date = tomorrow.strftime('%Y-%m-%d')
    return render_template('index.html', areas=AREA_CODES, default_date=default_date)

if __name__ == '__main__':
    app.run(debug=True)