import json, sys
from tkinter import Tk, Frame, Label, Toplevel, StringVar, Canvas, filedialog, BooleanVar, Text, Listbox, simpledialog
from tkinter.ttk import Button, Entry, OptionMenu, Style, Scrollbar, Checkbutton
from AliasVideoGameHelp.pokemonFunctions import get_stat
from AliasTkFunctions.tkfunctions import update_bg, CreateToolTip, fix_resolution_issue
from requests import get
from colorthief import ColorThief
from os import remove, chmod
from AliasColours.colourFunctions import rgbtohex
from AliasHelpfulFunctions.generalFunctions import minimize_python, play_sound
from urllib.parse import urlparse
from os.path import exists, splitext
from pygame import mixer
from PIL import Image, ImageTk

saved_pokemon = {"1": {"name": "HAM"}}
json.dump(saved_pokemon, open("saved_pokemon.json", "w"))

minimize_python()
fix_resolution_issue()

main = Tk()
main.geometry(f"{round(main.winfo_screenwidth() / 2)}x{round(main.winfo_screenheight() / 2)}+"
              f"{(main.winfo_screenwidth() - round(main.winfo_screenwidth() / 2)) // 2}+"
              f"{(main.winfo_screenheight() - round(main.winfo_screenheight() / 2)) // 2}")
main.update()
main.after_idle(main.focus_force)

# main.title(f"{" " * round(main.winfo_screenwidth() / 17.6)}✨ Pokemon Maker Deluxe ✨")
main.title("Pokemon Maker Deluxe")

view_mode = 0


def char_length(chars):
    def format_name():
        old_name = name.get()
        name.set(old_name.title().replace(" ", "-"))
    if len(chars) <= 26:
        main.after_idle(format_name)
    return len(chars) <= 26


top_frame = Frame(main)
top_frame.pack(side="top", pady=10)


def switch_view(*event):
    global view_mode
    view_mode += 1
    if view_mode > 2:
        view_mode = 0
    update_view()


view_button = Button(main, text="Functional Stats",
                     command=switch_view)
view_button.place(x=main.winfo_width() - 130, y=10)
main.bind("<Control-Tab>", switch_view)

name = StringVar(value="")
name_entry = Entry(top_frame, width=20, font=("TkTextFont", 12), validate="key", textvariable=name,
                   validatecommand=(main.register(char_length), "%P"), justify="center")
name_entry.pack(side="left")
name_entry.focus_force()


def save(*events):
    modal = Toplevel(main)
    modal.grab_set()
    modal.geometry(f"{round(main.winfo_screenwidth() / 3)}x{round(main.winfo_screenheight() / 3)}+"
                   f"{(main.winfo_screenwidth() - round(main.winfo_screenwidth() / 3)) // 2}+"
                   f"{(main.winfo_screenheight() - round(main.winfo_screenheight() / 3)) // 2}")

    canvas_frame = Frame(modal)
    canvas_frame.pack(side="right", fill="y")
    canvas = Canvas(canvas_frame, width=250, highlightthickness=0)
    scrollbar = Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both")
    scrollbar.pack(side="right", fill="y")
    canvas.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    modal_frame = Frame(canvas)
    canvas.create_window((0, 0), window=modal_frame, anchor="nw")
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 if event.delta > 0 else 1, "units"))

    saves = json.load(open("saved_pokemon.json", "r"))
    for x in saves:
        x_d = saves[x]
        frame = Frame(modal_frame, background="#f00")
        frame.pack(side="top", fill="x", expand=True)
        Label(frame, text=x_d["name"]).pack(side="left")

    main.wait_window(modal)


def reset(*event):
    load_pokemon({
        "name": "",
        "stats": {"hp": 0, "attack": 0, "defence": 0, "special-attack": 0, "special-defence": 0, "speed": 0},
        "types": ["Normal"],
        "height": 0,
        "width": 0,
        "sprite": "",
        "shiny": "",
        "cry": "",
        "abilities": {},
        "moves": [],
    })


if getattr(sys, "frozen", False) and splitext(sys.executable)[1] == ".exe":
    main.after_idle(reset)

