import json
import os
import re
from google.adk.agents.llm_agent import Agent

# This is the root agent definition provided by you.
# It will be used to interact with the user and generate responses.
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction="""You are an AI financial assistant whose goal is to interactively gather my information step by step (never all at once) 
    to create a comprehensive investment and financial plan. Dont make the responces long compress it keeping it jolly and informative but 
    the final report shall be detailed properly with all the graphs charts bars evertyhting Begin by asking “What is your name, income, gender, and age?” 
    and then move on sequentially to my net worth, emergency fund, expenses, assets, liabilities, and financial goals. Maintain an encouraging, interactive tone and 
    summarize my situation at key stages. Ask if I have any loans, and if yes, which type—personal, gold, home, student, car, or Loan Against Property (LAP)—then suggest 
    applicable tax deductions for each under Indian law. The final plan must consider taxable and non-taxable income, balance high-risk and low-risk investments, and 
    diversify across liquid and non-liquid assets while covering expenses, optimizing taxes, and recommending allocations in both government-backed (PPF, EPF, NSC, Sukanya Samriddhi, Sovereign Gold Bonds) 
    and private options (mutual funds, equity, NPS, real estate, insurance-linked products). When suggesting mutual funds, stocks, or commodities, provide their names, current cost per unit, expected future value, 
    and reasons for suitability with reliable sources. The output should include proper bar graphs and pie charts using text-based characters (e.g., using '█' to create a bar chart) to visually represent the data, 
    pros and cons of each option, and clear projections for goal achievement. Once all inputs are gathered, present a draft for approval, then deliver a professional final document (with my name at the top) containing
    a quarter-wise roadmap of investments and expected returns, formatted with the disclaimer at the start and end: “I’m just an AI assistant providing educational guidance; this is a prediction for an ideal-case scenario, 
    investments carry risks, and you should consult a licensed financial advisor before acting
    """,
)

def log_data(query, response, filename='conversation_log.json'):
    """
    Appends a query-response pair to a JSON file.
    If the file does not exist, it will be created.
    """
    data = []
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    new_entry = {
        'query': query,
        'response': response
    }
    data.append(new_entry)

    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Conversation logged to {filename}")

def generate_final_plan_document(filename, final_plan_content):
    """
    Generates a professional Markdown document with the final investment plan.
    This document can be easily converted to a PDF.
    """
    md_filename = os.path.splitext(filename)[0] + '.md'
    
    try:
        user_name = filename.split('_')[0].capitalize()
    except IndexError:
        user_name = "User"

    full_content = f"""
{user_name}

> I’m just an AI assistant providing educational guidance; this is a prediction for an ideal-case scenario, investments carry risks, and you should consult a licensed financial advisor before acting.

{final_plan_content}

> I’m just an AI assistant providing educational guidance; this is a prediction for an ideal-case scenario, investments carry risks, and you should consult a licensed financial advisor before acting.
"""
    with open(md_filename, 'w') as f:
        f.write(full_content.strip())
    print(f"\nYour final investment plan has been saved to '{md_filename}'. You can now convert this Markdown file to a DOCX or PDF using various tools or services.")
    
def find_matching_file(income, gender, city):
    """
    Searches for an existing conversation log file that matches the provided criteria.
    Criteria: same gender and city, and income within a +-20% range.
    """
    tolerance = 0.20
    pattern = re.compile(r'[^_]+_([mf])_(\d+\.?\d*)_([^.]+)\.json')

    for filename in os.listdir('.'):
        match = pattern.match(filename.lower())
        if match:
            file_gender, file_income_str, file_city = match.groups()
            file_income = float(file_income_str)
            if (file_gender == gender.lower() and 
                file_city.lower() == city.lower() and
                abs(income - file_income) <= tolerance * file_income):
                return filename
    return None

