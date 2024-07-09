# The InvestmentGenie Generative AI App ⭐️

I’m excited to share a project that automates financial planning and investment services using generative AI. This project demonstrates the significant impact of well-crafted prompts on AI-generated content, highlighting the importance of prompt engineering in maximizing the potential of generative AI systems.

## 1. What is the InvestmentGenie App 🤷?
The InvestmentGenie app is a [wealth management](https://www.investopedia.com/terms/w/wealthmanagement.asp) service that uses generative AI to create investment portfolios. It makes use of the asset allocation strategy, which is the process of dividing an investment portfolio among different asset categories, like stocks and bonds.

In this post, we focus on how to create a generative AI app that offers tailored personalized investment recommendations based on the lifestyle and preferences of users.

## 2. Prompt Engineering 🏗️
Prompt engineering is a crucial skill in working with generative AI models. It involves crafting effective inputs (prompts) to guide AI models in producing desired outputs. 

Prompt engineering techniques include zero-shot prompting, few-shot prompting, chain-of-thought prompting, and ReAct (reasoning and acting). This app makes use of the few-shot prompting technique, which provides a few examples of the task before asking the model to perform it.

## 3. Solution Overview 🛠️
The following figure shows the architecture of the InvestmentGenie app.

![Architecture diagram](images/architecture.png)

Users are able to configure the following input parameters on the app:
- Name
- Age
- Risk appetite
- Retirement age
- Amount to invest
- Marital status
- Number of kids

The personalized recommendations offered by the app includes sections such as:
- Personal details
- Recommendation summary
- Investment recommendation details (allocation, allocation amount, reason for recommendation)
- Allocation charts
- Additional notes
- Learning resources.

### 3.1 Model Selection
A selection of models was reviewed, with consideration for use cases, model attributes, maximum tokens, cost, accuracy, performance, and supported languages. Based on this, Anthropic Claude-3 Sonnet was selected as best suited for this use case, as it strikes a balance between intelligence and speed, and it optimizes on speed and cost.

### 3.2 Prerequisites

You first need to set up an AWS account and configure your [AWS Identity and Access Management](https://aws.amazon.com/iam) (IAM) permissions correctly. You then need to install [Boto3](https://docs.aws.amazon.com/pythonsdk) and the [AWS CLI](https://aws.amazon.com/cli). You also need to [request](https://catalog.workshops.aws/building-with-amazon-bedrock/en-US/prerequisites/bedrock-setup) Anthropic Claude 3 Sonnet model access on [Amazon Bedrock](https://aws.amazon.com/bedrock). You can find the code samples in the [GitHub repository](https://github.com/adelanajohn/InvestmentGenie).

This app utilizes the following patterns:
- Packages: For a hierarchical structuring of the module namespace.
- Application factory: An application factory in [Flask](https://flask.palletsprojects.com) is a design pattern useful in scaling Flask projects. It helps in creating and configuring Flask projects flexibly and efficiently, making it easier to develop, test, and maintain as it grows and evolves.
- Blueprints: Blueprints are a way to organize Flask applications into reusable and maintainable units.
- Templates: Templates are files that contain static data as well as placeholders for dynamic data. A template is rendered with specific data to produce a final document. This app makes use of the [Jinja](https://jinja.palletsprojects.com) template engine.

#### Python virtual environment setup
Establish a [Python venv module](https://docs.python.org/3/library/venv.html) virtual environment in the project directory and then proceed to install all necessary dependencies. By using a project-specific virtual environment, you ensure that all dependencies are installed exclusively within that environment, rather than system-wide.

Windows PowerShell
```shell
python -m venv venv
.\venv\Scripts\activate
```

macOS
```shell
python -m venv venv
source venv/bin/activate
```

You should see a parenthesized **(venv)** in front of the prompt after running the command, which indicates that you’ve successfully activated the virtual environment.

#### Add dependencies
Once you have activated your virtual environment, proceed with installing Flask.

```shell
python -m pip install Flask
```

#### Install requirements
```shell
python -m pip install -r requirements.txt
```

#### Configure AWS CLI options
Next, configure AWS CLI options. If this command is run with no arguments, you will be prompted for configuration values such as your AWS Access Key Id and your AWS Secret Access Key.
```shell
aws configure
```

```shell
AWS Access Key ID [****]:
AWS Secret Access Key [****]:
Default region name [us-east-1]: us-east -1
Default output format [json]: json
```

#### Run the Flask project

Windows PowerShell
```shell
python -m flask --app InvestmentGeniePackage run --port 8000 --debug
```

macOS
```shell
export FLASK_APP=InvestmentGeniePackage
python -m flask —app InvestmentGeniePackage run —port 8000 —debug
```

#### Quit the app
Press CTRL+C or ^C on the terminal. 

#### Exit the Python virtual environment
```shell
deactivate
```

### 3.3 Building the application

#### Application factory (/InvestmentGeniePackage/__init__.py)
Application Factory is a function that is responsible for creating the application object and its configuration.

```python
from flask import Flask

from InvestmentGeniePackage import (
    errors,
    pages
)

def create_app():
    app = Flask(__name__)
    app.secret_key = 'w4&L#3$Qc5@g'

    app.register_blueprint(pages.bp)
    app.register_error_handler(404, errors.page_not_found)
    return app
```

#### Blueprints (/InvestmentGeniePackage/pages.py)
Blueprints are modular components in Flask that encapsulate a collection of related views. They can be easily imported in the init file, providing a convenient way to organize and structure the application's routes and functionality.

```python
from flask import Blueprint, render_template, redirect, request, session, url_for
from json2html import *
import boto3
import json

bp = Blueprint("pages", __name__)

# Home page
@bp.route("/", methods=("GET", "POST"))
def home():
    session['quizFlag']="1"
    if request.method == "POST":
        return redirect(url_for("pages.recommendations"))
        
    return render_template("pages/home.html")

# Recommendations page
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

# LLM call
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
```
#### Page not found (/InvestmentGeniePackage/errors.py)
```python
from flask import render_template

def page_not_found(e):
    return render_template("errors/404.html"), 404
```

#### Base template (/InvestmentGeniePackage/templates/base.html)
The base template is designed to establish a uniform structure for your project while allowing flexibility in certain content areas through Jinja's block functionality.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Investment Genie</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
<h1>Investment Genie</h1>
<section>
  <header>
    {% block header %}{% endblock header %}
  </header>
  <main>
    {% block content %}<p>No messages.</p>{% endblock content %}
  </main>
</section>
</body>
</html>
```

#### Child templates (/InvestmentGeniePackage/templates/pages)
Template inheritance allows you to build a base “skeleton” template that contains all the common elements of your site and defines blocks that child templates can override.

## 4. Conclusion 🌅

This guide walks you through how to build an investment advisor powered by generative AI. It explores 
prompt engineering techniques leveraging the capabilities of Anthropic's Claude 3 Sonnet Large Language Model.