bottom_frame = Frame(main)
bottom_frame.pack(side="bottom")

Style().configure("small.TButton", width=8)
Button(bottom_frame, text="Reset", command=reset, style="small.TButton").pack(side="left", padx=(0, 5))
main.bind("<Control-r>", reset)

Style().configure("file.TButton", font=("TkTextFont", 9, "bold"), width=7)
Button(bottom_frame, text="File", command=save, style="file.TButton").pack(side="left", padx=(0, 5))
main.bind("<Control-s>", save)
# main.after_idle(save)

main_frame = Frame(main, background="#f00")  # f00
main_frame.pack(side="top", fill="both", expand=True)

left_subframe = Frame(main_frame, bg="#0f0")  # 0f0
left_subframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
left_subframe.pack_propagate(False)

right_subframe = Frame(main_frame, bg="#00f")  # 00f
right_subframe.pack(side="right", fill="both", expand=True, padx=(0, 5), pady=5)
right_subframe.pack_propagate(False)


def update_theme(colour):
    for h in ["main_frame", "left_subframe", "right_subframe"]:
        if True:
            globals()[h].configure(background=colour)

    for h in ["main", "top_frame", "bottom_frame"]:
        if True:
            globals()[h].configure(background=colour)

    Style().configure("TMenubutton", background=colour)
    Style().configure("TButton", background=colour)
    Style().configure("TCheckbutton", background=colour)

    for x in ["right_subframe", "left_subframe"]:
        update_bg(globals()[x])


# update_theme("SystemButtonFace")


def load_image(file):
    global current_sprite
    current_sprite = file

    if file == "":
        sprite.config(image="")
        sprite.image = None
        return

    image = Image.open(file)

    width, height = image.size

    # Calculate scaling factors for width and height
    width_scale = 100 / width
    height_scale = 100 / height

    # Choose the smaller scaling factor to ensure the image fits within a 300x300 space
    scaling_factor = min(width_scale, height_scale)

    # Calculate the new dimensions
    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    resized_image = image.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(resized_image)
    sprite.config(image=photo)
    sprite.image = photo


listboxes = {}


