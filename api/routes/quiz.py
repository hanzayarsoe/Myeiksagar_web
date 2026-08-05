"""Myeik culture quiz flow (session-based)."""

from flask import redirect, render_template, request, session, url_for

from quiz_data import QUESTIONS_PER_ROUND, pick_questions


def _normalize_answer(value):
    return (value or "").strip()


def register(app):
    @app.route("/quiz_start_page")
    def quiz_start_page():
        return render_template("quiz_start_page.html")

    @app.route("/quiz_start")
    def quiz_start():
        session.clear()
        session["level"] = "easy"
        session["score"] = 0
        session["question_number"] = 0
        session["completed_levels"] = 0
        session["questions"] = pick_questions(session["level"], QUESTIONS_PER_ROUND)
        session["total_questions"] = QUESTIONS_PER_ROUND
        return redirect(url_for("quiz"))

    @app.route("/quiz", methods=["GET", "POST"])
    def quiz():
        if "level" not in session:
            return redirect(url_for("quiz_start_page"))

        if request.method == "POST":
            user_answer = _normalize_answer(request.form.get("answer"))
            correct_answer = _normalize_answer(
                session["questions"][session["question_number"]]["answer"]
            )

            if user_answer == correct_answer:
                session["score"] += 1

            session["question_number"] += 1

            if session["question_number"] >= session["total_questions"]:
                if session["score"] == session["total_questions"]:
                    session["completed_levels"] += 1
                    if session["level"] == "hard":
                        return redirect(url_for("congratulations"))
                    return redirect(url_for("next_level"))
                return redirect(url_for("result"))

        if session["question_number"] < session["total_questions"]:
            question_data = session["questions"][session["question_number"]]
            return render_template(
                "quiz.html",
                question=question_data["question"],
                options=question_data["options"],
                level=session["level"],
                question_number=session["question_number"] + 1,
                total_questions=session["total_questions"],
            )
        return redirect(url_for("result"))

    @app.route("/next_level")
    def next_level():
        if "completed_levels" not in session or session["completed_levels"] < 1:
            return redirect(url_for("quiz_start_page"))
        upcoming = "medium" if session["level"] == "easy" else "hard"
        return render_template("next_level.html", next_level=upcoming)

    @app.route("/start_next_level")
    def start_next_level():
        if "completed_levels" not in session or session["completed_levels"] < 1:
            return redirect(url_for("quiz_start_page"))
        if session["level"] == "easy":
            session["level"] = "medium"
        elif session["level"] == "medium":
            session["level"] = "hard"

        session["score"] = 0
        session["question_number"] = 0
        session["questions"] = pick_questions(session["level"], QUESTIONS_PER_ROUND)
        session["total_questions"] = QUESTIONS_PER_ROUND
        return redirect(url_for("quiz"))

    @app.route("/congratulations")
    def congratulations():
        if "completed_levels" not in session or session["completed_levels"] < 3:
            return redirect(url_for("quiz_start_page"))
        session["completed_levels"] = 0
        return render_template("congratulations.html")

    @app.route("/result")
    def result():
        if "level" not in session:
            return redirect(url_for("quiz_start_page"))
        return render_template(
            "result.html",
            score=session["score"],
            level=session["level"],
        )
