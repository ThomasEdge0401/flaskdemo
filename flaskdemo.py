from flask import Flask, render_template, request, redirect, url_for, session
import wikipedia
from wikipedia.exceptions import (
    PageError,
    DisambiguationError,
    RedirectError,
    HTTPTimeoutError,
    WikipediaException,
)


def main():
    app.run(debug=True)


app = Flask(__name__)
# demo only; in real apps, load from environment
app.secret_key = "dev-only-secret-change-me"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        if "search" in request.form:
            term = request.form["search"].strip()
        else:
            term = ""
        session["search_term"] = term
        return redirect(url_for("results"))
    return render_template("search.html")


@app.route("/results")
def results():
    if "search_term" in session:
        term = session["search_term"].strip()
    else:
        term = ""
    if term == "":
        return redirect(url_for("search"))

    page, error_text, options = safe_get_page(term)
    return render_template(
        "results.html",
        page=page,
        term=term,
        error_text=error_text,
        options=options,
    )


def safe_get_page(search_term):
    """
    Resolve a Wikipedia page for search_term.
    Returns (page, error_text, options):
      - page: a wikipedia page object or None
      - error_text: message string ('' if none)
      - options: list of titles when disambiguation occurs
    """
    try:
        wikipedia.set_lang("en")
        page = wikipedia.page(search_term, auto_suggest=False, redirect=True)
        return page, "", []
    except DisambiguationError as e:
        return None, "We need a more specific title. Try one of the following, or a new search:", e.options
    except PageError:
        return None, f'Page id "{search_term}" does not match any pages. Try another id!', []
    except RedirectError as e:
        return None, f"Redirect issue: {e}. Try a more specific title.", []
    except HTTPTimeoutError:
        return None, "Wikipedia timed out. Please try again.", []
    except WikipediaException as e:
        return None, f"Wikipedia error: {e}", []
    except Exception as e:
        # final guard so nothing crashes the route
        return None, f"Unexpected error: {e}", []


if __name__ == "__main__":
    main()
