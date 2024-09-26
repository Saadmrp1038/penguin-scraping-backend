import subprocess
import os
import uuid

def run_scrapy_spider(url):
    scraper_project_dir = os.path.join(os.getcwd(), 'app/scraper')
    output_file = os.path.join(scraper_project_dir, f'output_{uuid.uuid4().hex}.json')

    command = [
        'scrapy', 'crawl', 'simple', '-a', f'url={url}', '-o', output_file, '--nolog'
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=scraper_project_dir)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        error_message = stderr.decode('utf-8')
        raise Exception(f"Scrapy spider failed: {error_message}")

    return output_file
