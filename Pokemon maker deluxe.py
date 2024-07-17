# TODO: implement early saving, e.g. save to a .pkm file which can be read as a .json file

import json
import sys
from PIL import Image, ImageTk
from colorthief import ColorThief
from os import remove, chmod
from os.path import exists, splitext
from pygame import mixer
from tkinter import (Tk, Frame, Label, Toplevel, StringVar, Canvas, filedialog, BooleanVar, Text, Listbox, simpledialog,
                     filedialog)
from tkinter.ttk import Button, Entry, OptionMenu, Style, Scrollbar, Checkbutton
from urllib.parse import urlparse
from requests import get, ConnectionError
from requests.exceptions import ReadTimeout
from aiohttp import ClientSession
from asyncio import run
from AliasColours.colourFunctions import rgbtohex
from AliasHelpfulFunctions.generalFunctions import minimize_python, play_sound
from AliasTkFunctions.tkfunctions import update_bg, CreateToolTip, fix_resolution_issue, resize_window
from AliasVideoGameHelp.pokemonFunctions import get_stat

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
    if view_mode > 1:  # mode limit
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


def save_boken(*events):
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
        Button(frame, text=x_d["name"]).pack(side="left")

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
        "moves": []
    })


def save():
    file = filedialog.asksaveasfilename(defaultextension=".pkmn", filetypes=[(f"Saved Pokemon files", "*.pkmn")])

    if file:
        json.dump({
            "name": name_entry.get(),
            "stats": {i: globals()[i].get() for i in
                      "hp attack defence special-attack special-defence speed".split(" ")},
            "types": [type_1.get(), type_2.get()],
            "height": 0,
            "width": 0,
            "sprite": current_sprite,
            "shiny": current_sprite,
            "cry": "",
            "abilities": ["".join(i.split(". ")[1::]) for i in list(listboxes["ability_list"].get(0, "end"))],
            "moves": list(listboxes["move_list"].get(0, "end")),
            "entry": globals()["description"].get("1.0", "end")
        }, open(file, "w"))


def load():
    file = filedialog.askopenfilename(filetypes=[(f"Saved Pokemon files", "*.pkmn")])
    if file:
        load_pokemon(json.load(open(file, "r")))


def save_context():
    modal = Toplevel()
    resize_window(modal, 4, 4, False)
    modal.bind("<FocusOut>", lambda event: modal.destroy())
    modal.focus_force()

    Style().configure("secret_menu.TButton", font=("TkDefaultFont", 12))

    Button(modal, text="Save", command=save,
           style="secret_menu.TButton").pack(side="top", fill="both", expand=True, padx=10, pady=(10, 5))

    Button(modal, text="Load", command=load,
           style="secret_menu.TButton").pack(side="top", fill="both", expand=True, padx=10, pady=(5, 10))


if getattr(sys, "frozen", False) and splitext(sys.executable)[1] == ".exe":
    main.after_idle(reset)

bottom_frame = Frame(main)
bottom_frame.pack(side="bottom", pady=5)

Style().configure("small.TButton", width=8)
Button(bottom_frame, text="Reset", command=reset, style="small.TButton").pack(side="left", padx=(0, 5))
main.bind("<Control-r>", reset)

Style().configure("file.TButton", font=("TkTextFont", 9, "bold"), width=7)
Button(bottom_frame, text="File", command=save_context, style="file.TButton").pack(side="left", padx=(0, 5))
main.bind("<Control-s>", lambda event=None: save())
main.bind("<Control-l>", lambda event=None: load())
# main.after_idle(save)

main_frame = Frame(main, background="#f00")  # f00
main_frame.pack(side="top", fill="both", expand=True)

left_subframe = Frame(main_frame, bg="#0f0")  # 0f0
left_subframe.pack(side="left", fill="both", expand=True, padx=5, pady=5)
left_subframe.pack_propagate(False)

right_subframe = Frame(main_frame, bg="#00f")  # 00f
right_subframe.pack(side="right", fill="both", expand=True, padx=(0, 5), pady=5)
right_subframe.pack_propagate(False)

