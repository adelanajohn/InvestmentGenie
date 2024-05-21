from flask import Blueprint, render_template, redirect, request, session, url_for
from json2html import *
import boto3
import json

bp = Blueprint("pages", __name__)

@bp.route("/", methods=("GET", "POST"))
def home():
    session['quizFlag']="1"
    if request.method == "POST":
        return redirect(url_for("pages.recommendations"))
        
    return render_template("pages/home.html")


@bp.route("/recommendations", methods=("GET", "POST"))
def recommendations():
    if request.method == "POST":
        name=request.form.get('Name')
        age=request.form.get('Age')
        risk_appetite=request.form.get('RiskAppetite')
        retirement_age=request.form.get('RetirementAge')
        amount_to_invest=request.form.get('AmountToInvest')
        marital_status=request.form.get('MaritalStatus')
        number_of_kids=request.form.get('NumberOfKids')
        
        jsonResponse=get_response(name, age, risk_appetite, retirement_age, amount_to_invest, marital_status, number_of_kids) # Call LLM

        # Extract JSON response
        startPosition = jsonResponse.index("{")
        endPosition = jsonResponse.rindex("}")
        json_response = jsonResponse[startPosition:endPosition+1]
                
        # Convert JSON data to a Python object 
        data = json.loads(json_response) 

        _name = data["name"]
        _age = data["age"]
        _risk_appetite = data["risk_appetite"] 
        _retirement_age = data["retirement_age"]
        _amount_to_invest = data["amount_to_invest"]
        _marital_status = data["marital_status"]
        _number_of_kids = data["number_of_kids"]
        _summary = data["summary"]
        _additional_note = data["additional_note"]
        _investment_advice = data["investment_advice"]
        _resources = data["resources"]

        chart_x_values = []
        chart_y_values = []
        # Loop through the top-level _investment_advice keys
        for category, details in _investment_advice.items():
            chart_x_values.append(category)
            chart_y_values.append(details.get('allocation_amount'))
            
        _investment_advice_table = json2html.convert(json=_investment_advice, table_attributes="class='table'")
        _resources_table = json2html.convert(json=_resources, table_attributes="class='table'")

        return render_template("pages/result.html", json_response=json_response, _name=_name, _age=_age, _risk_appetite=_risk_appetite, _retirement_age=_retirement_age, _amount_to_invest=_amount_to_invest, _marital_status=_marital_status, _number_of_kids=_number_of_kids, _investment_advice_table=_investment_advice_table, _summary=_summary, _additional_note=_additional_note, _resources_table=_resources_table, chart_x_values=chart_x_values, chart_y_values=chart_y_values)
        
    else:
        return render_template("pages/home.html")        
    
    return render_template("pages/recommendations.html")


def get_response(name, age, risk_appetite, retirement_age, amount_to_invest, marital_status, number_of_kids):
    bedrock=boto3.client(service_name="bedrock-runtime")

    prompt_example = {
        "name": "James Smith",
        "age": 40,
        "risk_appetite": "high",
        "retirement_age": 50,
        "amount_to_invest": 200000,
        "marital_status": "married",
        "number_of_kids": 2,
        
        "summary": "Based on your age of 40 years, high-risk appetite, planned retirement age of 50 years, marital status (married), and two children, I would recommend an investment strategy that emphasizes growth potential while considering your family's long-term financial needs.",
        "investment_advice": {
            "equity_investments": {
            "allocation": "55-65%",
            "allocation_amount": 100000,
            "recommendation": "Invest in a mix of large-cap, mid-cap, and small-cap stocks across various sectors and industries. Consider growth-oriented equity mutual funds, ETFs, or individual stocks with strong growth prospects. Given your high-risk appetite, you can maintain a tilt towards higher-risk, higher-return investments.",
            "reason": "At 48 years old with a high-risk appetite and a 2-year investment horizon until retirement, you can still afford to take on higher risk to potentially maximize growth. However, you may want to slightly reduce your equity allocation compared to when you were younger."
            },
            "fixed_income_investments": {
            "allocation": "25-35%",
            "allocation_amount": 100000,
            "recommendation": "Invest in government bonds, corporate bonds, and bond mutual funds or ETFs, focusing on short-term and intermediate-term bonds.",
            "reason": "As you approach retirement, increasing your allocation to fixed-income investments can provide stability and a steady stream of income."
            },
            "real_estate_investments": {
            "allocation": "10-15%",
            "allocation_amount": 100000,
            "recommendation": "Consider real estate investments such as REITs or direct real estate investments (if feasible).",
            "reason": "Real estate investments can offer diversification benefits, potential for capital appreciation, and income generation, which can be beneficial for your family's future needs."
            },
            "cash_and_cash_equivalents": {
            "allocation": "5-10%",
            "allocation_amount": 100000,
            "recommendation": "Maintain a cash reserve in highly liquid investments like money market funds or short-term CDs.",
            "reason": "This cash reserve can serve as an emergency fund, provide flexibility for rebalancing, and help meet any immediate financial needs as you approach retirement."
            }
        },
        "additional_note": "As you approach retirement, it's crucial to periodically review and rebalance your portfolio to align with your changing risk tolerance and investment horizon. Additionally, consult with a professional financial advisor to develop a comprehensive retirement plan that considers your specific goals, risk tolerance, and family's financial circumstances.",
        "resources": [
            {
            "name": "Investopedia",
            "url": "https://www.investopedia.com/",
            "description": "A comprehensive financial education resource covering various investment topics, including stocks, bonds, real estate, and portfolio management."
            },
            {
            "name": "Morningstar",
            "url": "https://www.morningstar.com/",
            "description": "Provides research, data, and analysis on mutual funds, ETFs, stocks, and other investment products, as well as portfolio management tools."
            },
            {
            "name": "Vanguard",
            "url": "https://investor.vanguard.com/",
            "description": "A leading provider of low-cost mutual funds and ETFs, offering educational resources and tools for investors."
            },
            {
            "name": "REIT.com",
            "url": "https://www.reit.com/",
            "description": "A comprehensive resource for information and education on real estate investment trusts (REITs)."
            }
        ]
    }
    
    prompt_example_json = json.dumps(prompt_example, indent=4) # Serialize the dictionary to a JSON string    

    prompt_data = f"""
        You are an investment advisor. You give investment advisory based on age, risk appetite, retirement age, amount to invest, marital status, and number of kids. Your advice includes purchasing securities and investment allocation ratios in each asset class. 

        Give an investment advice to <name>{name}</name>.
        Age is <age>{age} years</age>.
        Risk appetite is <risk_appetite>{risk_appetite}</risk_appetite>.
        Retirement age is <retirement_age>{retirement_age} years</retirement_age>.
        Amount to invest <amount_to_invest>{amount_to_invest}</amount_to_invest>.
        Marital status is <marital_status>{marital_status}</marital_status>.
        Number of kids is <number_of_kids>{number_of_kids}</number_of_kids>.

        Please include reasons for each recommendations. Include website resources to learn more about the suggested investment advice. Response format is json.

        See the sample response below:

        <response>
            {prompt_example_json}
        </response>
    """
    
    payload={
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0.8,
        "messages": [
            {
                "role": "user",
                "content": [{ "type": "text", "text": prompt_data}]
            }
        ],
    }

    body=json.dumps(payload)
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    response=bedrock.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body
    )

    response_body=json.loads(response.get("body").read())
    response_text=response_body.get("content")[0].get("text")
    return response_text
