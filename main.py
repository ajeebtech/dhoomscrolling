import moviepy
import ollama
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import random
import time
import flask
import requests
import json
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip
from webdriver_manager.chrome import ChromeDriverManager


#user auth using google on flask
##forms, get interests, a dropdown for the voices you want


class User():
    def __init__(self, name, interests, voice):
        self.name = name
        self.interests = interests
        self.voice = voice

def course_text(interests,voice):
    response = ollama.chat(
            model='llama3.2',
            messages=[{
                'role': 'user',
                'content': f'Give me a short, engaging explanation of a random basic topic from {interests}. Keep it concise—just enough for a 10-second voiceover. Make it informative yet entertaining, and match the tone and lingo of {voice}. Just give me text, no narrating'
            }]
        )
    course_text = response['message']['content'].strip()
    print(course_text)
    return course_text

# course_text(interests="History",voice="Peter Griffin")

def load_cookies_from_file(driver, file_path):
    with open(file_path, 'r') as file:
        for line in file:
            # Skip comments and empty lines
            if line.startswith('#') or not line.strip():
                continue
                
            try:
                fields = line.strip().split('\t')
                if len(fields) >= 7:
                    cookie = {
                        'domain': fields[0],
                        'path': fields[2],
                        'name': fields[5],
                        'value': fields[6],
                        'secure': fields[3] == 'TRUE',
                    }
                    
                    # Add expiry if it's a valid number
                    if fields[4].isdigit():
                        cookie['expiry'] = int(fields[4])
                    
                    # Add the cookie to the browser
                    try:
                        driver.add_cookie(cookie)
                        print(f"Added cookie: {cookie['name']}")
                    except Exception as e:
                        print(f"Failed to add cookie {cookie['name']}: {e}")
            except Exception as e:
                print(f"Error processing line: {line.strip()}")
                print(f"Error: {e}")