def update_view():
    global view_button, bst, type_1, type_2, sprite, current_sprite, listboxes
    view_button.configure(text="Functional" if view_mode == 0 else "Aesthetic" if view_mode == 1 else "Extra")

    [w.pack_forget() for w in left_subframe.winfo_children() + right_subframe.winfo_children()]

    if view_mode == 0:
        # stats
        Label(right_subframe, text="Stats", font=("TkTextFont", 13)).pack(side="top", pady=(10, 0))
        frame = Frame(right_subframe)
        frame.pack(side="top")
        Label(frame, width=10).pack(side="left", padx=5)
        for n in ["min-", "min", "max", "max+"]:
            label = Label(frame, text=n, width=3 if n != "max+" else 4)
            label.pack(side="left", padx=5)
            CreateToolTip(label, "0 IVs, 0 EVs, negative nature" if n == "min-" else
                                 "31 IVs, 0 EVs, neutral nature" if n == "min" else
                                 "31 IVs, 252 EVs, neutral nature" if n == "max" else
                                 "31 IVs, 252 EVs, positive nature", x_change=0,
                          background="#fff", font=("TkTextFont", 9))

        def number_check(chars, entry_name):
            if (all(char.isdigit() for char in chars) or chars == "") and len(chars) <= 3:
                globals()[entry_name].after_idle(update_counter, entry_name)
            return (all(char.isdigit() for char in chars) or chars == "") and len(chars) <= 3

        def update_counter(counter):
            base = int(globals()[counter].get()) if globals()[counter].get() else 0
            globals()[f"{counter}_MIN"].configure(text=get_stat(base, 0, 0, 100, False,
                                                                True if counter == "hp" else False))
            globals()[f"{counter}_min"].configure(text=get_stat(base, 31, 0, 100, None,
                                                                True if counter == "hp" else False))
            globals()[f"{counter}_max"].configure(text=get_stat(base, 31, 252, 100, None,
                                                                True if counter == "hp" else False))
            globals()[f"{counter}_MAX"].configure(text=get_stat(base, 31, 252, 100, True,
                                                                True if counter == "hp" else False))
            update_bst()

        def update_bst():
            try:
                b = 0
                for m in "hp attack defence special-attack special-defence speed".split(" "):
                    b += int(globals()[m].get()) if globals()[m].get() else 0
                bst.configure(text=b)
            except (NameError, KeyError):
                pass

        for i in "hp attack defence special-attack special-defence speed".split(" "):
            frame = Frame(right_subframe)
            frame.pack(side="top", pady=(5, 0))
            Label(frame, text=i.replace("hp", "HP").replace("special-attack", "Sp. Atk")
                               .replace("special-defence", "Sp. Def").replace("attack", "Attack")
                               .replace("defence", "Defence").replace("speed", "Speed"), width=6).pack(side="left")

            def on_entry_click(ent, event):
                globals()[ent].select_range(0, "end")

            if i not in globals():
                globals()[i] = Entry(frame, validate="key", justify="center", width=3)
                to_insert = "0"
            else:
                to_insert = globals()[i].get()
                globals()[i] = Entry(frame, validate="key", justify="center", width=3)
            globals()[i].config(
                validatecommand=(main.register(lambda chars, entry_name=i: number_check(chars, entry_name)), "%P", i))
            globals()[i].bind("<FocusIn>", lambda event, enter=i: on_entry_click(enter, event))
            globals()[i].pack(side="left", padx=5)

            for n in ["MIN", "min", "max", "MAX"]:
                globals()[f"{i}_{n}"] = Label(frame, text="NOT UPDATED", width=3)
                globals()[f"{i}_{n}"].pack(side="left", padx=5)

            globals()[i].insert("0", to_insert)

        frame = Frame(right_subframe)
        frame.pack(side="top", pady=(5, 0))
        Label(frame, text="BST", width=6, bg="#f00").pack(side="left", padx=(15, 0))
        bst = Label(frame, text="NOT UPDATED", width=3, bg="#0f0")
        bst.pack(side="left", padx=(7, 0))
        Label(frame, width=20).pack(side="left")
        update_bst()

        # type
        types = ["Normal", "Fire", "Water", "Grass", "Electric", "Flying", "Ground", "Rock", "Fighting", "Ice", "Poison", "Bug",
                 "Ghost", "Psychic", "Dragon", "Dark", "Fairy", "Steel"]
        if "type_1" not in globals():
            type_1 = StringVar(value=types[0])
            type_2 = StringVar(value="None")

            def check_type_2(*event):
                if type_2.get() == type_1.get():
                    main.after_idle(lambda: type_2.set("None"))

            type_1.trace("w", check_type_2)
            type_2.trace("w", check_type_2)

        frame = Frame(left_subframe)
        frame.pack(side="top", pady=(10, 10))

        Label(frame, text="Type:").pack(side="left", padx=(0, 5))
        OptionMenu(frame, type_1, type_1.get(), *types).pack(side="left")

        Label(frame, text="/").pack(side="left")
        OptionMenu(frame, type_2, type_2.get(), *types).pack(side="left")

        def add_item(lstbox_name):
            lstbox = listboxes[lstbox_name]
            max_items = 3 if lstbox_name == "ability_list" else 5  # Set limits for each listbox
            if lstbox.size() >= max_items:
                print(f"Limit Reached!!!    Cannot add more than {max_items} items.")
                return
            item = simpledialog.askstring("Input", "Enter item:")
            if item:
                lstbox.insert("end", f"{lstbox.size() + 1}. {item.title()}")

        def remove_item(lstbox_name):
            lstbox = listboxes[lstbox_name]
            selected_items = lstbox.curselection()
            for index in selected_items[::-1]:
                lstbox.delete(index)

        # Create frames and listboxes
        for i in ["ability_list", "move_list"]:

            if f"{i}_frame" not in listboxes:
                listboxes[f"{i}_frame"] = Frame(left_subframe)
            listboxes[f"{i}_frame"].pack(side="top", fill="both", expand=True)
            listboxes[f"{i}_frame"].pack_propagate(False)

            frame2 = Frame(listboxes[f"{i}_frame"])
            frame2.pack(side="left")
            Label(frame2, text=f"{i.split('_')[0].capitalize()}s".replace("ys", "ies")).pack(side="top",
                                                                                                padx=(50, 20),
                                                                                                pady=(10, 5))
            Button(frame2, text="New", command=lambda i=i: add_item(i)).pack(side="top", padx=(50, 20), pady=(10, 5))
            Button(frame2, text="Delete", command=lambda i=i: remove_item(i)).pack(side="top", padx=(50, 20),
                                                                                      pady=(10, 5))

            if i not in listboxes:
                listboxes[i] = Listbox(listboxes[f"{i}_frame"])
            listboxes[i].pack(side="left", fill="both", expand=True, pady=10, padx=(0, 50))

    elif view_mode == 1:
        Label(left_subframe, text="Sprite", font=("TkTextFont", 13)).pack(side="top", pady=(10, 0))
        if "sprite" not in globals():
            sprite = Label(left_subframe, text="NOT UPDATED")
            current_sprite = ""
        sprite.pack(side="top")

        def choose_sprite():
            global current_sprite
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp")])
            if file_path:
                update_theme(rgbtohex(ColorThief(file_path).get_color(quality=1)))

                load_image(file_path)
        Button(left_subframe, text="Choose sprite", command=choose_sprite).pack(side="top")

    elif view_mode == 2:
        # other
        Label(left_subframe, text="Description", font=("TkTextFont", 12)).pack(side="top", pady=(5, 0))

        if "description" not in globals():
            globals()["description"] = Text(left_subframe, height=1, width=1, font=("TkTextFont", 10))
        globals()["description"].pack(side="top", padx=(20, 10), pady=5, fill="both", expand=True)

        Label(left_subframe).pack(side="top", fill="both", expand=True)

        #

        Label(right_subframe, text="Notes", font=("TkTextFont", 12)).pack(side="top", pady=(5, 0))

        if "notes" not in globals():
            globals()["notes"] = Text(right_subframe, height=1, width=1, font=("TkTextFont", 10))
        globals()["notes"].pack(side="top", padx=(10, 20), pady=5, fill="both", expand=True)

        Label(right_subframe).pack(side="top", fill="both", expand=True)

    for x in ["right_subframe", "left_subframe"]:
        update_bg(globals()[x])


