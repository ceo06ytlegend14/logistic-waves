with open('builtin-clone/static/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the color definitions in .hero-shell
old_block = """  border-radius: 0;
  background: var(--navy);
  box-shadow: 0 10px 40px rgba(3, 79, 154, .30);
  color: var(--white);
  font-family: Inter, Arial, sans-serif;
}

.hero-photo {
  position: absolute;
  z-index: -2;
  inset: 0 0 0 36%;
  background:
    linear-gradient(90deg, rgba(3,79,154,.96) 0%, rgba(3,79,154,.42) 28%, rgba(3,79,154,.06) 65%),
    linear-gradient(0deg, rgba(2,45,92,.55), transparent 45%),
    url("/static/images/hero_multimodal_bg_2x.jpg") center right / cover no-repeat;
}

.hero-shell::before {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(112deg, #022e5e 0%, #034f9a 49%, transparent 49.1%);
  clip-path: polygon(0 0, 68% 0, 44% 100%, 0 100%);
}"""

new_block = """  border-radius: 0;
  background: linear-gradient(135deg, #034f9a 0%, #065eb8 100%);
  box-shadow: 0 10px 40px rgba(3, 79, 154, .30);
  color: var(--white);
  font-family: Inter, Arial, sans-serif;
}

.hero-photo {
  position: absolute;
  z-index: -2;
  inset: 0 0 0 36%;
  background:
    linear-gradient(90deg, #034f9a 0%, rgba(3,79,154,.85) 15%, rgba(3,79,154,.38) 32%, rgba(3,79,154,.02) 65%),
    linear-gradient(0deg, rgba(3,79,154,.65), transparent 45%),
    url("/static/images/hero_multimodal_bg_2x.jpg") center right / cover no-repeat;
}

.hero-shell::before {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(112deg, #023d77 0%, #034f9a 49%, transparent 49.1%);
  clip-path: polygon(0 0, 68% 0, 44% 100%, 0 100%);
}"""

if old_block in css:
    css = css.replace(old_block, new_block)
    with open('builtin-clone/static/styles.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("styles.css updated with vibrant #034f9a background!")
else:
    print("Could not match exact block, let's verify.")
