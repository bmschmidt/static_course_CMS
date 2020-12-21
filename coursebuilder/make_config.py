from .settings import course_settings, dir

with open(f"templates/configuration.tex", "w") as fout:
    for k, v in course_settings.items():
        if isinstance(v, list):
            if k == "Email":
                v = v[0]
            else:
                continue
        if isinstance(v, bool):
            continue
        fout.write("\\newcommand{\\" + 
        k.replace("_","") + 
        "}{" + v + "}\n")


        
