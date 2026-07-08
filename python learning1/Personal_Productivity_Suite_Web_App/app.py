from flask import Flask, render_template, request, redirect, send_file
from reportlab.pdfgen import canvas
import json
import os
import shutil
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data/notes.json"


def load_notes():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)



def save_notes(notes):

    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4)



@app.route("/")
def home():

    notes = load_notes()

    return render_template(
        "index.html",
        notes=notes
    )



@app.route("/add", methods=["POST"])
def add_note():

    notes = load_notes()

    note = {

        "id": len(notes) + 1,

        "title": request.form["title"],

        "content": request.form["content"],

        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    }


    notes.append(note)

    save_notes(notes)


    return redirect("/")



@app.route("/calculator", methods=["GET", "POST"])
def calculator():

    result = None

    if request.method == "POST":

        try:

            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operation = request.form["operation"]


            if operation == "add":

                result = num1 + num2


            elif operation == "subtract":

                result = num1 - num2


            elif operation == "multiply":

                result = num1 * num2


            elif operation == "divide":

                if num2 == 0:

                    result = "Cannot divide by zero"

                else:

                    result = num1 / num2


        except ValueError:

            result = "Enter valid numbers"



    return render_template(
        "calculator.html",
        result=result
    )

@app.route("/timer")
def timer():

    return render_template("timer.html")

@app.route("/unit_converter", methods=["GET", "POST"])
def unit_converter():

    result = None

    if request.method == "POST":

        try:

            value = float(request.form["value"])

            conversion = request.form["conversion"]


            if conversion == "km_miles":

                result = value * 0.621371


            elif conversion == "miles_km":

                result = value / 0.621371


            elif conversion == "c_f":

                result = (value * 9/5) + 32


            elif conversion == "f_c":

                result = (value - 32) * 5/9


        except ValueError:

            result = "Enter valid number"


    return render_template(
        "unit_converter.html",
        result=result
    )

@app.route("/file_organizer", methods=["GET", "POST"])
def file_organizer():

    message = None


    if request.method == "POST":

        source_folder = request.form["folder"]


        if not os.path.exists(source_folder):

            message = "Folder not found!"

            return render_template(
                "file_organizer.html",
                message=message
            )


        folders = {

            "Images": [".jpg", ".png", ".jpeg"],

            "Documents": [".pdf", ".txt", ".docx"],

            "Music": [".mp3"],

            "Videos": [".mp4", ".avi"]

        }


        for folder in folders:

            os.makedirs(
                os.path.join(source_folder, folder),
                exist_ok=True
            )


        os.makedirs(
            os.path.join(source_folder, "Others"),
            exist_ok=True
        )


        for file in os.listdir(source_folder):

            file_path = os.path.join(
                source_folder,
                file
            )


            if os.path.isdir(file_path):
                continue


            moved = False


            for folder, extensions in folders.items():

                if file.lower().endswith(tuple(extensions)):


                    shutil.move(
                        file_path,
                        os.path.join(
                            source_folder,
                            folder,
                            file
                        )
                    )


                    moved = True

                    break



            if not moved:

                shutil.move(

                    file_path,

                    os.path.join(
                        source_folder,
                        "Others",
                        file
                    )

                )


        message = "Files organized successfully!"



    return render_template(
        "file_organizer.html",
        message=message
    )

@app.route("/backup")
def backup():

    os.makedirs("data/backups", exist_ok=True)

    source = "data/notes.json"
    destination = "data/backups/notes_backup.json"

    if os.path.exists(source):
        shutil.copy(source, destination)
        return "Backup created successfully!"

    return "No notes found to backup."

@app.route("/restore")
def restore():

    source = "data/backups/notes_backup.json"
    destination = "data/notes.json"

    if os.path.exists(source):
        shutil.copy(source, destination)
        return redirect("/")

    return "No backup found."


@app.route("/search", methods=["GET"])
def search():

    keyword = request.args.get("keyword", "").lower()

    notes = load_notes()

    filtered = []

    for note in notes:

        if keyword in note["title"].lower() or keyword in note["content"].lower():

            filtered.append(note)

    return render_template(
        "index.html",
        notes=filtered
    )


@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):

    notes = load_notes()

    note = None

    for n in notes:
        if n["id"] == note_id:
            note = n
            break

    if note is None:
        return "Note not found!"

    if request.method == "POST":

        note["title"] = request.form["title"]
        note["content"] = request.form["content"]

        save_notes(notes)

        return redirect("/")

    return render_template(
        "edit_note.html",
        note=note
    )

@app.route("/delete/<int:note_id>")
def delete_note(note_id):

    notes = load_notes()

    notes = [note for note in notes if note["id"] != note_id]

    save_notes(notes)

    return redirect("/")

@app.route("/export_pdf")
def export_pdf():

    notes = load_notes()

    pdf_file = "notes.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 800, "Personal Productivity Suite")

    c.setFont("Helvetica", 12)

    y = 760

    for note in notes:

        c.drawString(50, y, f"Title: {note['title']}")
        y -= 20

        c.drawString(50, y, f"Content: {note['content']}")
        y -= 20

        c.drawString(50, y, f"Date: {note['date']}")
        y -= 35

    c.save()

    return send_file(pdf_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)


# Keep this at the very bottom

if __name__ == "__main__":

    app.run(debug=True)