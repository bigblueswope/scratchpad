import os

def notify(text, title):
    os.system("""
            osascript -e 'display notification "{}" with title "{}"
            '""".format(text, title))

def alert(text, title):
    os.system("""
                osascript -e 'display alert "{}" message"{}"
                '""".format(title, text))

notify("Thisi is the body text", "This is the Title")
#alert("Thisi is the body text", "This is the Title")

