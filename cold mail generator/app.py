import os
import uuid
import pandas as pd
import chromadb
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

# Load Environment Variables and the api key

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Flask App
app = Flask(__name__)

# Initialize ChromaDB Client( the vector database)
client = chromadb.PersistentClient(path="vector_data")#persistent client makes an entry into the directory, in order to store the meta data and avrious data(gibrish to humans)
collection = client.get_or_create_collection(name="portfolio")

# Load Portfolio Samples into ChromaDB
if not collection.count():#basic python iteration
    df = pd.read_csv("portfoliosample.csv")
    for _, row in df.iterrows():
        collection.add(
            documents=[row["Techstack"]],
            metadatas=[{"links": row["Links"]}],
            ids=[str(uuid.uuid4())],
        )

# Selenium WebDriver Setup
def initialize_driver():
    chromedriver_path = "C://Users//Vaibhav Kumar//OneDrive//Desktop//cold mail generator//chromedriver-win64//chromedriver.exe"
    
    if not os.path.exists(chromedriver_path):
        raise Exception(f"Chromedriver not found at {chromedriver_path}. Please check the path.")
    
    options = Options()# handling of header and feilds for, easy scaping and reduce load
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

# Scrape Website
def scrape_website(website):
    try:
        driver = initialize_driver()
        driver.get(website)
        time.sleep(5)#delay of 5 secs to load the page
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        return f"Error loading page: {str(e)}"

# Extract Job Details
def extract_job_details(html_content):#extracts title,descrption,responsibliteis and skill(skills and responsiblities are main)
    soup = BeautifulSoup(html_content, "html.parser")
    
    job_title = soup.find("h1")
    job_description = soup.find("div", class_="job-description")
    
    responsibilities = [li.text.strip() for li in soup.find_all("li", class_="responsibilities")]
    skills = [li.text.strip() for li in soup.find_all("li", class_="skills")]
    
    return {
        "title": job_title.text.strip() if job_title else "Unknown",
        "description": job_description.text.strip() if job_description else "",
        "responsibilities": ", ".join(responsibilities),
        "skills": ", ".join(skills)
    }

# Get Relevant Portfolio Links#in the vector data bases, nresult =2 meaning only topp 2 relvant feild withe metadata(link) will be displayed.
#can be increased, but will increarse the clutter.
def get_relevant_links(skills, responsibilities):
    search_query = f"{skills}, {responsibilities}"
    results = collection.query(
        query_texts=[search_query],
        n_results=2
    )
    # Debugging: Print query results, when you want to check in the backend
    #print("Query Results:", results)  
    
    formatted_links = []
    for i, metadata in enumerate(results["metadatas"][0]):
        if "links" in metadata:
            techstack = results["documents"][0][i]#extract the top 1 from the 2 results, which is semantically nearest.
            formatted_links.append(f"* {techstack} ({metadata['links']})")#this will ad the metadata into the formatted place
    
    print("Formatted Links:", formatted_links)  # Debugging: Print formatted links
    return "\n".join(formatted_links)

# LangChain Setup #framework to use llms
llm = ChatGroq(api_key=GROQ_API_KEY, model_name="llama3-8b-8192")
prompt_email = PromptTemplate.from_template(
    """
    ### JOB DESCRIPTION:
    {job_description}
    
    ### RESPONSIBILITIES:
    {responsibilities}
    
    ### REQUIRED SKILLS:
    {skills}
    
    ### PORTFOLIO LINKS:
    {link_list}
    ### EMAIL (NO PREAMBLE):
    ### INSTRUCTION:
        You are ABC, a business development executive at XYZ. XYZ is an AI & Software Consulting company dedicated to facilitating
        the seamless integration of business processes through automated tools. 
        Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability, 
        process optimization, cost reduction, and heightened overall efficiency. 
        Your job is to write a cold email to the client regarding the job mentioned above describing the capability of XYZ
        in fulfilling their needs.
        Adress the client as hiring manager only,and i dont need the preamble give me the direct email.
        Also mention a call to action, to the mail address of abc@xyz.in 
        Also add the most relevant ones from the following links to showcase Atliq's portfolio: {link_list}
        Remember you are ABC, BDE at XYZ. 
        Do not provide a preamble.
   
    ### EMAIL (NO PREAMBLE):
    """
    
)
chain_email = LLMChain(prompt=prompt_email, llm=llm)#gives input of the prompt(customized) to the llm, which is addressed using the groqapi key

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/process-job", methods=["POST"])
def process_job():
    try:#try-catch block for handling the errors
        data = request.json
        job_url = data.get("job_url")
        if not job_url:
            return jsonify({"error": "Job URL is required"}), 400 #request handling(server cannot process or understand the request)
        
        html_content = scrape_website(job_url)
        if "Error" in html_content:
            return jsonify({"error": html_content}), 500 #internal server error
        
        job_details = extract_job_details(html_content)
        skills = job_details["skills"]
        responsibilities = job_details["responsibilities"]
        
        portfolio_links = get_relevant_links(skills, responsibilities)
        #print("Portfolio Links for Email:", portfolio_links)  # Debugging: Print links before email generation
        
        email_result = chain_email.invoke({
            "job_description": job_details["description"],
            "responsibilities": responsibilities,
            "skills": skills,
            "link_list": portfolio_links
        })
        
        email_body = email_result.get("text", "No email generated.")
        
        return jsonify({
            "email": email_body,
            "portfolio_links": portfolio_links,
            "job_details": job_details
        })
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)})

if __name__ == "__main__":
    app.run(debug=True)