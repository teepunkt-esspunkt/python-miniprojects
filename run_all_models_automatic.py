# run_all_models_automatic.py
# Saves ALL outputs for this run into:

import os, time, re, json, pathlib, requests

# --- adjust these ---
A1111 = "http://127.0.0.1:7860"
WEBUI_ROOT = r"C:\username\stable-diffusion-webui"

PROMPT = "prompt"
NEG    = "blurry, lowres, deformed, extra limbs, watermark, text"
SEED   = -1      # set -1 for random
STEPS  = 30
CFG    = 7
W, H   = 700, 900
BATCH  = 1

# --------------------

def sanitize(s): return re.sub(r"[^a-zA-Z0-9._-]+", "_", s)

def api_get(path):
    r = requests.get(f"{A1111}{path}", timeout=60); r.raise_for_status(); return r.json()

def api_post(path, payload, timeout=1800):
    r = requests.post(f"{A1111}{path}", json=payload, timeout=timeout); r.raise_for_status(); return r.json()

def list_models():
    return [m["title"] for m in api_get("/sdapi/v1/sd-models")]

def set_model(title): api_post("/sdapi/v1/options", {"sd_model_checkpoint": title}, timeout=120)

def wait_selected(title, timeout=90):
    t0 = time.time()
    while time.time() - t0 < timeout:
        cur = api_get("/sdapi/v1/options").get("sd_model_checkpoint","")
        if cur == title: return True
        time.sleep(2)
    return False

def txt2img(base_outdir, date_str, time_str, filename_prefix, width, height):
    payload = {
        "prompt": PROMPT,
        "negative_prompt": NEG,
        "seed": SEED,
        "steps": STEPS,
        "cfg_scale": CFG,
        "width": width,
        "height": height,
        "batch_size": BATCH,
        "save_images": True,
        "override_settings": {
            # point to the *base* txt2img folder
            "outdir_txt2img_samples": base_outdir.replace("\\","/"),
            "outdir_txt2img_grids":   base_outdir.replace("\\","/"),

            # tell A1111 to actually create subfolders here
            "save_to_dirs": True,

            # lock the subfolder pattern to your run folder
            "directories_filename_pattern": f"{date_str}\\{time_str}",

            "samples_save": True,
            "samples_filename_pattern": f"{filename_prefix}-[seed]"
        },
        "override_settings_restore_afterwards": True
    }
    api_post("/sdapi/v1/txt2img", payload)


def write_text(path, text):
    pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(text)

def main():
    # Build run folder once
    date_str = time.strftime("%Y-%m-%d")
    time_str = time.strftime("%H-%M-%S")

    base_out = os.path.join(WEBUI_ROOT, "outputs", "txt2img-images")
    run_dir  = os.path.join(base_out, date_str, time_str)
    pathlib.Path(run_dir).mkdir(parents=True, exist_ok=True)
    print("Run folder:", run_dir)

    # Write settings.txt once
    models = list_models()
    if not models:
        print("No models found."); return
    settings_txt = os.path.join(run_dir, "settings.txt")
    write_text(
        settings_txt,
        "Prompt:\n" + PROMPT +
        "\n\nNegative Prompt:\n" + NEG +
        "\n\nParameters:\n" + json.dumps({
            "seed": SEED, "steps": STEPS, "cfg": CFG,
            "width": W, "height": H, "batch_size": BATCH
        }, indent=2) +
        "\n\nModels:\n" + "\n".join(models)
    )
    print("settings.txt →", settings_txt)

    # Loop models
    for i, title in enumerate(models, 1):
        print(f"[{i}/{len(models)}] {title}")
        try: set_model(title)
        except Exception as e:
            print("Failed to set model:", e); continue

        if not wait_selected(title):
            print("Model didn’t confirm; waiting 8s…"); time.sleep(8)

        prefix = sanitize(title.split(".safetensors")[0])

        tried_small = False
        while True:
            try:
                txt2img(base_out, date_str, time_str, prefix,
                    W if not tried_small else 512,
                    H if not tried_small else 512)
                break
            except requests.HTTPError:
                if not tried_small:
                    print("HTTP error; retrying 512x512…")
                    tried_small = True; time.sleep(5); continue
                print("Skipping after retry."); break
            except Exception as e:
                print("Error:", e); break

    print("\nDone. All images + settings.txt are in:", run_dir)

if __name__ == "__main__":
    main()