listboxes = {}


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

    for x in ["right_subframe", "left_subframe", "top_frame", "bottom_frame"]:
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

    scale = main.winfo_screenwidth() / 9.6
    width_scale = scale / width
    height_scale = scale / height

    scaling_factor = min(width_scale, height_scale)

    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)

    resized_image = image.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(resized_image)
    sprite.config(image=photo)
    sprite.image = photo


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
        types = ["Normal", "Fire", "Water", "Grass", "Electric", "Flying", "Ground", "Rock", "Fighting", "Ice",
                 "Poison", "Bug", "Ghost", "Psychic", "Dragon", "Dark", "Fairy", "Steel"]
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

        def add_item2(lstbox_name):
            lstbox = listboxes[lstbox_name]
            max_items = 3 if lstbox_name == "ability_list" else -1  # Set limits for each listbox
            if lstbox.size() == max_items:
                print(f"Limit Reached!!!    Cannot add more than {max_items} items.")
                return
            item = simpledialog.askstring("Input", "Enter item:")
            if item:
                if lstbox == listboxes["ability_list"]:
                    add_item(lstbox, f"{lstbox.size() + 1}. {item.title()}")
                else:
                    add_item(lstbox, item.title())

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
            Button(frame2, text="New", command=lambda j=i: add_item2(j)).pack(side="top", padx=(50, 20), pady=(10, 5))
            Button(frame2, text="Delete", command=lambda j=i: remove_item(j)).pack(side="top", padx=(50, 20),
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

        Label(left_subframe, text="Description", font=("TkTextFont", 12)).pack(side="top", pady=(5, 0))

        if "description" not in globals():
            globals()["description"] = Text(left_subframe, height=1, width=1, font=("TkTextFont", 10))
        globals()["description"].pack(side="top", padx=(20, 10), pady=5, fill="both", expand=True)

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

cache = {}


async def fill_mon2(*event):
    async def get_pokemon_data(pn, url="https://pokeapi.co/api/v2/pokemon/"):
        pn = f"{pn}{'-incarnate' if pn.lower() in ['tornadus', 'thundurus', 'landorus', 'enamorus'] else ''}"
        cache_key = pn.lower().replace(' ', '-')

        if cache_key in cache:
            return cache[cache_key]

        url = f"{url}{cache_key}"

        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    cache[cache_key] = data
                    return data  # Return the entire JSON response as a dictionary
                else:
                    return None

    async def get_pokemon_species_data(species_url):
        if species_url in cache:
            return cache[species_url]

        async with ClientSession() as session:
            async with session.get(species_url) as response:
                if response.status == 200:
                    data = await response.json()
                    cache[species_url] = data
                    return data
                else:
                    return None

    def parse_gender_rate(gender_rate):
        if gender_rate == -1:
            return {"genderless": 100, "male": 0, "female": 0}
        elif gender_rate == 0:
            return {"genderless": 0, "male": 100, "female": 0}
        elif gender_rate == 1:
            return {"genderless": 0, "male": 87.5, "female": 12.5}
        elif gender_rate == 2:
            return {"genderless": 0, "male": 75, "female": 25}
        elif gender_rate == 4:
            return {"genderless": 0, "male": 50, "female": 50}
        elif gender_rate == 6:
            return {"genderless": 0, "male": 25, "female": 75}
        elif gender_rate == 7:
            return {"genderless": 0, "male": 12.5, "female": 87.5}
        elif gender_rate == 8:
            return {"genderless": 0, "male": 0, "female": 100}
        else:
            return {"genderless": 0, "male": 0, "female": 0}

    async def get_evolution_chain(sd):
        evolution_chain_url = sd["evolution_chain"]["url"]
        evolution_chain_data = await get_pokemon_data(evolution_chain_url, "")
        chain = evolution_chain_data['chain']
        evolutions = []

        def get_evolutions(c):
            evolutions.append(c['species']['name'])
            for evolution in c['evolves_to']:
                get_evolutions(evolution)

        get_evolutions(chain)
        return evolutions

    try:
        unprocessed_pokemon = await get_pokemon_data(name.get())

        if unprocessed_pokemon:

            species_data = await get_pokemon_species_data(unprocessed_pokemon["species"]["url"])

            english_descriptions = [
                entry["flavor_text"]
                for entry in species_data["flavor_text_entries"]
                if entry["language"]["name"] == "en"
            ]

            processed_pokemon = {
                "name": unprocessed_pokemon["name"],
                "species": unprocessed_pokemon["species"],

                "forms": unprocessed_pokemon["forms"],

                "stats": {i["stat"]["name"].replace("defense", "defence"): i["base_stat"] for i in
                          unprocessed_pokemon["stats"]},
                "types": [i["type"]["name"] for i in unprocessed_pokemon["types"]],

                "height": unprocessed_pokemon["height"] / 10,
                "weight": unprocessed_pokemon["weight"],

                "sprite": unprocessed_pokemon["sprites"]["front_default"],
                "shiny": unprocessed_pokemon["sprites"]["front_shiny"],
                "cry": unprocessed_pokemon.get("cries", {}).get("latest", ""),

                "abilities": {i["ability"]["name"]: i["slot"] for i in unprocessed_pokemon["abilities"]},

                "level_moves": sorted(
                    [
                        {
                            "level": move['version_group_details'][0]['level_learned_at'],
                            "name": move['move']['name']
                        }
                        for move in unprocessed_pokemon["moves"]
                        if move["version_group_details"][0]["move_learn_method"]["name"] == "level-up"
                    ],
                    key=lambda move: move["level"]
                ),

                "egg_moves": sorted(
                    [move['move']['name'] for move in unprocessed_pokemon["moves"] if
                     move["version_group_details"][0]["move_learn_method"]["name"] == "egg"]
                ),

                "tm_moves": sorted(
                    [move['move']['name'] for move in unprocessed_pokemon["moves"] if
                     move["version_group_details"][0]["move_learn_method"]["name"] == "machine"]
                ),

                "entry": english_descriptions[-2],

                "egg_group": [species_data["egg_groups"][species_data["egg_groups"].index(i)]["name"] for i in
                              species_data["egg_groups"]],

                "is_baby": species_data["is_baby"],
                "is_legendary": species_data["is_legendary"],
                "is_mythical": species_data["is_mythical"],

                "gender": parse_gender_rate(species_data.get("gender_rate", -1)),

                "evolution_chain": await get_evolution_chain(species_data),
            }

            if processed_pokemon["name"] != processed_pokemon["evolution_chain"][0]:
                temp_pokemon = await get_pokemon_data(processed_pokemon["evolution_chain"][0])
                processed_pokemon.update({
                    "egg_moves": sorted(
                        [move['move']['name'] for move in temp_pokemon["moves"] if
                         move["version_group_details"][0]["move_learn_method"]["name"] == "egg"]
                    ),
                })

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
            current_sprite = pokemon["sprite" if not shiny.get() else "shiny"]

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
    if "entry" in pokemon:
        globals()["description"].insert("1.0", pokemon["entry"])
    globals()["notes"].delete("1.0", "end")

    listboxes["ability_list"].delete(0, "end")
    [add_item(listboxes["ability_list"], f"{listboxes["ability_list"].size() + 1}. {i.replace("-", " ").title()}")
     for i in pokemon["abilities"]]

    def update_moves():
        listboxes["move_list"].delete(0, "end")

        if "level_moves" in pokemon:
            [add_item(listboxes["move_list"], f"{i["level"]}: {i["name"].replace("-", " ").title()}") for i in
             pokemon["level_moves"]]

        if "egg_moves" in pokemon:
            [add_item(listboxes["move_list"], f"Egg: {i.replace("-", " ").title()}") for i in pokemon["egg_moves"]]

        if "tm_moves" in pokemon:
            [add_item(listboxes["move_list"], f"TM: {i.replace("-", " ").title()}") for i in pokemon["tm_moves"]]

        if "moves" in pokemon:
            [add_item(listboxes["move_list"], f"{i.replace("-", " ").title()}") for i in pokemon["moves"]]

    main.after_idle(update_moves)


def fill_mon(event=None):
    if internet_connection():
        run(fill_mon2())


def add_item(listbox, text, **kwargs):
    if listbox == listboxes["move_list"]:
        acronyms = {
            "eforce": "Expanding Force",
            "fout": "Fake Out",
            "pshot": "Parting Shot",
            "twave": "Thunder Wave",
            "eq": "Earthquake",
            "sd": "Swords Dance",
            "dd": "Dragon Dance",
            "cc": "Close Combat",
            "rocks": "Stealth Rock",
        }
        for x in acronyms:
            if text.lower() == x:
                text = acronyms[x]
                break
    listbox.insert("end", text)
    listbox.itemconfig(listbox.size() - 1, **kwargs)


def internet_connection():
    try:
        get("https://pokeapi.co/api/v2", timeout=1)
        return True
    except (ConnectionError, ReadTimeout):
        return False


auto_fill = Button(bottom_frame, text="Auto Fill", command=fill_mon, style="small.TButton")
auto_fill.pack(side="left", padx=(0, 5))
CreateToolTip(auto_fill,
              "Type in a pokemon's name,\nthen press auto fill to\nfill in the pokemon's stats!\n(Tick for shiny)"
              "\nNote: May include moves and abilities\nthat Pokemon no longer gets.",
              x_change=0, background="#fff", font=("TkTextFont", 9))

Checkbutton(bottom_frame, variable=shiny).pack(side="left")

main.bind("<Control-f>", fill_mon)
main.mainloop()
