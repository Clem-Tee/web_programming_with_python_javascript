from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django import forms
from . import util
import markdown2
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    """
    View function to display a specific encyclopedia entry.
    """
    entries = util.list_entries()
    matching_entry = next((e for e in entries if e.lower() == title.lower()), None)

    if matching_entry:
        content = util.get_entry(matching_entry)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": markdown2.markdown(content)
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })

def search(request):
    """
    View function to handle search queries.
    """
    query = request.GET.get('q', '').strip().lower()
    entries = util.list_entries()

    # Check if query matches an existing entry exactly (case-insensitive)
    for entry in entries:
        if entry.lower() == query:
            return redirect("entry", title=entry)
        
    # If no exact match, filter entries containing the search term
    matching_entries = [entry for entry in entries if query in entry.lower()]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "entries": matching_entries
    })

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={"class": "form-control"}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={"class": "form-control"}))

def create(request):
    """
    View function to handle creating a new encyclopedia entry.
    """
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"].strip()
            content = form.cleaned_data["content"]

            # Check if the entry already exists (case-insensitive)
            entries = util.list_entries()
            if title.lower() in [entry.lower() for entry in entries]:
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "error": "An entry with this title already exists."
                })
            
            # Save the new entry
            util.save_entry(title, content)
            return redirect("entry", title=title)

    # If GET request, display a new form
    return render(request, "encyclopedia/create.html", {"form": NewPageForm()})

def edit_entry(request, title):
    if request.method == "POST":
        new_content = request.POST["content"]
        util.save_entry(title, new_content) # Save the updated content
        return redirect("entry", title=title)
    
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {"message": "Page not found."})
    
    return render(request, "encyclopedia/edit.html", {"title": title, "content": content})

def random_page(request):
    """
    Redirects the user to a random encyclopedia entry.
    """
    entries = util.list_entries() # Get list of all entries
    if entries: # Ensure there are entries available
        random_entry = random.choice(entries) # Pick a random entry
        return redirect("entry", title=random_entry) # Redirect to that entry
    
    # If no entries exist, show an error page
    return render(request, "encyclopedia/error.html", {
        "message": "No entries available."
    })