for x in range(3):
    view_mode += 1
    if view_mode > 2:
        view_mode = 0
    update_view()


def fill_mon(*event):
    try:
        def get_pokemon_data(pn):
            pn = f"{pn}{"-Incarnate" if pn in ["Tornadus", "Thundurus", "Landorus", "Enamorus"] else ""}"
            url = f"https://pokeapi.co/api/v2/pokemon/{pn.lower().replace(" ", "-")}"
            response = get(url)

            if response.status_code == 200:
                data = response.json()
                return data  # Return the entire JSON response as a dictionary
            else:
                return None

        pokemon_name = name.get()
        unprocessed_pokemon = get_pokemon_data(pokemon_name)

        if unprocessed_pokemon:

            processed_pokemon = {
                "name": unprocessed_pokemon["name"],

                "stats": {i["stat"]["name"].replace("defense", "defence"): i["base_stat"] for i in unprocessed_pokemon["stats"]},
                "types": [i["type"]["name"] for i in unprocessed_pokemon["types"]],

                "height": unprocessed_pokemon["height"],
                "weight": unprocessed_pokemon["weight"],

                "sprite": unprocessed_pokemon["sprites"]["front_default"],
                "shiny": unprocessed_pokemon["sprites"]["front_shiny"],
                "cry": unprocessed_pokemon["cries"]["latest"],

                "abilities": {i["ability"]["name"]: i["slot"] for i in unprocessed_pokemon["abilities"]},
                "moves": [i["move"]["name"] for i in unprocessed_pokemon["moves"]],

                "description": f"As of current, it takes too long to get the description of a Pokemon.\nIf you have a "
                               f"faster version of mine, please reach out to me.\n"
                               f"\"description\": next((entry[\"flavor_text\"] for entry in unprocessed_pokemon[\""
                               f"species_data\"][\"flavor_text_entries\"] if entry[\"language\"][\"name\"] == \"en\"), "
                               f"\"No description available\")",
            }
            print(processed_pokemon)
            load_pokemon(processed_pokemon)
    except KeyError:
        pass


