import keyboard
import pyautogui
import pytesseract
import pandas as pd
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def load_vocab(csv_file):
    df = pd.read_csv(csv_file)
    return list(zip(df["Word"], df["Definition"]))

vocab_dict = load_vocab("data.csv")

def clean_text(text):
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    return text.strip()

def log_message(message, output_file):
    print(message)
    output_file.write(message + "\n")

def click_button(coord, label):
    x1, y1 = coord["top_left"]
    x2, y2 = coord["bottom_right"]
    
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)
    
    print(f"Clicking at: {label} ({center_x}, {center_y})")
    pyautogui.click(center_x, center_y)
    time.sleep(0.5)

def extract_quizlet_flashcards(vocab_dict):
    coords = {
        "r1c1": {"top_left": (200, 160), "bottom_right": (575, 400)},
        "r1c2": {"top_left": (595, 160), "bottom_right": (945, 400)},
        "r1c3": {"top_left": (985, 160), "bottom_right": (1355, 400)},
        "r1c4": {"top_left": (1345, 160), "bottom_right": (1690, 400)},
        "r2c1": {"top_left": (200, 430), "bottom_right": (575, 700)},
        "r2c2": {"top_left": (595, 430), "bottom_right": (945, 700)},
        "r2c3": {"top_left": (985, 430), "bottom_right": (1355, 700)},
        "r2c4": {"top_left": (1345, 430), "bottom_right": (1690, 700)},
        "r3c1": {"top_left": (200, 710), "bottom_right": (575, 980)},
        "r3c2": {"top_left": (595, 710), "bottom_right": (945, 980)},
        "r3c3": {"top_left": (985, 710), "bottom_right": (1355, 980)},
        "r3c4": {"top_left": (1345, 710), "bottom_right": (1690, 980)},
    }

    extracted_texts = []
    for label, coord in coords.items():
        x1, y1 = coord["top_left"]
        x2, y2 = coord["bottom_right"]

        width = x2 - x1
        height = y2 - y1

        screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
        extracted_text = pytesseract.image_to_string(screenshot).strip()
        extracted_texts.append([label, clean_text(extracted_text), coord])

    print("Extracted Texts:")
    for label, text, coord in extracted_texts:
        print(f"{label}: \"{text}\"")

    with open("output.txt", "a") as output_file:
        matched_pairs = set()
        for label, text, coord in extracted_texts:
            found_match = False
            short_text = text[:67]

            for word, definition in vocab_dict:
                if short_text == word[:len(short_text)]:
                    match_message = f"{label} Found match: {short_text} -> {definition} (Word Match)"
                    if (word, definition) not in matched_pairs:
                        log_message(match_message, output_file)
                        matched_pairs.add((word, definition))
                        click_button(coord, label)
                        for def_label, def_text, def_coord in extracted_texts:
                            if def_text == definition:
                                click_button(def_coord, def_label)
                    found_match = True
                    break
                elif short_text == definition[:len(short_text)]:
                    match_message = f"{label} Found match: {short_text} -> {word} (Definition Match)"
                    if (word, definition) not in matched_pairs:
                        log_message(match_message, output_file)
                        matched_pairs.add((word, definition))
                        click_button(coord, label)
                        for word_label, word_text, word_coord in extracted_texts:
                            if word_text == word:
                                click_button(word_coord, word_label)
                    found_match = True
                    break

            if not found_match:
                log_message(f"No match found for: {short_text}", output_file)

keyboard.add_hotkey("ctrl+alt+t", lambda: extract_quizlet_flashcards(vocab_dict))
keyboard.wait()