def main():
    """
    Main function to run the interactive financial assistant and log data.
    """
    print("Welcome! I am your AI financial assistant.")
    print("Let's start building your financial plan.")
    print("Type 'quit' at any time to exit.")

    user_input = input("You: What is your Name, Age, Income (in lakhs), Gender (M/F), and City of residence?\n")
    try:
        parts = [p.strip() for p in user_input.split(',')]
        user_name = parts[0]
        user_age = int(parts[1])
        user_income = float(parts[2])
        user_gender = parts[3].upper()
        user_city = parts[4]
    except (ValueError, IndexError):
        print("Invalid input format. Please try again, providing all five details separated by commas.")
        return

    conversation_filename = f"{user_name.lower()}_{user_gender.lower()}_{user_income}_{user_city.lower()}.json"

    matching_file = find_matching_file(user_income, user_gender, user_city)
    
    if matching_file:
        print(f"\nFound a similar profile: {matching_file}")
        try:
            with open(matching_file, 'r') as f:
                historical_data = json.load(f)
            print("Loading historical conversation data for reference...")
            # Here you would load historical data into the agent's context
            for entry in historical_data:
                print(f"Historical Query: {entry['query']}")
                print(f"Historical Response: {entry['response']}")
        except Exception as e:
            print(f"Error loading historical data: {e}")
            
    initial_query = f"""
    You are an AI financial assistant whose goal is to interactively gather information from me step by step in order to create a comprehensive investment and financial plan. My name is {user_name}, I am a {user_age} year old {user_gender} living in {user_city} with an annual income of {user_income} lakhs.
    The plan must consider both taxable and non-taxable income, diversify my portfolio across liquid and non-liquid assets, and balance high-risk and low-risk investments while ultimately helping me grow wealth toward a specific target within a defined timeframe. It should also cover my annual living expenses, provide effective tax-saving strategies, and suggest practical ways to reduce expenses. You must never ask for all details at once but instead ask me one question at a time. Throughout the conversation, you should maintain a slightly interactive and encouraging mood, appreciating my progress, net worth, or portfolio as I share it. As you gather details, summarize my situation at key stages and ultimately present a structured roadmap that includes building an emergency fund, optimizing taxes, and allocating surplus across Indian government-backed options such as PPF, EPF, NSC, Sukanya Samriddhi, and Sovereign Gold Bonds, as well as private options such as mutual funds, equity, NPS, real estate, and insurance-linked products. Ask the person if they have any loans; if yes, ask which type—personal, gold, home, student, car, or Loan Against Property (LAP)—then suggest applicable tax deductions for each. The plan must also account for age-based strategies by suggesting senior citizen investment options when relevant and highlight female-specific schemes offered by the Indian government when applicable. In addition, when recommending mutual funds, stocks, and commodities, you must provide their names, current cost per unit, expected future value, and explain why they are suitable, making sure the information is accurate and citing reliable financial news or sources where relevant. You should also provide a graphical representation of allocations through bar graphs and pie charts using text-based characters (e.g., using '█' to create a bar chart) to visually represent the data, pros and cons of each option, and clear projections for goal achievement. Once all inputs are gathered, present a draft for approval, then deliver a professional final document (with my name at the top) containing a quarter-wise roadmap of investments and expected returns, formatted with the disclaimer at the start and end: “I’m just an AI assistant providing educational guidance; this is a prediction for an ideal-case scenario, investments carry risks, and you should consult a licensed financial advisor before acting.”
    """
    
    print("Agent is getting ready with the initial plan...")
    response = root_agent.ask(initial_query)
    print(f"Agent: {response}")
    log_data(initial_query, response, filename=conversation_filename)

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        agent_response = root_agent.ask(user_input)
        print(f"Agent: {agent_response}")
        log_data(user_input, agent_response, filename=conversation_filename)

        if "final" in agent_response.lower() and ("plan" in agent_response.lower() or "roadmap" in agent_response.lower()):
            print("\nAgent has completed the plan. Automatically generating the final document...")
            generate_final_plan_document(conversation_filename, agent_response)
            break

if __name__ == '__main__':
    main()