shiny = BooleanVar(value=False)


def load_pokemon(pokemon):
    global shiny

    name.set(pokemon["name"].title().replace(" ", "-"))

    for stat in pokemon["stats"]:
        if stat in globals():
            globals()[stat].delete("0", "end")
            globals()[stat].insert("0", f"{pokemon["stats"][stat]}")

    type_1.set(pokemon["types"][0].capitalize())
    type_2.set(pokemon["types"][0].capitalize() if len(pokemon["types"]) == 1 else pokemon["types"][1].capitalize())

    def load_sprite():
        global current_sprite, shiny
        current_sprite = pokemon["sprite" if not shiny.get() else "shiny"]

        if urlparse(pokemon["sprite" if not shiny.get() else "shiny"]).scheme in ("http", "https"):
            file_name = f"sprite.{pokemon["sprite" if not shiny.get() else "shiny"].split(".")[-1]}"

            with open(file_name, "wb") as handler:
                handler.write(get(pokemon["sprite" if not shiny.get() else "shiny"]).content)
            update_theme(rgbtohex(ColorThief(file_name).get_color(quality=1)))

            load_image(file_name)

            chmod(file_name, 0o777)
            remove(file_name)
        elif exists(pokemon["sprite" if not shiny.get() else "shiny"]):
            update_theme(rgbtohex(ColorThief(pokemon["sprite" if not shiny.get() else "shiny"]).get_color(quality=1)))

            load_image(pokemon["sprite" if not shiny.get() else "shiny"])
        else:
            update_theme("SystemButtonFace")

            load_image("")

    def load_cry():
        global shiny
        if urlparse(pokemon["cry"]).scheme in ("http", "https"):
            file_name = f"cry.{pokemon["cry"].split(".")[-1]}"

            response = get(pokemon["cry"], stream=True)
            if response.status_code == 200:
                try:
                    open(file_name, "w").write("")
                    with open(file_name, "wb") as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                except PermissionError:
                    return
                mixer.init()
                mixer.music.load(file_name)
                mixer.music.play()

                def stop():
                    if mixer.music.get_busy():
                        main.after(100, stop)
                        return
                    mixer.quit()
                    chmod(file_name, 0o777)
                    remove(file_name)
                stop()
        elif exists(pokemon["cry"]):
            play_sound(pokemon["cry"])

    if ("sprite" in pokemon and not shiny.get()) or ("shiny" in pokemon and shiny.get()):
        main.after_idle(load_sprite)
    if "cry" in pokemon:
        main.after_idle(load_cry)

    globals()["description"].delete("1.0", "end")
    if "description" in pokemon:
        globals()["description"].insert("1.0", pokemon["description"])
    globals()["notes"].delete("1.0", "end")

    listboxes["ability_list"].delete(0, "end")
    [listboxes["ability_list"].insert("end", f"{listboxes["ability_list"].size() + 1}. {i.replace("-", " ").title()}") for i in pokemon["abilities"]]

    listboxes["move_list"].delete(0, "end")
    [listboxes["move_list"].insert("end", i.replace("-", " ").title()) for i in pokemon["moves"]]


auto_fill = Button(bottom_frame, text="Auto Fill", command=fill_mon, style="small.TButton")
auto_fill.pack(side="left", padx=(0, 5))
CreateToolTip(auto_fill,
              "Type in a pokemon's name,\nthen press auto fill to\nfill in the pokemon's stats!\n(Tick for shiny)",
              x_change=0, background="#fff", font=("TkTextFont", 9))

Checkbutton(bottom_frame, variable=shiny).pack(side="left")

main.bind("<Control-f>", fill_mon)
main.mainloop()
