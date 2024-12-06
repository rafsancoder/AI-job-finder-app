import flet as ft
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Load Hugging Face GPT-2 model using PyTorch
try:
    advisor = pipeline("text-generation", model="gpt2")
except Exception as e:
    advisor = None
    print(f"Error initializing Hugging Face pipeline: {e}")

# Function to get career advice
def get_advice(question):
    if not advisor:
        return "AI model is not available. Please check your installation of PyTorch or TensorFlow."
    try:
        prompt = (
            f"You are an expert career advisor. Provide detailed, professional advice for the following query:\n\n"
            f"'{question}'\n\n"
            "Your response should include:\n"
            "1. Specific suggestions.\n"
            "2. Practical steps.\n"
            "3. Additional tips or resources if applicable.\n\nAnswer:"
        )
        result = advisor(prompt, max_length=500, num_return_sequences=1, truncation=True)
        return result[0]["generated_text"].strip()
    except Exception as e:
        return f"Error generating advice: {str(e)}"

# Function to scrape job listings using ScraperAPI
def scrape_jobs(query):
    try:
        api_key = "3941c0d62a0b8bde497e0e31631cc56b"  # Replace with your ScraperAPI key
        url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l="
        proxy_url = f"https://api.scraperapi.com?api_key={api_key}&url={url}"

        response = requests.get(proxy_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="job_seen_beacon")

        job_list = []
        for card in job_cards[:5]:  # Limit to 5 results
            try:
                title = card.find("h2", class_="jobTitle").text.strip() if card.find("h2", class_="jobTitle") else "No Title"
                company = card.find("span", class_="companyName").text.strip() if card.find("span", class_="companyName") else "Unknown Company"
                link = "https://www.indeed.com" + card.find("a")["href"] if card.find("a") else "#"
                job_list.append((title, company, link))
            except Exception as e:
                print(f"Error parsing job card: {e}")

        if not job_list:
            print("No jobs found. The structure of the page might have changed.")
        return job_list
    except Exception as e:
        print(f"Error scraping jobs: {e}")
        return []

# Main Flet app
def main(page: ft.Page):
    page.title = "AI Job Finder and Advisor"
    page.scroll=ft.ScrollMode.AUTO
    page.vertical_alignment=ft.MainAxisAlignment.CENTER
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0

    # Define a dynamic content container
    content_area = ft.Container(expand=True)

    # Background Image
    background_image = ft.Container(
        content=ft.Image(
            src="assets/images/image-1.png",  # Replace with your image path
            fit=ft.ImageFit.COVER,
            width=1600,
            height=800,
        ),
        expand=True,
    )

    # Navigation Bar
    navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icon(ft.Icons.HOME, color="green"), label="Home"),
            ft.NavigationBarDestination(icon=ft.Icon(ft.Icons.WORK, color="green"), label="Jobs"),
            ft.NavigationBarDestination(icon=ft.Icon(ft.Icons.LIGHTBULB, color="green"), label="Advice"),
        ],
        selected_index=0,
        on_change=lambda e: navigate_to(e.control.selected_index),
    )

    # Home Page Content
    def home_view():
        return ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome to the AI Job Finder and Advisor!",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.TEAL_ACCENT,
                        text_align="center"
                    ),
                    ft.Text(
                        "Your ultimate tool for finding jobs and receiving career advice."
                        "Focus on advancing your career, not navigating endless job boards." 
                        "We simplify the complexities of job searching and career planning, from tailored job listings to expert advice,so you can achieve your professional goals faster and with confidence.",
                        size=20,
                        width=800,
                        color=ft.Colors.YELLOW,
                        text_align="center"

                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # Job Search Page Content
    job_results = ft.ListView(height=400, spacing=10, padding=10)

    def search_jobs(e):
        job_results.controls.clear()
        query = job_search_input.value
        if query:
            jobs = scrape_jobs(query)
            if not jobs:
                job_results.controls.append(
                    ft.Text("No jobs found. Try a different search.", color=ft.Colors.RED)
                )
            else:
                for title, company, link in jobs:
                    job_results.controls.append(
                        ft.Card(
                            content=ft.ListTile(
                                title=ft.Text(title, color=ft.Colors.LIME),
                                subtitle=ft.Text(company, color=ft.Colors.TEAL),
                                trailing=ft.Icon(ft.Icons.OPEN_IN_NEW, color=ft.Colors.CYAN),
                                on_click=lambda e, job_url=link: page.launch_url(job_url),
                            ),
                        )
                    )
            job_results.update()

    job_search_input = ft.TextField(label="Enter job title or keyword",width=800,text_align="center", border_color="white")
    search_button = ft.ElevatedButton("Search Jobs", on_click=search_jobs)

    def job_view():
        return ft.Column(
            [
                ft.Text(
                    "Find Your Dream Job",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.YELLOW,
                ),
                job_search_input,
                search_button,
                job_results,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # Advice Page Content
    advice_input = ft.TextField(label="Ask for career advice",width=800,text_align="center", border_color="white")
    advice_output = ft.Text("", selectable=True, max_lines=None, color=ft.Colors.YELLOW)

    def get_advice_click(e):
        question = advice_input.value
        if question:
            advice_output.value = "Thinking..."
            advice_output.update()
            advice_output.value = get_advice(question)
            advice_output.update()

    advice_button = ft.ElevatedButton("Get Advice", on_click=get_advice_click)

    def advice_view():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Career Advice",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.YELLOW,
                    ),
                    advice_input,
                    advice_button,
                    advice_output,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
        )

    # Navigation to update content area
    def navigate_to(selected_index):
        if selected_index == 0:
            content_area.content = home_view()
        elif selected_index == 1:
            content_area.content = job_view()
        elif selected_index == 2:
            content_area.content = advice_view()
        content_area.update()

    # Main container with background and content
    main_container = ft.Stack(
        [
            background_image,
            ft.Column(
                [
                    navigation_bar,
                    content_area,
                ],
                expand=True,
            ),
        ]
    )

    # Add the main container to the page
    page.add(main_container)
    navigate_to(0)


ft.app(target=main)