def tts(course_text, voice, url='https://app.play.ht/studio/file/2Tt3EoUOQxoOTs0C9VCy'):

    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # Prevents sandboxing issues
    chrome_options.add_argument("--disable-dev-shm-usage")  # Fixes memory errors
    chrome_options.add_argument("--remote-debugging-port=9222")  # Helps debugging
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_options.add_argument("--window-size=1920x1080")

    # Correct profile configuration
    chrome_options.add_argument("--user-data-dir=/Users/jatin/Library/Application Support/Google/Chrome")
    chrome_options.add_argument("--profile-directory=Default")

    # Automatic driver management
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    try:
        # Navigate to the URL
        print(f"Opening {url}...")
        driver.get(url)
        # Check if "User not found" exists
        user_not_found = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'User not found')]"))
        )
        cookie_file = "cookies.txt"  # Update this with actual path if needed
        load_cookies_from_file(driver, cookie_file)
        if user_not_found:
            print("User not found. Clicking the login button...")
            login_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Log in')]"))
            )
            login_button.click()
            google_signin_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Sign in with Google')]"))
        )
            google_signin_button.click()

            # Wait for Google auth page to load
            time.sleep(2)

            # Now you're on the Google authentication page
            # Enter email
            email_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.clear()
            email_input.send_keys("your_email@gmail.com")

            # Click Next
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/parent::button"))
            )
            next_button.click()

            # Wait for password field
            time.sleep(2)
            password_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_input.send_keys("your_password")

            # Click Next to complete sign-in
            password_next = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/parent::button"))
            )
            password_next.click()
        else:
            print("User not found message NOT detected, continuing normally.")
            user_not_found = None
        
        # login time
        wait = WebDriverWait(driver, 10)
        
        # Find and handle the span button
        button_xpath = "//span[contains(@class, 'kt-truncate')]"
        button_element = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        
        # Get the current text
        current_text = button_element.text
        print(f"Found button with text: '{current_text}'")
        target_text = voice
        
        # Check if the text already matches
        if current_text == target_text:
            print(f"Text already matches '{target_text}'. No change needed.")
        else:
            # Click the button to trigger whatever change mechanism is available
            print("Clicking the button...")
            button_element.click()
            
            # Find and click the Cloned button
            cloned_button_selectors = [
                # By ID
                "//button[@id='headlessui-tabs-tab-:r47:']",
                # By text
                "//button[contains(text(), 'Cloned')]",
                # By class and text combination
                "//button[contains(@class, 'kt-text-black') and contains(text(), 'Cloned')]",
                # By role and aria-selected
                "//button[@role='tab' and @aria-selected='true' and contains(text(), 'Cloned')]"
            ]
            
            cloned_button = None
            for selector in cloned_button_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    cloned_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    cloned_button.click()
                    break
                except Exception:
                    continue
            
            # Add new step: Find and click on Peter Griffin
            print(f"Looking for '{voice}' text...")
            peter_griffin_selectors = [
                f"//td[contains(text(), '{voice}')]",
                f"//*[contains(text(), '{voice}')]"
            ]
            
            for selector in peter_griffin_selectors:
                try:
                    print(f"Trying selector for {voice}: {selector}")
                    peter_griffin_element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    peter_griffin_element.click()
                    print(f"Successfully clicked on '{voice}'!")
                    time.sleep(1)  # Wait for any changes after clicking
                    break
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
        
        # Wait for the text element to be present
        print("Waiting for the text element to load...")
        
        # Find the span element using the provided XPath
        text_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@data-lexical-text='true']")))
        
        print("Element found. Clicking to focus...")
        # Click on the element to focus it
        text_element.click()
        
        # Now select all text and delete it
        print("Selecting all text and clearing...")
        # For Windows/Linux use Control+A
        text_element.send_keys(Keys.COMMAND, 'a')
        text_element.send_keys(Keys.DELETE)
        
        # Type new text if provided
        new_text = course_text
        if new_text:
            print(f"Typing new text: {new_text}")
            text_element.send_keys(new_text)
        else:
            print("Leaving text box empty")
        
        # NEW STEP: Find and click the X mark SVG icon
        print("Looking for X mark (close) icon...")
        x_mark_selectors = [
            # Based on the SVG data you provided
            "//svg[contains(@class, 'kt-cursor-pointer')][contains(@data-sentry-element, 'XMarkIcon')]",
            # By class combination that seems unique to the X button
            "//svg[contains(@class, 'kt-absolute kt-right-4 kt-top-4')]",
            # By path description (since SVG has a specific path for X mark)
            "//svg[.//path[contains(@d, 'M5.47 5.47a.75.75 0 0 1 1.06 0L12 10.94l5.47-5.47')]]",
            # By data attributes
            "//svg[@data-sentry-element='XMarkIcon']"
        ]
        
        for selector in x_mark_selectors:
            try:
                print(f"Trying selector for X mark icon: {selector}")
                x_mark_element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                x_mark_element.click()
                print("Successfully clicked on X mark icon!")
                time.sleep(1)  # Wait for any closing animations
                break
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue
        
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Speech')]")
        button.click()
        time.sleep(15)
        print("Operation completed successfully!")
        wav_url = None
        for _ in range(15):  # Wait for up to 15 seconds
            logs = driver.get_log("performance")
            for log in logs:
                try:
                    msg = json.loads(log["message"])["message"]
                    if msg["method"] == "Network.responseReceived":
                        url = msg["params"]["response"]["url"]
                        if url.endswith(".wav"):
                            wav_url = url
                            break
                except Exception:
                    continue
            if wav_url:
                break
            time.sleep(1)

        if wav_url:
            print(f"WAV File URL: {wav_url}")

            # Download the WAV file
            response = requests.get(wav_url)
            with open(f"{voice}.wav", "wb") as f:
                f.write(response.content)
            print("WAV file downloaded successfully!")
        else:
            print("WAV file not found.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    # finally:
    #     driver.quit()
    return f'{voice}.wav'

tts(course_text=course_text(interests="History", voice="Peter Griffin"),voice="Peter Griffin")

def clip(audio_file=tts(course_text=course_text(interests="History", voice="Peter Griffin"), voice="Peter Griffin"),voice = "Peter Griffin"):

    clips_dir = "minecraft/"
    video_files = [f for f in os.listdir(clips_dir) if f.endswith((".mp4", ".mov", ".avi"))]
    if not video_files:
        raise ValueError("No video files found in 'minecraft/' directory.")

    random_video = os.path.join(clips_dir, random.choice(video_files))
    print(f"Selected Video: {random_video}")

    # Step 2: Load the video and audio
    video = VideoFileClip(random_video)
    audio = AudioFileClip(f"{audio_file}")  # Change to your audio file

    video = video.loop(duration=audio.duration)

    # Step 4: Convert to Vertical Aspect Ratio (9:16)
    target_width = 1080  # Standard phone width
    target_height = 1920  # Standard phone height

    # Resize and crop to fill the screen
    video = video.resize(width=target_width)  # Resize while maintaining aspect ratio
    video = video.crop(y_center=video.h / 2, width=target_width, height=target_height)  # Center crop

    # Step 5: Overlay PNG (Matching Peter Griffin's Position)
    overlay = ImageClip(f"overlaycharacters/{voice}.png").set_duration(video.duration)  # Keep overlay duration same as video
    overlay = overlay.resize(height=250)  # Adjust overlay size

    # Custom Positioning (Center-bottom like Peter Griffin)
    overlay_x = (target_width - overlay.w) / 2  # Center horizontally
    overlay_y = target_height - 500  # Adjust height to match reference

    overlay = overlay.set_position((overlay_x, overlay_y))  # Apply new position

    # Step 6: Combine everything
    final_clip = CompositeVideoClip([video, overlay])
    final_clip = final_clip.set_audio(audio)  # Attach final audio

    # Step 6: Export the final video 
    final_clip.write_videofile(f"{voice}.mp4", codec="libx264", fps=video.fps)

    






    
