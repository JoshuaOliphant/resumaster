import anthropic
from logfire import span
import pathlib

class AnthropicService:
    def __init__(self):
        self.client = anthropic.Anthropic()
        prompt_path = pathlib.Path(__file__).parent.parent / "prompt.md"
        with open(prompt_path, "r") as f:
            self.prompt_template = f.read()

    def customize_resume(self, resume_content: str, job_description: str, github_info: str = "", personal_writeup: str = "") -> str:
        """Customize a resume based on a job description and optional additional information"""
        with span("customize_resume"):
            # Fill in the prompt template
            prompt = self.prompt_template.replace("{{EXISTING_RESUME}}", resume_content)
            prompt = prompt.replace("{{JOB_DESCRIPTION}}", job_description)
            prompt = prompt.replace("{{GITHUB_INFO}}", github_info or "Not provided")
            prompt = prompt.replace("{{PERSONAL_WRITEUP}}", personal_writeup or "Not provided")

            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract just the tailored resume part
            content = response.content[0].text  # Get the text from the first content block
            start_tag = "<tailored_resume>"
            end_tag = "</tailored_resume>"
            
            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag)
            
            if start_idx != -1 and end_idx != -1:
                return content[start_idx + len(start_tag):end_idx].strip()
            else:
                # If tags not found, return the whole response
                return content

anthropic_service = AnthropicService()
